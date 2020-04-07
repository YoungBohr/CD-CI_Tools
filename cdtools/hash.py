# -*- coding: utf-8 -*-

import hashlib

__all__ = ('checksum',)


def checksum(path):
    with open(path, 'rb') as file:
        chunk = file.read()
        md5 = hashlib.md5(chunk).hexdigest()
        sha1 = hashlib.sha1(chunk).hexdigest()
        sha512 = hashlib.sha512(chunk).hexdigest()
    _sum = {'md5': md5, 'sha1': sha1, 'sha512': sha512}
    return _sum
