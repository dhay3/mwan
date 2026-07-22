from config.Config import MwanConfig
from scapy.all import (
    Ether,
    IP,
    TCP,
    get_if_addr,
    get_if_hwaddr,
    sendp,
    srp1,
)

from .ARP import arp_request, get_hwsrc
from .DNS import resolve


def parse_addr(addr: str):
    if ':' not in addr or addr.endswith(':'):
        raise ValueError(f'missing port: {addr}')

    host, port = addr.split(':')

    try:
        port = int(port)
    except ValueError:
        raise ValueError(f'invalid port: {addr}')

    if port < 1 or port > 65535:
        raise ValueError(f'invalid port: {addr}')

    return host, port


def ping(config: MwanConfig, addr: str):
    host, port = parse_addr(addr)
    dev = config.primary.dev
    dst_addr = resolve(host, dev, config.probe.timeout)
    src_addr = get_if_addr(dev)
    src_hwaddr = get_if_hwaddr(dev)
    dst_hwaddr = get_hwsrc(arp_request(src_addr, dst_addr, dev, config.probe.timeout))

    for _ in range(config.probe.count):
        packet = (
            Ether(src=src_hwaddr, dst=dst_hwaddr)
            / IP(src=src_addr, dst=dst_addr)
            / TCP(dport=port, flags='S')
        )
        ans = srp1(
            packet,
            iface=dev,
            timeout=config.probe.timeout,
            verbose=False,
        )
        if ans and ans.haslayer(TCP):
            l3 = ans.getlayer(TCP)
            if l3.flags & 0x12 == 0x12:
                packet = (
                    Ether(src=src_hwaddr, dst=dst_hwaddr)
                    / IP(src=src_addr, dst=dst_addr)
                    / TCP(
                        dport=port,
                        sport=l3.dport,
                        flags='R',
                        seq=l3.ack,
                    )
                )
                sendp(
                    packet,
                    iface=dev,
                    verbose=False,
                )
                return True
    return False
