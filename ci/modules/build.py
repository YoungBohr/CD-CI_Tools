# -*- coding: utf-8 -*-

import os
import tarfile
from git import Repo
from datetime import datetime


class Artifact(object):
    def __init__(self, path):
        self.repo = Repo(path)

    def check(self):
        if self.repo.is_dirty():
            untracked_files = self.repo.untracked_files()
            raise Exception(f'Repository data has been modified\n{untracked_files}')
        return True

    def get_head(self):
        head_hash = self.repo.head.object.hexsha
        return head_hash

    def change_log(self, previous_commit_hash=None):
        if previous_commit_hash is None:
            previous_commit_hash = list(self.repo.iter_commits())[1]

        changes = self.repo.git.diff(previous_commit_hash, self.get_head())
        assert isinstance(changes, str)
        return changes

    def sync(self, branch, reset=False, remote='origin/master'):
        if reset:
            output = self.repo.git.reset('--hard', remote)
            print(output)
        try:
            output = self.repo.git.checkout(branch)
            print(output)
            output = self.repo.git.pull()
            print(output)
        except Exception as errors:
            raise errors
        else:
            print('Successful synchronization')
            return 0

    def committer(self):
        author = self.repo.head.reference.commit.author.name
        email = self.repo.head.reference.commit.author.email
        date = datetime.fromtimestamp(
            self.repo.head.reference.commit.committed_date)
        message = self.repo.head.reference.commit.message
        commit_info = [author, email, date, message]
        return commit_info


class BuildWithGradle(Artifact):
    def __init__(self, path, **meta):
        super().__init__(path)
        self.meta = meta

    def build(self):
        cmd = self.meta['build_command']
        build_path = self.meta['build_path']
        os.chdir(build_path)
        value = os.system(cmd)
        value = value >> 8

        if value > 0:
            raise SystemError('[Error]: Compile Failed')

    def pack(self, dist, version):
        app = self.meta['app']
        folder = self.meta['archive_folder']
        date = datetime.today().strftime("%Y%m%d")
        jar_name = f'{app}-{version}.jar'
        tar_ball = f'{dist}/{app}-{version}-{date}.tgz'

        for f in os.listdir(folder):
            if app in f and f.endswith('.jar'):
                with tarfile.open(tar_ball, 'w:gz') as tar:
                    tar.add(f'{folder}/{f}', arcname=jar_name)
                break
            else:
                raise FileExistsError('Artifact Not Found')

        return tar_ball


class NpmBuild(Artifact):
    def __init__(self, path, **meta):
        super().__init__(path)
        self.meta = meta

    def build(self):
        build_path = self.meta['build_path']
        os.chdir(build_path)

        if not os.system('npm install'):
            raise SystemError('[Error]: Missing Requirements')

        value = os.system('npm run build')
        value = value >> 8

        if value > 0:
            raise SystemError('[Error]: Compile Failed')

    def pack(self, dist, version):
        web = self.meta['web']
        folder = self.meta['build_folder']
        date = datetime.today().strftime("%Y%m%d")
        tar_ball = f'{dist}/{web}-{version}-{date}.tgz'

        with tarfile.open(tar_ball, 'w:gz') as tar:
            for f in os.listdir(folder):
                tar.add(f'{folder}/{f}')

        return tar_ball


__all__ = (Artifact, BuildWithGradle, NpmBuild)
