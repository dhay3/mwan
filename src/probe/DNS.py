from ipaddress import AddressValueError, IPv4Address

from scapy.layers.dns import dns_resolve


def resolve(host):
    try:
        return str(IPv4Address(host))
    except AddressValueError:
        pass

    answers = dns_resolve(
        qname=host,
        qtype='A',
        timeout=1,
        verbose=0,
    )

    if not answers:
        raise RuntimeError(f'dns resolve failed: {host}')

    return str(IPv4Address(answers[0].rdata))
