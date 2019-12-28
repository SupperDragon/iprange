#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import ipaddress
import re

class IpRange:
    '''
        @brief: IP范围类, 支持IPv4和IPv6格式
    '''
    def __init__(self):
        self._ip_min = None
        self._ip_max = None

    def _match_host_ip(self, hostip):
        '''
            @brief: 用单个IP地址初始化IP范围
            @param hostip: 主机ip, 支持点分十进制格式/整形格式/字节序格式
            @return: 成功返回True, 失败返回False
        '''
        try:
            ipobj = ipaddress.ip_address(hostip)
            self._ip_min = ipobj
            self._ip_max = ipobj
        except ValueError:
            return False
        return True

    def _match_network(self, network):
        '''
            @brief: 用一个网络初始化IP范围
            @param network: 网络地址, 支持掩码格式和前缀格式
            @return: 成功返回True, 失败返回False
        '''
        try:
            netobj = ipaddress.ip_network(network, strict=False)
            self._ip_min = netobj[0]
            self._ip_max = netobj[-1]
        except ValueError:
            return False
        return True

    def _match_ip_section(self, section):
        '''
            @brief: 用一个IP地址区间初始化IP范围
            @param section: IP地址区间字符串
            @return: 成功返回True, 失败返回False
        '''
        if not isinstance(section, str):
            return False

        section = section.strip()
        if section == "":
            return False

        # 正则表达式不需要太严格,后面的ipaddress会替我们把关
        mtch = re.match(r'^([0-9A-Fa-f.:]+)\s*-\s*([0-9A-Fa-f.:]+)$', section)
        if mtch is None:
            return False

        start, end = mtch.groups()
        try:
            start_obj = ipaddress.ip_address(start)
            end_obj = ipaddress.ip_address(end)
            if start_obj.version != end_obj.version:
                return False
            if start_obj < end_obj:
                self._ip_min, self._ip_max = start_obj, end_obj
            else:
                self._ip_min, self._ip_max = end_obj, start_obj
        except ValueError:
            return False
        return True

    def set_range(self, iprange):
        '''
            @brief: 设置IP地址范围
            @param iprange: IP地址范围
            @return 成功返回True, 失败返回False
        '''
        if self._match_host_ip(iprange):
            return True
        if self._match_network(iprange):
            return True
        if self._match_ip_section(iprange):
            return True
        return False

    def contain(self, ip):
        try:
            ipobj = ipaddress.ip_address(ip)
            return ipobj >= self._ip_min and ipobj <= self._ip_max
        except ValueError:
            return False
        return False
