# /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from typing import Any, Union

import yaml
from orm import *
from hash import *
from build import *
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

engine = create_engine('mysql+mysqldb://tta:tta2020@mysql.nextlord.com:3306/devops?charset=utf8', encoding='utf-8')
Session = sessionmaker(bind=engine)


def row_insert(row):
    session = Session()
    session.add(row)
    session.commit()
    session.close()


def build(config):
    session = Session()

    if not os.path.exists(config):
        raise FileExistsError

    with open(config, 'r', encoding="utf-8") as data:
        meta = yaml.load(data)
        repo = meta['repo']
        app_type = meta['type']
        server_address = meta['server_address']

    def app_row():
        name = meta['name']
        project = meta['project']

        server = session.query(Server).filter(Server.ip == server_address).scalar()
        q = session.query(App).filter(App.name == name, App.type == app_type,
                                      App.project == project, App.server_id == server.id)
        exists = session.query(q.exists()).scalar()
        if not exists:
            row = App(name=name, type=app_type, project=project, server_id=server.id)
            row_insert(row)
        else:
            row = q.scalar()
        return row

    if not os.path.exists(repo):
        raise FileExistsError('Repository dose not exist')

    if app_type == 'java':
        artifact = BuildWithGradle(repo, **meta)
    elif app_type == 'js':
        artifact = NpmBuild(repo, **meta)
    else:
        raise TypeError('Unsupport this Compilation type')

    app = app_row()

    if artifact.check():
        artifact.sync(branch=branch, reset=reset, remote=remote)

    def calculate_the_version():
        head = artifact.get_head()
        versions = session.query(Version).filter(Version.app_id == app.id).order_by(desc(Version.version))

        exists = session.query(versions.exists()).scalar()
        if not exists:
            change_log = artifact.change_log()
            previous_version = meta['version']
        else:
            previous_commit_hash = versions[0].commit_hash
            previous_version = versions[0].version

            if head == previous_commit_hash:
                return versions[0].version
            else:
                change_log = artifact.change_log(previous_commit_hash)

        print(f'Commit Log: \n{change_log}')

        lines = change_log.count('\n')
        mutable_version = [int(x) for x in previous_version.split('.')]

        quotient = lines // 36
        if quotient < 2:
            mutable_version[2] = mutable_version[2] + 1
        elif quotient >= 2:
            mutable_version[2] = mutable_version[2] + quotient

        quotient2 = mutable_version[2] // 27
        if quotient2 > 0:
            mutable_version[2] = mutable_version[2] % 27
            mutable_version[1] = mutable_version[1] + quotient2

        quotient3 = mutable_version[1] // 18
        if quotient3 > 0:
            mutable_version[1] = mutable_version[1] % 18
            mutable_version[0] = mutable_version[0] + quotient3

        current_version = '.'.join(list(map(str, mutable_version)))
        commit_info = artifact.committer()
        row = Version(app_id=app.id, version=current_version, commit_hash=head, commit_author=commit_info[0],
                      committer_email=commit_info[1], commit_date=commit_info[2], commit_message=commit_info[3],
                      commit_log=change_log)
        row_insert(row)

        return current_version

    version = calculate_the_version()
    meta['version'] = version
    meta['id'] = app.id

    user_name = os.environ.get('BUILD_USER')
    user_id = session.query(User).filter(User.name == user_name).scalar().real

    dist = os.environ.get('WORKSPACE')
    artifact.build()
    archive_path = artifact.pack(dist, version)
    md5, sha1, sha512 = checksum(archive_path)

    build_row = Build(repo=repo, user_id=user_id, app_id=app.id, branch=branch,
                      version=version, md5=md5, sha1=sha1, sha512=sha512)
    row_insert(build_row)

    with open(config, 'r+', encoding="utf-8") as data:
        yaml.dump(meta, data)
