#!/usr/bin/env python
# coding: utf-8
import argparse
import os


def _sanitize(ver):
    skt_list = []
    for point in ver.strip().split('.'):
        point = point.strip()
        try:
            point = int(point)
        except ValueError:
            pass
        skt_list.append(point)
    return skt_list


def _get_ver_str(ver):
    ver_list = _sanitize(ver)
    return ', '.join([repr(point) if not isinstance(point, int)
                      else str(point) for point in ver_list])


def _bump(ver):
    os.system('sed -i \'\' -e "s/version_info = .*/version_info = (%s)/" rest_arch/__init__.py' % _get_ver_str(ver))  # noqa


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('version')
    args = parser.parse_args()
    _bump(args.version)
    os.system('echo "version bumped to `python setup.py --version`"')


if __name__ == '__main__':
    main()
