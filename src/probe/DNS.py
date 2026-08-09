from ipaddress import AddressValueError, IPv4Address

from config import MwanConfig
from scapy.all import (
    DNS,
    DNSQR,
    Ether,
    IP,
    UDP,
    get_if_addr,
    get_if_hwaddr,
    srp1,
)

from .ARP import arp_request, get_hwsrc
from error import MwanProbeError


def resolve(config: MwanConfig, host: str) -> str:
    try:
        return str(IPv4Address(host))
    except AddressValueError:
        pass

    dev = config.primary.dev
    timeout = config.probe.timeout
    src_addr = get_if_addr(dev)
    src_hwaddr = get_if_hwaddr(dev)

    for nameserver in config.probe.dns:
        nameserver_addr = str(nameserver)
        try:
            dst_hwaddr = get_hwsrc(arp_request(src_addr, nameserver_addr, dev, timeout))
            packet = (
                Ether(src=src_hwaddr, dst=dst_hwaddr)
                / IP(src=src_addr, dst=nameserver_addr)
                / UDP(dport=53)
                / DNS(rd=1, qd=DNSQR(qname=host, qtype='A'))
            )
            ans = srp1(
                packet,
                iface=dev,
                timeout=timeout,
                verbose=False,
            )
        except Exception:
            continue

        if not ans or not ans.haslayer(DNS):
            continue

        dns = ans.getlayer(DNS)
        if dns.qr != 1 or dns.rcode != 0:
            continue

        for index in range(dns.ancount or 0):
            answer = dns.an[index]
            if answer.type == 1:
                return str(IPv4Address(answer.rdata))

    dns_servers = ','.join(str(nameserver) for nameserver in config.probe.dns)
    raise MwanProbeError(f'dns resolve failed: {dev} [{dns_servers}] {host}')
