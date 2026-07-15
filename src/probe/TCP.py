import socket

from config.Config import MwanConfig
from .L2 import ether, resolve_target
from scapy.all import (
    IP,
    TCP,
    sendp,
    srp1,
)


def parse_addr(addr: str):
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
    dst_addr = socket.gethostbyname(host)
    target = resolve_target(dev, dst_addr, config.probe.timeout)

    for _ in range(config.probe.count):
        packet = (
            ether(target)
            / IP(src=target.src_addr, dst=target.dst_addr)
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
                    ether(target)
                    / IP(src=target.src_addr, dst=target.dst_addr)
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
