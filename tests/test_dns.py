import unittest
from unittest.mock import patch

from scapy.all import DNS, DNSRR, Ether, IP, UDP

from probe.DNS import resolve


class ResolveTest(unittest.TestCase):
    def test_sends_dns_query_through_primary_interface(self):
        response = (
            Ether()
            / IP()
            / UDP()
            / DNS(
                qr=1,
                rcode=0,
                ancount=1,
                an=DNSRR(
                    rrname='example.com',
                    type='A',
                    rdata='203.0.113.10',
                ),
            )
        )

        with (
            patch('probe.DNS.conf.nameservers', ['192.0.2.53']),
            patch('probe.DNS.get_if_addr', return_value='192.0.2.10'),
            patch('probe.DNS.get_if_hwaddr', return_value='00:11:22:33:44:55'),
            patch('probe.DNS.arp_request', return_value=object()) as arp_request,
            patch('probe.DNS.get_hwsrc', return_value='66:77:88:99:aa:bb'),
            patch('probe.DNS.srp1', return_value=response) as srp1,
        ):
            result = resolve('example.com', 'ens19', 2)

        self.assertEqual(result, '203.0.113.10')
        arp_request.assert_called_once_with('192.0.2.10', '192.0.2.53', 'ens19', 2)
        packet = srp1.call_args.args[0]
        self.assertEqual(packet[IP].src, '192.0.2.10')
        self.assertEqual(packet[IP].dst, '192.0.2.53')
        self.assertEqual(packet[UDP].dport, 53)
        self.assertEqual(srp1.call_args.kwargs['iface'], 'ens19')

    def test_does_not_send_dns_query_for_ipv4_literal(self):
        with patch('probe.DNS.srp1') as srp1:
            result = resolve('203.0.113.10', 'ens19', 2)

        self.assertEqual(result, '203.0.113.10')
        srp1.assert_not_called()


if __name__ == '__main__':
    unittest.main()
