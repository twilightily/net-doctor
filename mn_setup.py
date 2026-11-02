#!/usr/bin/env python3
import socket
import time
import statistics
import subprocess
import platform
import sys

from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info

# -----------------------------
# Diagnostic Tool Configuration & Core Functions
# -----------------------------
TARGET = "10.0.0.3"  # Default IP of h3 in Mininet
PORT = 5005          # Custom port safe for UDP diagnostic testing
PACKETS = 10
TIMEOUT = 3

#what we're doing is we're making h3 run a program and have it listening on port 5005
#we configure it so that it sends back 

def resolve_host(host):
    print(f"[+] Target Host -> {host}")
    return host

def measure_rtt(host, port, count):
    rtts = [] #rtts of each of the sent packets
    lost = 0
    print("\n--- UDP RTT / Packet Loss ---")
    
    for i in range(count):
        # SOCK_DGRAM specifies a UDP implementation layer
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #this creates a socket
        sock.settimeout(TIMEOUT)
        
        payload = f"PING {i + 1}".encode() #the data that we're gonna send over the socket
        start = time.perf_counter()
        try:
            sock.sendto(payload, (host, port))
            data, addr = sock.recvfrom(1024)
            end = time.perf_counter()
            
            rtt = (end - start) * 1000
            rtts.append(rtt)
            print(f"Packet {i + 1}: {rtt:.2f} ms")
        except (socket.timeout, socket.error):
            lost += 1
            print(f"Packet {i + 1}: TIMEOUT/LOST")
        finally:
            sock.close()
        time.sleep(0.2)
        
    if rtts:
        print(f"\nMinimum RTT : {min(rtts):.2f} ms")
        print(f"Maximum RTT : {max(rtts):.2f} ms")
        print(f"Average RTT : {statistics.mean(rtts):.2f} ms")
    packet_loss = (lost / count) * 100
    print(f"Packets sent : {count}")
    print(f"Packets lost : {lost}")
    print(f"Packet loss : {packet_loss:.2f}%")
    return rtts, packet_loss

def measure_udp_echo_delay(host, port):
    print("\n--- UDP Echo Connection Delay ---")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT)
    
    payload = b"INIT_ECHO"
    start = time.perf_counter()
    try:
        sock.sendto(payload, (host, port))
        data, addr = sock.recvfrom(1024)
        end = time.perf_counter()
        delay = (end - start) * 1000
        print(f"UDP structural delay baseline: {delay:.2f} ms")
        return delay
    except socket.error as e:
        print(f"UDP transit check failed: {e}")
        return None
    finally:
        sock.close()

def send_udp_application_data(host, port):
    print("\n--- UDP Application Data Transfer ---")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT)
    
    # Custom light application payload simulating data transaction
    request = b"APP_DATA_REQUEST_PAYLOAD"
    try:
        start = time.perf_counter()
        sock.sendto(request, (host, port))
        response, addr = sock.recvfrom(1024)
        end = time.perf_counter()
        elapsed = (end - start) * 1000
        print(f"Received {len(response)} bytes back from server")
        print(f"Application round trip: {elapsed:.2f} ms")
        return elapsed
    except socket.error as e:
        print(f"UDP application transfer error: {e}")
        return None
    finally:
        sock.close()

def discover_path(host):
    print("\n--- Network Path ---")
    system = platform.system()
    try:
        # Standard traceroute defaults to sending UDP packets on Linux environments
        if system == "Windows":
            command = ["tracert", "-d", host]
        else:
            command = ["traceroute", "-n", host]
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        print(result.stdout)
        return result.stdout
    except FileNotFoundError:
        print("Traceroute command is not installed.")
        return None
    except subprocess.TimeoutExpired:
        print("Traceroute timed out.")
        return None

# -----------------------------
# Main Test Framework Runner
# -----------------------------
def run_diagnostic_tool():
    print("\n==============================")
    print(" Running UDP Network Diagnostic Tool inside Mininet (h1 -> h3)")
    print("==============================")
    ip = resolve_host(TARGET)
    echo_delay = measure_udp_echo_delay(ip, PORT)
    rtts, packet_loss = measure_rtt(ip, PORT, PACKETS)
    application_delay = send_udp_application_data(ip, PORT)
    discover_path(ip)
    
    print("\n==============================")
    print(" Final Results")
    print("==============================")
    if echo_delay is not None:
        print(f"UDP initial delay   : {echo_delay:.2f} ms")
    if rtts:
        print(f"Average UDP RTT     : {statistics.mean(rtts):.2f} ms")
    print(f"Packet loss         : {packet_loss:.2f}%")
    if application_delay is not None:
        print(f"Application delay   : {application_delay:.2f} ms")

# -----------------------------
# Mininet Infrastructure Instantiation
# -----------------------------
def build_and_run_sdn():
    net = Mininet(topo=None, build=False, ipBase='10.0.0.0/8')

    info('*** Adding SDN Controller\n')
    c0 = net.addController(name='c0', controller=RemoteController, ip='127.0.0.1', port=6653)
	#c0 talks to the switches via OpenFlow 1.3 protocol
    info('*** Adding Switches\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch, protocols='OpenFlow13')
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch, protocols='OpenFlow13')
    s3 = net.addSwitch('s3', cls=OVSKernelSwitch, protocols='OpenFlow13')

    info('*** Adding End Hosts\n')
    h1 = net.addHost('h1', ip='10.0.0.1', defaultRoute=None)
    h2 = net.addHost('h2', ip='10.0.0.2', defaultRoute=None)
    h3 = net.addHost('h3', ip='10.0.0.3', defaultRoute=None)

    info('*** Fabricating Links\n')
    net.addLink(h1, s1)
    net.addLink(s1, s2)
    #net.addLink(s2, h2)
    net.addLink(s1, s3)
    net.addLink(s3, h3)

    info('*** Booting up the network\n')
    net.start()

    # Step 1: Spin up an active background UDP server daemon loop directly on host h3
    info('*** Starting Application Target UDP server on h3 (Port 5005)\n')

    udp_server_code = ( #this is the code that we're keeping running on h3, notice how it sends back the same data to the same address
        "import socket\n"
        "s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)\n"
        f"s.bind(('0.0.0.0', {PORT}))\n"
        "while True:\n"
        "    data, addr = s.recvfrom(1024)\n"
        "    s.sendto(data, addr)\n"
    )
    
    h3.cmd(f'python3 -c "{udp_server_code}" &') #we're getting it running on h3 using its cmd
    time.sleep(2)  

    # Step 2: Clear switch dependencies and populates Flow Tables 
    info('*** Performing initial network discovery ping\n')
    net.pingAll()

    # Step 3: Run the updated diagnostic script natively via host h1 reference loop
    info('*** Executing custom UDP network diagnostic measurements directly on host h1\n')
    info(h1.cmd('python3 mn_setup.py --run-tool')) #we're running diagnostics on h1

    # Step 4: Tear down environment cleanly
    info('\n*** Dropping into Interactive Mininet CLI. Type "exit" to close down.\n')
    CLI(net)

    info('*** Killing background UDP daemons and cleaning up\n')
    h3.cmd('pkill -f "socket.SOCK_DGRAM"')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    # If called internally by h1.cmd execution proxy, bypass topology constructor loops
    if len(sys.argv) > 1 and sys.argv[1] == '--run-tool': #you're defining saying if you run this with so and so flag run so and so function
        run_diagnostic_tool()
    else:
        build_and_run_sdn()
