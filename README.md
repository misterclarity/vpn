# Python VPN Client for VPNGate

## Description

This project is a Python-based command-line tool designed to simplify connecting to free VPN servers listed on [VPNGate.net](http://www.vpngate.net/). It allows users to select a country they wish to emulate their connection from, automatically fetches and selects an optimal server, and manages the OpenVPN client connection.

## Features

*   Fetches publicly available VPN server lists from VPNGate.net's API.
*   Allows users to choose a country to connect through.
*   Automatically selects an optimal server based on a combination of speed, ping, and score.
*   Manages OpenVPN client process connections using `.ovpn` configuration files.
*   Provides a simple command-line interface (CLI) for ease of use.

## Requirements

*   Python 3.6+
*   OpenVPN client: Must be installed on your system and accessible via the system's PATH.
    *   On Linux, this is typically the `openvpn` package.
    *   On macOS, you can install it via Homebrew (`brew install openvpn`).
    *   On Windows, you can install the official OpenVPN client.
*   `requests` Python library: Used for fetching data from the VPNGate API.
*   Administrative privileges: `sudo` (on Linux/macOS) or Administrator rights (on Windows) are generally required for OpenVPN to create network interfaces and modify routing tables.

## Setup

1.  **Install Python and OpenVPN:**
    *   Ensure Python 3 (version 3.6 or newer) is installed on your system.
    *   Install the OpenVPN client appropriate for your operating system. Make sure the `openvpn` command is available in your system's PATH.

2.  **Get the Project Files:**
    *   Place the `vpn_project` directory (which includes `vpn_client.py`, `openvpn_manager.py`, and `vpngate_scraper.py`) in your desired location. Or, clone this repository if it's hosted.

3.  **Install Required Python Library:**
    *   Open your terminal or command prompt and install the `requests` library:
        ```bash
        pip install requests
        ```
    *   If you are using a virtual environment (recommended), activate it before running pip.

## How to Run

1.  **Navigate to the Project Directory:**
    *   Open your terminal or command prompt.
    *   Change to the directory that *contains* the `vpn_project` folder. For example, if `vpn_project` is in `~/Projects/python_vpn`, you would navigate to `~/Projects/python_vpn`.

2.  **Run the VPN Client:**
    *   Execute the client script as a module:
        ```bash
        python -m vpn_project.vpn_client
        ```
    *   **Administrative Privileges:** OpenVPN usually requires administrative rights to manage network connections.
        *   On **Linux or macOS**, you will likely need to run the script with `sudo`:
            ```bash
            sudo python -m vpn_project.vpn_client
            ```
            You will be prompted for your sudo password when OpenVPN attempts to start.
        *   On **Windows**, you may need to run your command prompt as an Administrator.

3.  **Follow On-Screen Prompts:**
    *   The script will display a list of available countries.
    *   Enter the number corresponding to your desired country and press Enter.
    *   The script will then attempt to find the best server and connect.

4.  **Disconnecting:**
    *   Once connected (or if the connection attempt has started), the script will prompt you. To disconnect, type `d` or `disconnect` and press Enter.

## Important Notes

*   **Server Reliability:** This tool relies on public, volunteer-run VPN servers listed by VPNGate.net. The availability, speed, and quality of these servers can vary significantly and are not guaranteed.
*   **Connection Success:** A successful VPN connection depends on several factors, including your local OpenVPN installation being correctly configured, your network environment (firewalls, etc.), and the current status of the chosen VPNGate server.
*   **Internet Connection:** An active internet connection is required to fetch the server list from VPNGate.net.
*   **Security:** Be aware of the risks associated with using free, public VPN services. These servers are operated by volunteers, and their security practices may vary.
*   **Sudo Usage:** The `openvpn_manager.py` script uses `sudo openvpn ...` by default. This is a common requirement. If your OpenVPN setup does not require sudo, or if you manage permissions differently, you might need to adjust the command in `openvpn_manager.py`.

---

This README provides a basic guide. Depending on your OS and specific OpenVPN setup, some steps or commands might need minor adjustments.
