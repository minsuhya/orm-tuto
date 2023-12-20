#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, jsonify, abort, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class TAB1(db.Model):
    __bind_key__ = 'db1'
    __tablename__ = 'rupi_tbl_db1'
    __table_args__ = {
        'autoload': True,
        # 'autoload_with': db.engine
        'autoload_with': db.get_engine(bind="db1")
    }

class TAB2(db.Model):
    __bind_key__ = 'db2'
    __tablename__ = 'rupi_tbl_db2'

    __table_args__ = {
        'autoload': True,
        # 'autoload_with': db.engine
        'autoload_with': db.get_engine(bind="db2")
    }
