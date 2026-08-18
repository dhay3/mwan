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

from .ARP import resolve_hwaddr
from error import MwanProbeError


def dns_request(
    host: str,
    l3_src: str,
    l3_dst: str,
    l2_src: str,
    l2_dst: str,
    dev: str,
    timeout: int,
):
    packet = (
        Ether(src=l2_src, dst=l2_dst)
        / IP(src=l3_src, dst=l3_dst)
        / UDP(dport=53)
        / DNS(rd=1, qd=DNSQR(qname=host, qtype='A'))
    )
    ans = srp1(
        packet,
        iface=dev,
        timeout=timeout,
        verbose=False,
    )
    return ans


def get_rdata(ans) -> str:
    if ans is None or not ans.haslayer(DNS):
        return

    dns = ans.getlayer(DNS)
    if dns.qr != 1 or dns.rcode != 0:
        return

    for index in range(dns.ancount or 0):
        answer = dns.an[index]
        if answer.type == 1:
            return str(IPv4Address(answer.rdata))


def resolve_host(config: MwanConfig, host: str) -> str:
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
            dst_hwaddr = resolve_hwaddr(src_addr, nameserver_addr, dev, timeout)
            ans = dns_request(
                host,
                src_addr,
                nameserver_addr,
                src_hwaddr,
                dst_hwaddr,
                dev,
                timeout,
            )
            rdata = get_rdata(ans)
            if rdata is not None:
                return rdata
        except MwanProbeError:
            continue

    dns_servers = ','.join(str(nameserver) for nameserver in config.probe.dns)
    raise MwanProbeError(f'dns resolve failed: {dev} {dns_servers} {host}')


__all__ = ['resolve_host']
