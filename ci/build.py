# /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import yaml
import shutil
import subprocess
from modules.orm import *
from git import Repo
from datetime import datetime
from git import GitCommandError
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

engine = create_engine('mysql+mysqldb://tta:tta2020@mysql.nextlord.com:3306/devops?charset=utf8', encoding='utf-8')
Session = sessionmaker(bind=engine)


def row_insert(row):
    session = Session()
    session.add(row)
    session.commit()
    session.close()


def read_config(config_path):
    if not os.path.exists(config_path):
        raise FileExistsError('配置文件不存在')

    with open(config_path, 'r', encoding="utf-8") as data:
        config = yaml.load(data)

    return config


def search_service(**service):
    session = Session()
    name = service['name']
    service_type = service['type']
    project = service['project']
    host = service['host']

    server = session.query(Server).filter(Server.host == host).scalar()
    query = session.query(Service).filter(Service.name == name, Service.type == service_type,
                                          Service.project == project, Service.server. == server.id)
    exists = session.query(query.exists()).scalar()

    if not exists:
        row = Service(name=name, type=service_type, project=project, server_id=server.id)
        row_insert(row)
    else:
        row = query.scalar()

    return row


def repo_sync(**meta):
    path = meta['repo']

    if not os.path.exists(path):
        raise FileExistsError('仓库路径不存在')

    repo = Repo(path)

    if repo.is_dirty():
        untracked_files = repo.untracked_files()
        raise Exception(f'未跟踪的文件：\n{untracked_files}')

    branch = meta['branch']
    reset = meta['reset']

    if reset:
        remote = meta['remote']
        print(repo.git.reset('--hard', remote))

    try:
        print(repo.git.checkout(branch))
        print(repo.git.pull())
    except GitCommandError as errors:
        raise errors
    else:
        print('仓库同步成功')

    def version_row():
        session = Session()
        service_id = meta['id']
        head = repo.head.object.hexsha
        versions = session.query(Version).filter(Version.service_id == service_id).order_by(desc(Version.version))
        exists = session.query(versions.exists()).scalar()

        if not exists:
            previous_hash = list(repo.iter_commits())[1]
        else:
            previous_hash = versions[0].commit_hash

        change_log = repo.git.diff(previous_hash, head)
        print(f'Commit Log: \n{change_log}')

        commit_info = repo.head.reference.commit
        author = commit_info.author.name
        email = author.email
        commit_date = datetime.fromtimestamp(commit_info.committed_date)
        message = commit_info.message
        version = ' '.join(message)[-1]
        try:
            mutable_version = [int(x) for x in version.split('.')]
            for i in mutable_version:
                if i < 0:
                    raise Exception('版本号不能为负')
        except TypeError as err:
            print('版本号格式错误')
            raise err

        row = Version(service_id=service_id, version=version, commit_hash=head, commit_author=author,
                      author_email=email, commit_date=commit_date, commit_message=message,
                      commit_log=change_log)

        row_insert(row)

        return row

    return version_row()


def build(**meta):
    compile_path = meta['compile_path']
    if not os.path.exists(compile_path):
        raise FileExistsError('编译路径不存在')

    command = meta['command']
    for c in command:
        status, result = subprocess.getstatusoutput(c)
        status = status >> 8
        print(result)

        if status > 0:
            raise SystemError('编译失败')

    archive_folder = meta['archive_folder']
    builder = os.getenv('BUILD_USER')
    dist = os.getenv('WORKSPACE')

