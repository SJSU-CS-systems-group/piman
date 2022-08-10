# DNS

## Navigation
- [DNS Resource Record](#dns-resource-record)
- [Resource Record Format](#resource-record-format)
    - [A RR](#a-rr)
    - [PTR RR](#ptr-rr)
    - [SRV RR](#srv-rr)
    - [What about multiple answers?](#what-about-multiple-answers)
- [Why we need DNS server and SRV records in piman?](#why-we-need-dns-server-and-srv-records-in-piman)
- [How to test](#how-to-test)
- [Suggestion for extracting DNS format](#suggestion-for-extracting-dns-format)
## DNS Resource Record
DNS resource records are categorized information to query, for example, some common ones might Type A for resolving hostnames, Type PTR for reverse DNS lookups, and Type SRV for indicating service location (in our case, it is node_exporter). You can explore more RRs on [Wiki](https://en.wikipedia.org/wiki/List_of_DNS_record_types).

## Resource Record Format
Here, we only focus on the DNS response's Anwser section since other sections are mostly identical to the ones in the request. And for more information, you can read [rfc1034](https://datatracker.ietf.org/doc/html/rfc1034), [rfc1035](https://datatracker.ietf.org/doc/html/rfc1035), and [rfc2782](https://datatracker.ietf.org/doc/html/rfc2782).

Please follow the order from top and the size of each field to construct your packet. For the Name field, you can use a two-byte pointer b'\xc0\x0c' that points to the Zone RR Name field. And if the you are returning host names as data, you need to put a null byte (\x00) at the end of the Data field.
### A RR
| Field        | Size           | Note                                                      |
| ------------ |:--------------:| -----:                                                    |
| Name         | 16 bits        | \xc0\x0c                                                  |
| Type         | 16 bits        | value is 1                                                |
| Class        | 16 bits        | value is 1 (Internet: IN)                                 |
| TTL          | 32 bits        | unsigned integer that specifies the time period in seconds|
| Data length  | 16 bits        | the length of Data field (unit: byte)                     |
| Data         | 32 bits        | IPv4 address                                              |

<br>

### PTR RR
| Field        | Size           | Note                                                      |
| ------------ |:--------------:| -----:                                                    |
| Name         | 16 bits        | \xc0\x0c                                                  |
| Type         | 16 bits        | value is 12                                               |
| Class        | 16 bits        | value is 1 (Internet: IN)                                 |
| TTL          | 32 bits        | unsigned integer that specifies the time period in seconds|
| Data length  | 16 bits        | the length of Data field (unit: byte)                     |
| Data         | variable size  | host name                                                 |

<br>

### SRV RR
| Field        | Size           | Note                                                       |
| ------------ |:--------------:| -----:                                                     |
| Name         | 16 bits        | \xc0\x0c                                                   |
| Type         | 16 bits        | value is 33                                                |
| Class        | 16 bits        | value is 1 (Internet: IN)                                  |
| TTL          | 32 bits        | unsigned integer that specifies the time period in seconds |
| Data length  | 16 bits        | the length of Data field (unit: byte)                      |
| Data         | variable size  | Data field consists of Priority, Weight, Port, and Target  |
| Priority     | 16 bits        | unsigned integer                                           |
| Weight       | 16 bits        | unsigned integer                                           |
| Port         | 16 bits        | range from 0 -65535                                        |
| Target       | variable size  | target's host name                                         |

<br>

### What about multiple answers?
You will need to ANCOUNT to the number of answers in the header section in the resposne packets, and combine all the answers in the answer section.

For example, if you are returning two answers, first, set the ANCOUNT to 2. And pack two anwsers back to back like this:

Name 1 | Type 1 | Class 1| TTL 1| Data length 1| Data 1| Name 2 | Type 2 | Class 2| TTL 2| Data length 2| Data 2

## Why we need DNS server and SRV records in piman?
In order to use Prometheus on piman and export the metric data from all the pis, we need to specify where to gather data, and in this case, it will be all the pi's IP addresses and port 9100 if we use node_exporter.

However, there will be **prometheus.yml** that specifes where to gather data and **hosts.csv** that contains all the pis' IPs, and if we need to add one more pi, we will need to update two files. Hence, to keep it simple and easy to maintain, we use SRV records to indicate the services' location, which means that we only need to specify target as **metrics.city.cs158b** in **prometheus.yml**, and the DNS server (piman) will resolve all the pi's addresses and ports for us (node_exporter). To be specific, **metrics.city.cs158b** is the general name we use for SRV records, and you might need to change it to the one you use.

## How to test
Resolve pi's host name.
- pi-port: pi's port number, ex: 1, 2, 11, or 12
- city: your city name, ex: eureka
```bash
dig @127.0.0.1 pi[pi-port].city.cs158b
# ex: dig @127.0.0.1 pi1.eureka.cs158b
```

Resolve pi's IP
- pi-IP: pi's IP, ex: 172.16.5.1
```bash
dig @127.0.0.1 -x [pi-IP]
# ex: dig @127.0.0.1 -x 172.16.5.1
```

Resolve SRV records for all pis
- city: your city name, ex: eureka
```bash
dig @127.0.0.1 SRV metrics.city.cs158b
# ex: dig @127.0.0.1 SRV metrics.eureka.cs158b
```

Resolve non-cs158b TLD queries
```bash
dig @127.0.0.1 yahoo.com
dig @127.0.0.1 -x 157.240.22.35
dig @127.0.0.1 SRV _sip._udp.sip.voice.google.com
dig @127.0.0.1 SRV srv _xmpp-client._tcp.jabberzac.org
```

## Suggestion for extracting DNS format
Use **WireShark** and set the filter on *dns*. The following commands are also helpful:
```bash
dig @8.8.8.8 yahoo.com
dig @8.8.8.8 -x 157.240.22.35
dig @8.8.8.8 SRV _sip._udp.sip.voice.google.com
dig @8.8.8.8 SRV srv _xmpp-client._tcp.jabberzac.org
```
