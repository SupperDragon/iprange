#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pdb
import unittest
import ipaddress
from iprange import IpRange

class Test_IpRange_set_range(unittest.TestCase):
    '''
        @brief: 测试IpRange类的set_range()接口
    '''
    def setUp(self):
        self.myrange = IpRange()

    def test_set_host_ip(self):
        '''
            @brief: 用主机IP初始化
        '''
        # 支持点分十进制字符串初始化
        ipv4_str = "192.168.1.2"
        self.assertTrue(self.myrange.set_range(ipv4_str))
        self.assertEqual(ipv4_str, self.myrange._ip_min.compressed)
        self.assertEqual(self.myrange._ip_min, self.myrange._ip_max)

        # 支持32位整形IP初始化
        ipv4_int = 3232235777 # 192.168.1.1
        self.assertTrue(self.myrange.set_range(ipv4_int))
        self.assertEqual("192.168.1.1", self.myrange._ip_min.compressed)
        self.assertEqual(self.myrange._ip_min, self.myrange._ip_max)

        # 支持32位packed数据初始化
        ipv4_packed = b'\xC0\xA8\x00\x01' # 192.168.0.1
        self.assertTrue(self.myrange.set_range(ipv4_packed))
        self.assertEqual("192.168.0.1", self.myrange._ip_min.compressed)
        self.assertEqual(self.myrange._ip_min, self.myrange._ip_max)

        # 支持IPv6
        ipv6_str = "2001:db8::1000"
        self.assertTrue(self.myrange.set_range(ipv6_str))
        self.assertEqual(ipv6_str, self.myrange._ip_min.compressed)
        self.assertEqual(self.myrange._ip_min, self.myrange._ip_max)

    def test_set_prefix_network(self):
        '''
            @brief: 用前缀式网络地址初始化
        '''
        # 支持IPv4网络地址
        netv4_str = "192.168.0.0/24"
        self.assertTrue(self.myrange.set_range(netv4_str))
        self.assertEqual("192.168.0.0", self.myrange._ip_min.compressed)
        self.assertEqual("192.168.0.255", self.myrange._ip_max.compressed)

        # 支持IPv6网络地址
        netv6_str = "2001:db00::/112"
        self.assertTrue(self.myrange.set_range(netv6_str))
        self.assertEqual("2001:db00::", self.myrange._ip_min.compressed.lower())
        self.assertEqual("2001:db00::ffff", self.myrange._ip_max.compressed.lower())

    def test_set_mark_network(self):
        '''
            @brief: 用子网掩码式网络地址初始化
        '''
        # 支持IPv4网络地址
        netv4_str = "192.168.0.0/255.255.255.0"
        self.assertTrue(self.myrange.set_range(netv4_str))
        self.assertEqual("192.168.0.0", self.myrange._ip_min.compressed)
        self.assertEqual("192.168.0.255", self.myrange._ip_max.compressed)

    def test_set_loose_fmt_network(self):
        '''
            @brief: 支持非严格格式的网络地域
        '''
        netv4_str = "192.168.0.1/24"
        self.assertTrue(self.myrange.set_range(netv4_str))
        self.assertEqual("192.168.0.0", self.myrange._ip_min.compressed)
        self.assertEqual("192.168.0.255", self.myrange._ip_max.compressed)

    def test_set_ip_section(self):
        '''
            @brief: 用IP区间初始化
        '''
        # 支持IPv4地址区间
        ipv4_sec = "192.168.0.0-192.168.0.255"
        self.assertTrue(self.myrange.set_range(ipv4_sec))
        self.assertEqual("192.168.0.0", self.myrange._ip_min.compressed)
        self.assertEqual("192.168.0.255", self.myrange._ip_max.compressed)

        # 支持IPv6地址区间
        ipv6_sec = "2001:db00::000f-2001:db00::00ff"
        self.assertTrue(self.myrange.set_range(ipv6_sec))
        self.assertEqual("2001:db00::f", self.myrange._ip_min.compressed.lower())
        self.assertEqual("2001:db00::ff", self.myrange._ip_max.compressed.lower())

    def test_strict_version(self):
        '''
            @brief: 地址范围的起始与结束要是相同版本的地址
        '''
        ip_sec = "192.168.0.0-2001:db00::ffff"
        self.assertFalse(self.myrange.set_range(ip_sec))

class Test_IpRange_containment_test(unittest.TestCase):
    '''
        @brief: 测试IpRange类的contain()接口
    '''
    def setUp(self):
        self.ipv4range = IpRange()
        self.ipv4range.set_range("192.168.123.0/24")
        self.ipv6range = IpRange()
        self.ipv6range.set_range("2001:db00::f-2001:db00::ff")

    def test_ipv4_containment(self):
        '''
            @brief: 测试IPv4的包含关系
        '''
        # 被测试的IP包含于IP范围内时, 返回True
        self.assertTrue(self.ipv4range.contain("192.168.123.0"))
        self.assertTrue(self.ipv4range.contain("192.168.123.255"))
        self.assertTrue(self.ipv4range.contain("192.168.123.128"))
        # 被测试 的IP超出国IP范围时, 返回False
        self.assertFalse(self.ipv4range.contain("192.168.122.255"))
        self.assertFalse(self.ipv4range.contain("192.168.124.0"))

    def test_ipv6_containment(self):
        '''
            @brief: 测试IPv6包含关系
        '''
        # 被测试的IP包含于IP范围内时, 返回True
        self.assertTrue(self.ipv6range.contain("2001:db00::f"))
        self.assertTrue(self.ipv6range.contain("2001:db00::f0"))
        self.assertTrue(self.ipv6range.contain("2001:db00::ff"))
        # 被测试 的IP超出国IP范围时, 返回False
        self.assertFalse(self.ipv6range.contain("2001:db00::e"))
        self.assertFalse(self.ipv6range.contain("2001:db00::100"))

    def test_support_ipstr(self):
        '''
            @brief: 测试对ip字符串的支持
        '''
        self.assertTrue(self.ipv4range.contain("192.168.123.128"))
        self.assertTrue(self.ipv6range.contain("2001:db00::f0"))

    def test_support_packed_ipbytes(self):
        '''
            @brief: 测试对 IP 字节序列的支持
        '''
        ipobj = ipaddress.ip_address("192.168.123.123")
        ippacked = ipobj.packed
        self.assertTrue(self.ipv4range.contain(ippacked))

    def test_support_int_ip(self):
        '''
            @brief: 测试对整型IP地域的支持
        '''
        self.assertTrue(self.ipv4range.contain(3232267135))


if __name__ == "__main__":
    unittest.main()
