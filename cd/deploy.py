#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import argparse
import subprocess
import yaml


def get_args():
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('-c', '--config=', dest='config', help='Specify the config path')
    parser.add_argument('-f', '--file=', dest='file', help='Specify the custom file')
    parser.add_argument('-w', '--website', default=False, dest='website', help='Whether it is a web package, the '
                                                                               'default is False')
    args = parser.parse_args()
    return args


def read_config(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as data:
            configs = yaml.load(data, Loader=yaml.FullLoader)
        return configs
    else:
        raise FileExistsError(f'config {path} does not exist')


def check_tcp(tcp):
    for t in tcp:
        if t > 65534:
            continue
        cmd = subprocess.Popen(f'lsof -i tcp:{t} | grep LISTEN', shell=True, stdout=subprocess.PIPE)
        result = cmd.communicate()[0].decode('utf-8')

        if result != '':
            raise OSError(f'tcp {t} has been used')

        cmd.stdout.close()


def check_udp(udp):
    for u in udp:
        if u > 65534:
            continue
        cmd = os.popen(f'lsof -i udp:{u}', 'r', 1)
        result = cmd.read()
        cmd.close()

        if result != '':
            raise OSError(f'udp {u} has been used')
