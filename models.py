#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Optional
import sqlmodel as sm
from sqlmodel import SQLModel, Session, text, Field
from sqlalchemy.ext import declarative_base

# sqlmodel table
# SQLModel 정석적인 형태
#  class Hero(SQLModel, table=True):
#      id: Optional[int] = Field(default=None, primary_key=True)
#      name: str
#      secret_name: str
#      age: Optional[int] = None


# metadata 를 일부 사용
#  class Hero(SQLModel, table=True):
#      id: Optional[int] = sm.Field(default=None, primary_key=True)
#      name: str = sm.Field(index=True)
#      age: Optional[int] = sm.Field(default=None)
#
#      # metadata
#      __tablename__: str = "departments"
#      __table_args__ = {
#          "mysql_engine": "InnoDB",
#          "extend_existing": True,  # 없으면 SAWarning 출력
#          "autoload_with": db_engine   # DB 스키마로부터 메타데이터 자동 로드
#      }
#
#  # metadata.Table 만 사용
class Hero(sm.SQLModel, table=True):
    # __table__ 사용시에는 따로 필드 지정을 할 수 없음
    # id: Optional[int] = sm.Field(default=None, primary_key=True)
    # name: str = sm.Field(index=True)
    # age: Optional[int] = sm.Field(default=None)

    # metadata
    __table__ = sm.Table(
        "departments",
        sm.SQLModel.metadata,
        sm.Column("id", sm.Integer, primary_key=True),
        sm.Column("name", sm.String(50)),
        sm.Column("age", sm.Integer, default=None),
        mysql_engine='InnoDB',
        extend_existing=True,
        autoload_with=db_engine,
    )

# sqlalchemy table
# declarative base class
Base = declarative_base()

# 선언적(declarative) 매핑: 정석적인 형태
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)

# 옵션 사용
class MyClass(Base):
    __tablename__ = 'departments'
    __table_args__ = {'mysql_engine':'InnoDB'}

# 옵션에 제약사항 사용
class MyClass(Base):
    __tablename__ = 'departments'
    __table_args__ = (
            ForeignKeyConstraint(['id'], ['remote_table.id']),
            UniqueConstraint('foo'),
            )

# 클래식 매핑: metadata(registry) 만 사용
class MyClass(Base):
    __table__ = Table('my_table', Base.metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String(50))
    )
