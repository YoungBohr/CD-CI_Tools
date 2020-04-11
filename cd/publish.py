# /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import yaml


class Archive(object):

    def __init__(self, config_path):
        self.archive = ''
        self.conf = config_path
        if not os.path.exists(self.conf):
            raise FileExistsError('Config does not exist')
        with open(self.conf, 'r', encoding="utf-8") as meta:
            self.meta = yaml.load(meta)

    @property
    def version(self):
        version = self.meta['version']
        return version

    @version.setter
    def version(self, value):
        assert isinstance(value, str)
        self.meta['version'] = value
        with open(self.conf, 'r+', encoding="utf-8") as meta:
            yaml.dump(self.meta, meta)

    def check(self):
        user = self.meta['user']
        group = self.meta['group']
        relevant_dirs = self.meta['relevant_dirs'].split(',')

        if not os.path.exists(self.archive):
            raise FileExistsError(f'{self.archive} ought to be deployed was not found')

        if self.version not in self.archive:
            raise Exception('Mismatch Version')

        for r in relevant_dirs:
            if not os.path.exists(r):
                os.makedirs(r, 0o755)
            os.chown(r, user, group)

        return True

    def backup(self, reserves=3, clean_up=True):
        backup_dir = self.meta['backup_dir']
        shutil.move(self.archive, backup_dir)

        backups = os.listdir(backup_dir)
        if len(backups) > 1:
            backups.sort(key=lambda x: os.path.getctime(os.path.join(backup_dir, x)))

        if clean_up:
            if len(backups) > reserves:
                for b in backups[reserves:]:
                    needless = os.path.join(backup_dir, b)
                    os.remove(needless)


class JavaArchive(Archive):

    def __init__(self, config_path):
        super().__init__(config_path)

    @property
    def jar(self):
        with open(self.conf, 'r', encoding="utf-8") as meta:
            jar_path = yaml.load(meta)['jar']
        return jar_path

    @jar.deleter
    def jar(self):
        os.remove(self.jar)

    def upgrade(self, arg=None):
        instance = self.meta['app']
        shutil.unpack_archive(self.archive, self.jar)

        if not arg:
            instance = instance + '@' + arg

        value = os.system(f'sudo systemctl restart {instance}')
        value = value >> 8
        if value > 0:
            del self.jar
            raise SystemError('[Error]: Startup Exception')
        else:
            print('Deployed Successfully')

        return True

    def rollback(self, backup):
        if not os.path.exists(backup):
            raise FileExistsError
        else:
            self.archive = backup
        self.upgrade()


class WebPackage(Archive):

    def __init__(self, config_path):
        super().__init__(config_path)
        self.root = self.meta['html_root_path']

    def upgrade(self):
        user = self.meta['user']
        group = self.meta['group']
        objects = self.meta['objects_to_be_replaced']

        for o in objects:
            path = os.path.join(self.root, o)
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)

        shutil.unpack_archive(self.archive, self.root)
        shutil.chown(self.root, user, group)
        print('Finished')

        return True

    def rollback(self, backup):
        if not os.path.exists(backup):
            raise FileExistsError
        else:
            self.archive = backup
        self.upgrade()


__all__ = (Archive, JavaArchive, WebPackage)
