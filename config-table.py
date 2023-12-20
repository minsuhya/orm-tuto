#!/usr/bin/env python
# -*- coding: utf-8 -*-

# config table - sqlalchemy with reflect
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Table, select
from sqlalchemy.orm import Session as OrmSession

# db connection info
db_string = "mysql+pymysql://{}:{}@{}:{}/{}".format("rupi",
                                                    quote_plus("rupi@@1234"),
                                                    "localhost", "33062",
                                                    "rupi_db")
db_engine = create_engine(db_string, echo=True)

Base = declarative_base()
Base.metadata.reflect(db_engine)


class Departments(Base):
    __table__ = Base.metadata.tables["departments"]


with OrmSession(db_engine) as session:
    result = session.execute("select * from departments")
    print("sqlalchemy: ", result.fetchall())

    department = session.execute(select(Departments)).first()
    print(department[0].name, department[0].id, department[0].priority)
