import logging
import uuid
from functools import cache
from typing import NamedTuple

from config.Config import MwanConfig


logger = logging.getLogger("Probe")


class ScapyModules(NamedTuple):
    ICMP: type
    IP: type
    TCP: type
    UDP: type
    Raw: type
    send: object
    sr1: object


@cache
def load_scapy() -> ScapyModules:
    try:
        from scapy.layers.inet import ICMP, IP, TCP, UDP
        from scapy.packet import Raw
        from scapy.sendrecv import send, sr1
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "scapy is required for probe packets; install scapy>=2.6,<3.0"
        ) from exc
    return ScapyModules(ICMP, IP, TCP, UDP, Raw, send, sr1)


def parse_host_port(value: str) -> tuple[str, int]:
    host, separator, port_value = value.rpartition(":")
    if not separator or not host or not port_value:
        raise ValueError(f"host must include port: {value}")

    try:
        port = int(port_value)
    except ValueError as exc:
        raise ValueError(f"invalid port in host: {value}") from exc

    if port < 1 or port > 65535:
        raise ValueError(f"port out of range in host: {value}")

    return host, port


def receive_one(config: MwanConfig, packet):
    scapy = load_scapy()
    return scapy.sr1(
        packet,
        iface=config.primary.dev,
        timeout=config.probe.timeout,
        verbose=False,
    )


def icmp_ping(config: MwanConfig, addr: str) -> bool:
    if ":" in addr:
        raise ValueError(f"icmp host must not include port: {addr}")

    scapy = load_scapy()
    for sequence in range(config.probe.count):
        packet = scapy.IP(dst=addr) / scapy.ICMP(seq=sequence)
        response = receive_one(config, packet)
        if response and response.haslayer(scapy.ICMP):
            icmp = response.getlayer(scapy.ICMP)
            if icmp.type == 0:
                return True
    return False


def tcp_ping(config: MwanConfig, addr: str) -> bool:
    host, port = parse_host_port(addr)
    scapy = load_scapy()
    for _ in range(config.probe.count):
        packet = scapy.IP(dst=host) / scapy.TCP(dport=port, flags="S")
        response = receive_one(config, packet)
        if not response or not response.haslayer(scapy.TCP):
            continue

        tcp = response.getlayer(scapy.TCP)
        if tcp.flags & 0x12 == 0x12:
            reset = scapy.IP(dst=host) / scapy.TCP(
                dport=port,
                sport=tcp.dport,
                flags="R",
                seq=tcp.ack,
            )
            scapy.send(reset, iface=config.primary.dev, verbose=False)
            return True
    return False


def udp_ping(config: MwanConfig, addr: str) -> bool:
    host, port = parse_host_port(addr)
    scapy = load_scapy()
    for _ in range(config.probe.count):
        packet = (
            scapy.IP(dst=host) / scapy.UDP(dport=port) / scapy.Raw(load=b"mwan-probe")
        )
        response = receive_one(config, packet)
        if response is None:
            return True
        if response.haslayer(scapy.ICMP):
            icmp = response.getlayer(scapy.ICMP)
            if icmp.type == 3 and icmp.code == 3:
                continue
        return True
    return False


def ping(config: MwanConfig, addr: str) -> bool:
    if config.probe.protocol == 0:
        return icmp_ping(config, addr)
    if config.probe.protocol == 1:
        return tcp_ping(config, addr)
    if config.probe.protocol == 2:
        return udp_ping(config, addr)
    raise RuntimeError(f"unsupported probe protocol: {config.probe.protocol}")


def ping_cycle(config: MwanConfig) -> bool:
    results = []
    uid = uuid.uuid4()
    for addr in config.probe.hosts:
        try:
            result = ping(config, addr)
        except Exception as exc:
            raise RuntimeError(f"event_id={uid}") from exc
        results.append(result)
    fail = not any(results)
    return fail
