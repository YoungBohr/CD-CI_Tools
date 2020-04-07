# /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from typing import Any, Union

import yaml
from orm import *
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
        name = meta['name']
        repo = meta['repo']
        app_type = meta['type']
        server_address = meta['server_address']

    def app_row():
        server_id = session.query(Server.id).filter(Server.ip == server_address)
        q = session.query(App).filter(App.name == name, App.type == app_type, App.server_id == server_id)
        exists = session.query(q.exists()).scalar()
        if not exists:
            row = App(name=name, type=app_type, project=meta['project'], server_id=server_id)
            row_insert(row)
        else:
            row = q.scalar()
        return row

    if not os.path.exists(repo):
        raise FileExistsError('Repository dose not exist')

    if app_type == 'java':
        artifact = BuildWithGradle(repo, **meta)
    elif app_type == 'js':
        artifact = BuildWithNpm(repo, **meta)
    else:
        raise TypeError('Unsupport this Compilation type')

    app = app_row()

    if artifact.check():
        artifact.sync(branch=branch, reset=reset, remote=remote)

    def calculate_the_version(version, lines):
        mutable_version = [int(x) for x in version.split('.')]

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

        new_version = '.'.join(list(map(str, mutable_version)))

        return new_version

    def version_row():
        head = artifact.get_head()
        versions = session.query(Version).filter(Version.app_id == app.id).order_by(desc(Version.version))
        exists = session.query(versions.exists()).scalar()
        if not exists:
            change_log = artifact.change_log()
            lines = change_log.count('\n')
