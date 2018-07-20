# coding=utf-8
import base64
import hashlib

from sqlalchemy import (Column, ForeignKey, Integer, MetaData, String, Table,
                        create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .dormitory import Dormitory
from .ecard import Ecard
from .edu_manage import EduManage
from .ehall import Ehall
from .lib import Lib
from .logistics import Logistics
from .meol import Meol


class_set = [Dormitory, Ecard, Ehall, Lib, Logistics, Meol, EduManage]
Base = declarative_base()
db_name = 'cookies_cache.db'


class SDUT(object):
    @classmethod
    def get_ehall(self, user_id, password):
        user = get_user(user_id, password)
        if user:
            ehall = Ehall(user.cookies)
            # 使用空密码进行登录，如果 cookies 有效则不会校验，否则说明 cookies 失效
            ehall.login('-', '-')
            if ehall.logined:
                return ehall
        ehall = Ehall()
        ehall.login(user_id, password)
        if ehall.logined:
            save_user(user_id, password, ehall.cookies)
            return ehall
        return None

    @classmethod
    def get_object(self, clas, user_id, password):
        assert clas in class_set
        ehall = self.get_ehall(user_id, password)
        if not ehall:
            return None
        if clas.__name__ == 'Ehall':
            return ehall
        obj = clas(ehall)
        return obj if obj.logined else None


class User(Base):
    __tablename__ = 'user'

    user_id = Column(String(64), primary_key=True)
    password = Column(String(128))
    cookies = Column(String(1024))


def save_user(user_id, password, cookies):
    """ 将 cookies 信息存入数据库 """
    engine = create_engine('sqlite:///{db_name}'.format(db_name=db_name))

    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    user = get_user(user_id, password)
    if user:
        # 若用户已存在，则更新数据
        user = session.query(User).filter(User.user_id == user_id).one()
        user.cookies = cookies
        session.flush()
    elif get_user_by_id(user_id):
        # 若用户已存在，但密码不同, 则更新密码
        user = session.query(User).filter(User.user_id == user_id).one()
        user.password = passwd_encode(password)
        user.cookies = cookies
        session.flush()
    else:
        # 否则创建用户数据
        new_user = User(user_id=user_id, password=passwd_encode(
            password), cookies=cookies)
        session.add(new_user)

    session.commit()
    session.close()


def get_user_by_id(user_id):
    """ 通过 user_id 查找用户信息 """
    engine = create_engine('sqlite:///{db_name}'.format(db_name=db_name))

    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    user = session.query(User).filter(User.user_id == user_id).all()
    session.close()

    if not user:
        return None
    user = user[0]

    return user


def get_user(user_id, password):
    """ 从数据库查询指定用户的信息 """
    engine = create_engine('sqlite:///{db_name}'.format(db_name=db_name))

    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    user = session.query(User).filter(User.user_id == user_id).all()
    session.close()

    if not user:
        return None
    user = user[0]

    if user.password == passwd_encode(password):
        return user
    return None


def get_user_list():
    """ 从数据库查询所有用户的信息 """
    engine = create_engine('sqlite:///{db_name}'.format(db_name=db_name))

    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    user = session.query(User).all()
    session.close()

    return user


def create_db():
    """ 创建数据库文件 """
    engine = create_engine('sqlite:///{db_name}'.format(db_name=db_name))
    metadata = MetaData(engine)
    user_table = Table(
        'user', metadata,
        Column('user_id', String(64), primary_key=True),
        Column('password', String(128)),
        Column('cookies', String(1024))
    )
    user_table
    metadata.create_all()


def passwd_encode(data):
    """ 密码加密 """
    if isinstance(data, str):
        data = base64.b64encode(data.encode('utf-8'))
    m = hashlib.md5()
    m.update(data)
    return m.hexdigest()
