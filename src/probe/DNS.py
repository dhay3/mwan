from ipaddress import AddressValueError, IPv4Address

from scapy.all import (
    DNS,
    DNSQR,
    Ether,
    IP,
    UDP,
    conf,
    get_if_addr,
    get_if_hwaddr,
    srp1,
)

from .ARP import arp_request, get_hwsrc
from error import MwanProbeError


def resolve(host: str, dev: str, timeout: int) -> str:
    try:
        return str(IPv4Address(host))
    except AddressValueError:
        pass

    src_addr = get_if_addr(dev)
    src_hwaddr = get_if_hwaddr(dev)
    nameservers = []
    for nameserver in conf.nameservers:
        try:
            nameservers.append(str(IPv4Address(nameserver)))
        except AddressValueError:
            continue

    for nameserver in nameservers:
        try:
            dst_hwaddr = get_hwsrc(arp_request(src_addr, nameserver, dev, timeout))
            packet = (
                Ether(src=src_hwaddr, dst=dst_hwaddr)
                / IP(src=src_addr, dst=nameserver)
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

    raise MwanProbeError(f'resolve failed via {dev}: {host}')
