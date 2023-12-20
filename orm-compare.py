#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Optional
from urllib.parse import quote_plus
from sqlalchemy import create_engine
import sqlmodel as sm
from sqlmodel import SQLModel, Session, text, Field
from sqlalchemy.orm import Session as OrmSession
from pydantic import BaseModel
from sqlalchemy.orm import declarative_base # 1.4
#  from sqlalchemy.orm import DeclarativeBase # 2.0
from sqlalchemy import Table, select

# db connection info
db_string = "mysql+pymysql://{}:{}@{}:{}/{}".format("rupi", quote_plus("rupi@@1234"), "localhost", "33062", "rupi_db")
db_engine = create_engine(db_string, echo=True)

# Base
Base = declarative_base()
Base.metadata.reflect(db_engine)
#  class Departments(Base):
    #  __table__ = Table('departments', Base.metadata, autoload=True, autoload_with=db_engine)

Base.metadata.reflect(db_engine)

class Departments(Base):
    __table__ = Base.metadata.tables["departments"]

def main():
    # db connection

    # create db session
    with db_engine.connect() as conn:
        result = conn.execute(text("select * from departments"))
        #  result = conn.execute("select version()")
        print(result.all())

    # sqlmodel - create db session
    with Session(db_engine) as session:
        statement = text("select * from departments")
        result = session.exec(statement)
        print("sqlmodel: ", result.fetchall())

    # sqlalchemy - create db session
    with OrmSession(db_engine) as session:
        result = session.execute(text("select * from departments"))
        print("sqlalchemy: ", result.fetchall())

        row = session.execute(select(Departments)).first()
        print(row)




if __name__ == "__main__":
    main()
