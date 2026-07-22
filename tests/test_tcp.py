import unittest

from probe.TCP import parse_addr


class ParseAddrTest(unittest.TestCase):
    def test_rejects_address_without_port_separator(self):
        with self.assertRaisesRegex(ValueError, r'^missing port: example\.com$'):
            parse_addr('example.com')

    def test_rejects_empty_port(self):
        with self.assertRaisesRegex(ValueError, r'^missing port: example\.com:$'):
            parse_addr('example.com:')

    def test_accepts_address_with_port(self):
        self.assertEqual(parse_addr('example.com:443'), ('example.com', 443))


if __name__ == '__main__':
    unittest.main()
