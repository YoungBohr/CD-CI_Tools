#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import shutil
import argparse
from subprocess import Popen, PIPE
import yaml


def get_args():
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('-c', '--config=', required=True, dest='config', help='Specify the config path')
    parser.add_argument('-i', '--instance=', default='default', dest='instance', help='Select a command to be run')
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
        cmd = Popen(f'lsof -i tcp:{t} | grep LISTEN', shell=True, stdout=PIPE)
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

        if result == '':
            continue
        else:
            raise OSError(f'udp {u} has been used')


def prestart_check(cfg):
    file = cfg['file']
    file_path = file['work_dir'] + '/' + file['name']
    owner = file['owner']
    group = file['group']
    mode = file['mode']

    if os.path.exists(file_path):
        shutil.chown(file_path, user=owner, group=group)
        os.chmod(file_path, mode)
    else:
        raise FileExistsError(f'{file_path} does not exist')

    write_enable = cfg['write_enable']
    # assert isinstance(write_enable, list)
    for w in write_enable:
        if os.access(w, os.R_OK | os.W_OK):
            continue
        else:
            os.chmod(w, os.R_OK | os.W_OK)

    net = cfg['net']
    tcp = net['tcp']
    # assert isinstance(tcp, list)
    if len(tcp) > 0:
        check_tcp(tcp)

    udp = net['udp']
    # assert isinstance(udp, list)
    if len(udp) > 0:
        check_udp(udp)


def get_env(cfg):
    env_dict = {}
    get_env_list = cfg['get']
    assert isinstance(get_env_list, list)

    if len(get_env_list) > 0:
        for g in get_env_list:
            env = os.environ.get(g)
            env_dict[g] = env

    set_env_list = cfg['set']
    assert isinstance(set_env_list, list)

    if len(set_env_list) > 0:
        for s in set_env_list:
            env_list = s.split('=')
            env_dict[env_list[0]] = env_list[1]

    if len(env_dict) > 0:
        return env_dict
    else:
        return None


def startup(cfg, instance):
    command = cfg['command'][instance]
    # assert isinstance(command, list)

    pid_file = cfg['pid']
    envs = get_env(cfg['environment'])

    process = Popen(command, shell=False, env=envs, stdin=None, stdout=None, stderr=None, close_fds=True)
    with open(pid_file, 'w+') as f:
        f.write(f'{process.pid}')

    return 0


def main():
    args = get_args()
    path = args.config
    instance = args.instance
    config = read_config(path)

    prestart_check(config)
    run_config = config['run']
    startup(run_config, instance)


if __name__ == '__main__':
    main()
