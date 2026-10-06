A mini project built as a team to enhance the understanding of how socket programming works and even every network related terms. Vibecoded with understanding...

# Network Diagnostic and Path Analysis Tool

A socket-based network diagnostic application that uses **UDP probes** to measure network performance and analyze packet paths. The application collects network metrics such as **round-trip time (RTT), packet loss, delay, and path characteristics**, and correlates these measurements with an **SDN network topology**.

## Features

* **UDP Diagnostic Probes**

  * Sends UDP packets to a target host.
  * Uses sequence numbers and timestamps to identify individual probes.

* **Round-Trip Time (RTT) Measurement**

  * Measures the time taken for a UDP probe to reach the destination and receive a response.
  * Calculates minimum, maximum, and average RTT.

* **Packet Loss Detection**

  * Tracks sent and received probes.
  * Identifies missing responses.
  * Calculates packet loss percentage.

* **Path Analysis**

  * Analyzes the network path between the source and destination.
  * Records path characteristics such as intermediate hops where available.

* **SDN Topology Discovery**

  * Retrieves the topology of the Software-Defined Network.
  * Represents switches, links, and connected hosts.

* **Measurement and Path Correlation**

  * Maps measured network paths to the corresponding SDN topology.
  * Helps identify how network topology affects measured performance.

* **Failed Path Detection**

  * Identifies paths that experience packet loss or become unreachable.
  * Helps determine potential connectivity problems.

* **Alternative Path Comparison**

  * Compares multiple available paths based on metrics such as:

    * RTT
    * Packet loss
    * Number of hops
    * Path availability

## Protocol

**UDP (User Datagram Protocol)**

UDP is used for diagnostic probes because it is connectionless and has low protocol overhead, making it suitable for measuring network behavior without establishing a TCP connection.

## Measurements

The application collects the following metrics:

| Metric            | Description                                                  |
| ----------------- | ------------------------------------------------------------ |
| RTT               | Time taken for a probe to travel to the destination and back |
| Delay             | Network delay observed during communication                  |
| Packet Loss       | Percentage of probes that do not receive a response          |
| Hop Count         | Number of network hops in the observed path                  |
| Path Availability | Whether a particular path is reachable                       |
| Path Performance  | Performance comparison between different paths               |

## System Workflow

```text
                    ┌─────────────────────┐
                    │   Diagnostic Tool   │
                    └──────────┬──────────┘
                               │
                         UDP Probes
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Network / SDN    │
                    │      Topology       │
                    └──────────┬──────────┘
                               │
                         UDP Response
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Metric Analysis   │
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
              Path Analysis        SDN Topology
                    │                     │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │ Path Correlation &  │
                    │     Comparison      │
                    └─────────────────────┘
```

## Project Objectives

1. Implement UDP-based network diagnostic probes.
2. Measure round-trip time between source and destination.
3. Detect and calculate packet loss.
4. Analyze the network path followed by packets.
5. Discover and represent the SDN network topology.
6. Correlate application-level measurements with SDN network paths.
7. Identify failed or degraded paths.
8. Compare alternative paths and determine their relative performance.

## Technologies

* **Python**
* **UDP Sockets**
* **Network Programming**
* **SDN**
* **Network Topology Analysis**

## Example Output

```text
Network Diagnostic

Target: 192.168.1.10
Protocol: UDP
Probes Sent: 10
Probes Received: 9

Packet Loss: 10%

RTT:
  Minimum: 2.31 ms
  Maximum: 8.74 ms
  Average: 4.52 ms

Path:
Host → Switch 1 → Switch 3 → Switch 5 → Destination

Path Status: Available

Alternative Path:
Host → Switch 1 → Switch 2 → Switch 5 → Destination

Path Comparison:
Path 1: 4.52 ms, 0% additional loss
Path 2: 7.13 ms, 10% packet loss
```

## Note

This project is intended for **network diagnostics and SDN path analysis** in a controlled or authorized network environment.

