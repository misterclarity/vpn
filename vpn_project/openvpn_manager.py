import subprocess
import os
import signal

class OpenVPNManager:
    def __init__(self):
        self.process = None
        self.connected = False

    def connect(self, ovpn_file_path):
        """
        Connects to an OpenVPN server using the provided .ovpn configuration file.
        """
        if self.connected:
            print("Already connected. Please disconnect first.")
            return

        if not os.path.exists(ovpn_file_path):
            print(f"Error: OVPN configuration file not found at {ovpn_file_path}")
            return

        # Construct the command.
        # Note: Using sudo typically requires the script to be run with sudo privileges
        # or for sudo to be configured for passwordless execution of openvpn for the user.
        command = ["sudo", "openvpn", "--config", ovpn_file_path]

        try:
            print(f"Attempting to connect to OpenVPN using config: {ovpn_file_path}...")
            # Start the OpenVPN process
            self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)
            self.connected = True
            print(f"OpenVPN process started (PID: {self.process.pid}). Monitoring connection...")
            # Note: Actual connection establishment is asynchronous.
            # A more robust implementation would monitor self.process.stdout or self.process.stderr
            # for specific messages indicating successful connection or failure.
        except FileNotFoundError:
            print("Error: 'openvpn' command not found. Please ensure OpenVPN is installed and in your PATH.")
            self.connected = False
            self.process = None
        except Exception as e:
            print(f"An error occurred while trying to start OpenVPN: {e}")
            self.connected = False
            if self.process: # If process started but an error occurred later
                try:
                    os.killpg(os.getpgid(self.process.pid), signal.SIGTERM) # Send SIGTERM to the process group
                    self.process.wait(timeout=5)
                except ProcessLookupError:
                    pass # Process already dead
                except subprocess.TimeoutExpired:
                    os.killpg(os.getpgid(self.process.pid), signal.SIGKILL) # Force kill
                    self.process.wait(timeout=5)
                except Exception as kill_e:
                    print(f"Error trying to clean up process after failed start: {kill_e}")
            self.process = None


    def disconnect(self):
        """
        Disconnects from the OpenVPN server by terminating the OpenVPN process.
        """
        if not self.process or not self.connected:
            print("Not connected to any OpenVPN server or process not found.")
            return

        print(f"Attempting to disconnect from OpenVPN (PID: {self.process.pid})...")
        try:
            # Send SIGTERM to the entire process group created by OpenVPN
            # This is more reliable for stopping OpenVPN and its child processes.
            # sudo may be required here if the script user doesn't own the openvpn process
            # However, Popen with sudo in the command means the process is owned by root.
            # The 'sudo kill' approach is more robust if direct killpg fails due to permissions.
            # For now, we assume this script (or its user) has rights to kill the process it started,
            # or that OpenVPN handles the signal gracefully.

            # Try to terminate the process group first
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            self.process.wait(timeout=10) # Wait for graceful termination
            print("OpenVPN process group terminated (SIGTERM).")
        except subprocess.TimeoutExpired:
            print("OpenVPN process group did not terminate gracefully with SIGTERM. Forcing SIGKILL...")
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGKILL) # Force kill process group
                self.process.wait(timeout=5) # Wait for kill
                print("OpenVPN process group killed (SIGKILL).")
            except Exception as e_kill:
                print(f"Error during SIGKILL: {e_kill}. Manual cleanup might be needed.")
        except ProcessLookupError:
            print("Process already terminated.")
        except Exception as e:
            print(f"An error occurred while trying to disconnect: {e}")
            print(f"You might need to manually kill the OpenVPN process group (e.g., sudo kill -TERM -- -{self.process.pid}).")
        finally:
            self.process = None
            self.connected = False

if __name__ == '__main__':
    # Example Usage (for testing purposes, run this script directly)
    manager = OpenVPNManager()
    dummy_ovpn_file = "dummy.ovpn"

    # Create a dummy .ovpn file for the example
    # This is just to allow the connect method to run without file errors
    # A real connection requires a valid .ovpn file and OpenVPN setup
    if not os.path.exists(dummy_ovpn_file):
        with open(dummy_ovpn_file, "w") as f:
            f.write("client\n")
            f.write("dev tun\n") # Basic config line
            f.write("proto udp\n") # Basic config line
            # Add a non-existent remote to prevent it from actually trying to connect for too long
            f.write("remote non.existent.server._123 1194\n")


    # Test connect (will likely show 'process started' then fail or hang if OpenVPN tries to connect)
    # In a real scenario, OpenVPN output should be monitored for success.
    print("--- Test Connect ---")
    manager.connect(dummy_ovpn_file)

    if manager.connected and manager.process:
        print(f"OpenVPN process launched with PID: {manager.process.pid} (Process Group ID: {os.getpgid(manager.process.pid)})")
        print("Simulating some work...")
        try:
            # Let it run for a few seconds
            for i in range(5):
                print(f"Working... {i+1}/5")
                if manager.process.poll() is not None: # Check if process died
                    print("OpenVPN process died unexpectedly.")
                    manager.connected = False # Update status
                    break
                subprocess.run(["sleep", "1"]) # Use subprocess.run for sleep
            if manager.connected: # If still "connected" after sleep
                input("OpenVPN is 'running' (likely waiting for connection). Press Enter to disconnect...")
        except KeyboardInterrupt:
            print("Interrupted by user.")
        finally:
            print("--- Test Disconnect ---")
            manager.disconnect()
    else:
        print("Failed to start or keep OpenVPN process alive in example.")
        if manager.process: # If process exists but not marked connected or died
             manager.disconnect() # Try to clean up

    # Clean up dummy file
    if os.path.exists(dummy_ovpn_file):
        os.remove(dummy_ovpn_file)

    print("Example finished.")
