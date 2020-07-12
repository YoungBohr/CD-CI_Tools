# !/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import time
import argparse


def read_file(args):
    start_time = ' '.join(args.start_time)
    end_time = ' '.join(args.end_time)
    count = 0

    if not os.path.exists(args.file):
        raise FileExistsError(f'config {args.file} does not exist')

    try:
        timestamp_start = int(time.mktime(time.strptime(start_time, '%Y-%m-%d %H:%M:%S')))
        timestamp_end = int(time.mktime(time.strptime(end_time, '%Y-%m-%d %H:%M:%S')))

    except ValueError as err:
        raise (err, '日期格式错误')

    with open(args.file, 'r', encoding='utf-8') as f:
        while l in line:
            line = f.readline()
            for i in range(timestamp_start, timestamp_end):
                date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(i))
                if date in line:
                    if args.keywords in line:
                        count += 1
                    line = f.readline()
                print(f'date:{date}, num: {count}')
                count = 0


def main():
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('-f', '--filepath=', required=True, dest='file', help='Specify the log path')
    parser.add_argument('-k', '--keyword=', dest='keywords', help='Matching keywords')
    parser.add_argument('-s', '--start=', dest='start_time', nargs=2, help='Specify a start time')
    parser.add_argument('-e', '--end=', dest='end_time', nargs=2, help='Select a end time')
    args = parser.parse_args()
    read_file(args)


if __name__ == '__main__':
    main()
