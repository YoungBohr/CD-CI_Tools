# -*- coding: utf-8 -*-

import os
from hash import checksum
from cd.publish import (JavaArchive,
                        WebPackage)


class RollBack(JavaArchive, WebPackage):
    def __init__(self, config_path):
        super().__init__(config_path)

    @staticmethod
    def backup_info(path, enum=-1):
        backup_dir = path
        backups = os.listdir(backup_dir)
        if len(backups) > 1:
            backups.sort(key=lambda x: os.path.getctime(os.path.join(backup_dir, x)))

        if enum == -1:
            return backups

        if enum > len(backups):
            raise IndexError('Index out of range')

        file_path = os.path.join(backup_dir, backups[enum])
        file_size = os.path.getsize(file_path)
        version = backups[enum].split('-')[1]
        date = os.path.getctime(backup_dir)
        _checksum = checksum(backup_dir)

        info = {'name': backups[enum], 'byte': file_size,
                'version': version, 'publish_date': date,
                'checksum': _checksum}

        return info
