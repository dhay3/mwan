from config.Config import MwanConfig
from scapy.all import (
    sr1,
    send,
    IP,
    TCP,
)


def parse_addr(addr: str):
    host, port = addr.split(":")

    try:
        port = int(port)
    except ValueError:
        raise ValueError(f"invalid port: {addr}")

    if port < 1 or port > 65535:
        raise ValueError(f"invalid port: {addr}")

    return host, port


def ping(config: MwanConfig, addr: str):
    host, port = parse_addr(addr)

    for _ in range(config.probe.count):
        packet = IP(dst=f"{host}%{config.primary.dev}") / TCP(dport=port, flags="S")
        ans = sr1(
            packet,
            timeout=config.probe.timeout,
            verbose=False,
        )
        if ans and ans.haslayer(TCP):
            l3 = ans.getlayer(TCP)
            if l3.flags & 0x12 == 0x12:
                packet = IP(dst=f"{host}%{config.primary.dev}") / TCP(
                    dport=port,
                    sport=l3.dport,
                    flags="R",
                    seq=l3.ack,
                )
                send(
                    packet,
                    verbose=False,
                )
                return True
    return False
