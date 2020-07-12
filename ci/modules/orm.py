# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Table, Column, ForeignKey, Integer, DateTime, String, Text)

Base = declarative_base()

server_service = Table('association', Base.metadata,
                       Column('server_id', Integer, ForeignKey('server.id'), primary_key=True,),
                       Column('service_id', Integer, ForeignKey('service.id'), primary_key=True,)
                       )
server_publishment = Table('association', Base.metadata,
                           Column('server_id', Integer, ForeignKey('server.id')),
                           Column('publishment_id', Integer, ForeignKey('publishment.id'))
                           )


class Server(Base):
    __tablename__ = 'server'

    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=True)
    alias = Column(String(30), nullable=True)
    host = Column(String(30), nullable=False)
    domain_name = Column(String(60), nullable=True)
    ssh_port = Column(Integer, nullable=True)
    ssh_user = Column(String(30), nullable=True)
    ssh_password = Column(String(60), nullable=True)
    ssh_private_key = Column(Text, nullable=True)
    jump_host_id = Column(Integer,nullable=True)
    service = relationship('Service', secondary=server_service, back_populates='server')
    publishment = relationship('Publishment', secondary=server_publishment, back_populates='server')

    def __repr__(self):
        row = f'<Sever(name={self.name},alias={self.alias},host={self.host},domain_name={self.domain_name})>'
        return row


class Service(Base):
    __tablename__ = 'service'

    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    type = Column(String(15), nullable=False)
    project = Column(String(30), nullable=False)

    server = relationship('Server', secondary=server_service, back_populates='service')
    version = relationship('Version', backref='service')
    build = relationship('Build', backref='service')
    publishment = relationship('Publishment', backref='service')

    def __repr__(self):
        hosts = ''
        if len(self.server) > 0:
            host_list = []
            for i in iter(self.server):
                host_list.append(i.host)
            hosts = ','.join(host_list)

        row = f'<Service(name={self.name},type={self.type},project={self.project},hosts={hosts})>'
        return row


class Version(Base):
    __tablename__ = 'version'

    id = Column(Integer, primary_key=True, autoincrement=True)
    service_id = Column(Integer, ForeignKey('service.id'))
    version = Column(String(15), unique=True, nullable=False)
    date = Column(DateTime, default=datetime.now(), nullable=False)
    commit_hash = Column(String(60), nullable=False)
    commit_author = Column(String(30), nullable=False)
    author_email = Column(String(30), nullable=False)
    commit_date = Column(DateTime, nullable=False)
    commit_message = Column(String(30), nullable=False)
    commit_log = Column(Text, nullable=True)


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30), nullable=False)
    password = Column(String(30), nullable=False)
    email_address = Column(String(30), nullable=False)

    build = relationship('Build', backref='user')
    publishment = relationship('Publishment', backref='publisher')


class Build(Base):
    __tablename__ = 'build'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, default=datetime.now(), nullable=False)
    repo = Column(String(60), nullable=False)
    branch = Column(String(30), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    service_id = Column(Integer, ForeignKey('service.id'))
    version_id = Column(Integer, nullable=False)
    md5 = Column(String(32), nullable=False)
    sha1 = Column(String(40), nullable=False)
    sha512 = Column(String(128), nullable=False)

    publishment = relationship('Publishment', backref='build')


class Publishment(Base):
    __tablename__ = 'publishment'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, default=datetime.now(), nullable=False)
    service_id = Column(Integer, ForeignKey('service.id'))
    publisher_id = Column(Integer, ForeignKey('user.id'))
    build_id = Column(Integer, ForeignKey('build.id'))
    result = Column(String(10), nullable=True)

    server = relationship('Server', secondary=server_publishment, back_populates='publishment')
