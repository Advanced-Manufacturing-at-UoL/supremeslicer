import socket
import ipaddress

def find_printer_ip(subnet_prefix, ports, timeout=1):
    """
    Scans the specified subnet for devices and returns a list of IPs that respond to a connection attempt on the specified ports.
    
    :param subnet_prefix: The subnet prefix to scan, provided by the user.
    :param ports: List of ports to attempt to connect to.
    :param timeout: The timeout in seconds for each connection attempt (default: 1).
    :return: List of IPs that responded to the connection attempt.
    """
    subnet = f"{subnet_prefix}.0.0/16"
    ip_network = ipaddress.ip_network(subnet, strict=False)
    live_ips = []

    for ip in ip_network.hosts():
        ip_str = str(ip)
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                result = sock.connect_ex((ip_str, port))
                if result == 0:
                    print(f"Device found at {ip_str} on port {port}")
                    live_ips.append(ip_str)
                sock.close()
            except Exception as e:
                print(f"Error scanning {ip_str} on port {port}: {e}")
                continue

    return live_ips

if __name__ == "__main__":
    subnet_prefix = input("Enter the IP prefix (e.g., 10.41): ").strip()
    ports_input = input("Enter the ports to check, separated by commas (e.g., 80, 22): ").strip()
    
    # Convert the input ports to a list of integers
    ports = [int(port) for port in ports_input.split(",")]

    printer_ips = find_printer_ip(subnet_prefix, ports)
    
    if printer_ips:
        print(f"Printer(s) found at: {', '.join(printer_ips)}")
    else:
        print("No printers found.")
