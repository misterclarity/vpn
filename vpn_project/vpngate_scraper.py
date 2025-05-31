import requests
import csv
import base64

class VPNGateScraper:
    def __init__(self, vpngate_url="http://www.vpngate.net/api/iphone/"):
        """
        Initializes the scraper with the VPNGate API URL.
        """
        self.vpngate_url = vpngate_url
        self.headers = { # Set a common User-Agent to avoid potential blocking
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def fetch_server_data(self):
        """
        Fetches raw CSV data from the VPNGate API.
        Returns the raw CSV content as a string, or None if fetching fails.
        """
        try:
            response = requests.get(self.vpngate_url, headers=self.headers, timeout=10)
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)

            # The content is expected to be text, but let's ensure it's decoded correctly.
            # VPNGate API usually sends UTF-8, but we can check encoding.
            # print(f"Detected encoding: {response.encoding}") # For debugging
            # response.encoding = 'utf-8' # Or set explicitly if known
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching server data: {e}")
            return None

    def parse_server_data(self, csv_data):
        """
        Parses the raw CSV data string into a list of server dictionaries.
        Decodes the Base64 OpenVPN configuration data.
        """
        if not csv_data:
            return []

        servers = []
        # Split lines and handle potential initial comment lines
        lines = csv_data.strip().split('\n')

        if len(lines) < 2:
            print("CSV data is too short or malformed.")
            return []

        # Find the header line (starts with #HostName)
        header_line_index = -1
        for i, line in enumerate(lines):
            if line.startswith("#HostName"):
                header_line_index = i
                break

        if header_line_index == -1:
            print("CSV header line starting with '#HostName' not found.")
            print("First 5 lines of received data:")
            for i in range(min(5, len(lines))):
                print(lines[i])
            return []

        # The header is the identified line, stripped of '#'
        header_str = lines[header_line_index].lstrip('#')
        header_fields = [h.strip() for h in header_str.split(',')]

        # Data lines start from the line immediately after the header line
        # and should not start with '*' or '#' (which are comments/meta)
        data_lines_for_csv = []
        for i in range(header_line_index + 1, len(lines)):
            line = lines[i]
            if line and not line.startswith('*') and not line.startswith('#'):
                data_lines_for_csv.append(line)

        if not data_lines_for_csv:
            print("No valid data lines found after the header for CSV processing.")
            return []

        # Use csv.reader and then create dicts, or use DictReader directly with the data lines
        # DictReader expects data lines to be passed to it, not the whole block including comments

        # We need to provide the fieldnames to DictReader if the first line of data_lines_for_csv is not the header
        reader = csv.DictReader(data_lines_for_csv, fieldnames=header_fields)

        for row_num, row in enumerate(reader):
            try:
                # Ensure all expected keys are present, or skip row
                if 'OpenVPN_ConfigData_Base64' not in row or not row['OpenVPN_ConfigData_Base64']:
                    # print(f"Skipping server (row {row_num + 1}): Missing OpenVPN_ConfigData_Base64 or it's empty.")
                    continue

                # Decode OpenVPN config
                decoded_config = base64.b64decode(row['OpenVPN_ConfigData_Base64']).decode('utf-8')
                row['ovpn_config'] = decoded_config
                servers.append(row)
            except base64.binascii.Error as e:
                print(f"Error decoding Base64 for server (row {row_num + 1}): {e}. Server: {row.get('HostName', 'N/A')}")
            except UnicodeDecodeError as e:
                print(f"Error decoding OVPN config to UTF-8 for server (row {row_num + 1}): {e}. Server: {row.get('HostName', 'N/A')}")
            except Exception as e:
                print(f"An unexpected error occurred parsing server (row {row_num + 1}): {e}. Server: {row.get('HostName', 'N/A')}")

        return servers

    def get_servers(self, filter_country_short=None):
        """
        Fetches, parses, and optionally filters server data by short country code.
        Returns a list of server dictionaries.
        """
        csv_data = self.fetch_server_data()
        if not csv_data:
            return []

        servers = self.parse_server_data(csv_data)

        if filter_country_short:
            filter_country_short = filter_country_short.lower()
            servers = [s for s in servers if s.get('CountryShort', '').lower() == filter_country_short]

        return servers

    def get_available_countries(self):
        """
        Gets all servers and returns a sorted list of unique (CountryLong, CountryShort) tuples.
        """
        servers = self.get_servers() # Get all servers without filtering first
        if not servers:
            return []

        countries = set()
        for server in servers:
            country_long = server.get('CountryLong')
            country_short = server.get('CountryShort')
            if country_long and country_short:
                countries.add((country_long, country_short))

        return sorted(list(countries), key=lambda x: x[0])


if __name__ == '__main__':
    scraper = VPNGateScraper()

    print("Fetching server data (this might take a moment)...")
    # Test fetching raw data (optional)
    # raw_data = scraper.fetch_server_data()
    # if raw_data:
    #     print(f"Fetched {len(raw_data)} bytes of data. First 200 chars: {raw_data[:200]}")
    # else:
    #     print("Failed to fetch raw data.")

    print("\n--- Available Countries ---")
    available_countries = scraper.get_available_countries()
    if available_countries:
        for cl, cs in available_countries:
            print(f"{cl} ({cs})")
    else:
        print("No countries found or error fetching data.")

    print("\n--- Servers from Japan (JP) ---")
    jp_servers = scraper.get_servers(filter_country_short="JP")
    if jp_servers:
        print(f"Found {len(jp_servers)} servers in Japan.")
        for i, server in enumerate(jp_servers[:3]): # Print details of first 3
            print(f"  Server {i+1} (JP):")
            print(f"    HostName: {server.get('HostName')}")
            print(f"    IP: {server.get('IP')}")
            print(f"    Score: {server.get('Score')}")
            print(f"    Speed: {server.get('Speed')}")
            # print(f"    OVPN Config (first 50 chars): {server.get('ovpn_config', '')[:50].replace(chr(10), ' ')}...") # Be careful printing config
            print(f"    OVPN Config Available: {'Yes' if server.get('ovpn_config') else 'No'}")
    else:
        print("No servers found for Japan (JP) or error fetching data.")

    print("\n--- Servers from United States (US) ---")
    us_servers = scraper.get_servers(filter_country_short="US")
    if us_servers:
        print(f"Found {len(us_servers)} servers in United States.")
        # (Optionally print details for a few US servers as above)
    else:
        print("No servers found for United States (US) or error fetching data.")

    print("\n--- All Servers (first 3) ---")
    all_servers = scraper.get_servers()
    if all_servers:
        print(f"Found {len(all_servers)} total servers.")
        for i, server in enumerate(all_servers[:3]): # Print details of first 3
            print(f"  Server {i+1} ({server.get('CountryShort')}):")
            print(f"    HostName: {server.get('HostName')}")
            print(f"    IP: {server.get('IP')}")
            print(f"    OVPN Config Available: {'Yes' if server.get('ovpn_config') else 'No'}")
    else:
        print("No servers found or error fetching data.")
