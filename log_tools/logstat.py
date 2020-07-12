# !/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import datetime
import argparse
# import subprocess


def read_file(args):
    # timestamp_start = int(time.mktime(time.strptime(args.start_time, '%Y-%m-%d %H:%M:%S')))
    # timestamp_end = int(time.mktime(time.strptime(args.end_time, '%Y-%m-%d %H:%M:%S')))
    # interval = timestamp_end - timestamp_start

    start_time = ' '.join(args.start_time)
    end_time = ' '.join(args.end_time)
    count = 0

    if not os.path.exists(args.file):
        raise FileExistsError(f'config {args.file} does not exist')

    try:
        datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')

    except ValueError as err:
        raise (err, '日期格式错误')

    with open(args.file, 'r', encoding='utf-8') as data:
        while start_time < end_time:
            line = data.readline()
            t = line.split('.')[0]
            if start_time > t:
                continue
            elif start_time == t and args.keyword in line:
                count += 1
            elif start_time < t:
                print(f'date: {start_time}, num: {str(count)}')
                start_time = t
                if args.keyword in line:
                    count = 1
                else:
                    count = 0


def main():
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('-f', '--filepath=', required=True, dest='file', help='Specify the log path')
    parser.add_argument('-k', '--keyword=', dest='keyword', default='发送TOPIC  UAV_ATTITUDE_4_WS  uav = 111800011800000066', help='Matching keywords')
    parser.add_argument('-s', '--start=', dest='start_time', nargs=2, help='Specify a start time')
    parser.add_argument('-e', '--end=', dest='end_time', nargs=2, help='Select a end time')
    args = parser.parse_args()
    read_file(args)


if __name__ == '__main__':
    main()
