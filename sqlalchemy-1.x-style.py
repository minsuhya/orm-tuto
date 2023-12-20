#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 1) DB 연결
from urllib.parse import quote_plus as urlquote

from sqlalchemy import create_engine

db_string = f"mysql+pymysql://rupi:{urlquote('rupi@@1234')}@localhost:33062/rupi_db"
engine = create_engine(db_string, future=True, echo=True)

# 2) Model 선언
# Base 기반으로 Model(class) 선언도 동일

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# Base 기반으로 Model(class) 선언
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    fullname = Column(String(50), nullable=False)
    nickname = Column(String(50), nullable=False)

    def __repr__(self):
        return f"User(id={self.id}, name={self.name}, fullname={self.fullname}, nickname={self.nickname})"


print(User.__table__)

# 3) 선언한 모든 Table 생성

Base.metadata.create_all(engine)

# 4) User 데이터 생성

ed_user = User(name='ed', fullname='Ed Jones', nickname='edsnickname')
print(ed_user.name)
print(ed_user.nickname)

# 5) Session 생성

#  2단계: sessionmaker 팩토리로부터 Session 생성자와 session 개체 생성
#  cf. Future 스타일에서는 바로 Session 통해 session 생성

from sqlalchemy.orm import sessionmaker

# factory
Session = sessionmaker(bind=engine)
# session
session = Session()

# sqlalchemy.orm.session.Session
print(type(session))
print(session)  # Session instance

# 6) Session을 통해 데이터 추가 (insert, update, autoflush, expire_on_commit[default=True])

#  User(ed) 에 대한 변경사항들이 select(User) 이벤트 때 flush(적용) 됨
#  #  autoflush: 명시적으로 flush/commit 안해도 발생 (Session 옵션)
#  commit 이후 User 모델의 instance 에 대해 refresh 실행됨
#  #  commit 이전의 User(ed) 의 id 는 None
#  #  commit 이후의 User(ed) 에 id 값이 채워져 있음 (refresh)
#  Session 의 옵션 expire_on_commit = True 에 의해 자동 refresh

# ed_user.id = None
ed_user = User(name='ed', fullname='Ed Jones', nickname='edsnickname')
print(f"HEAD: new User[id={ed_user.id}]:", ed_user)

session.add(ed_user)  # pending 상태

# select User 이벤트에 flush 발생
first_user = session.query(User).filter_by(name='ed').first()
print(f"first_user[id={first_user.id}]:", first_user)

from sqlalchemy import text

query = text("SELECT * FROM users WHERE name=:name_1")

# sqlalchemy.engine.result.ScalarResult
results = session.execute(query, {"name_1": "ed"}).scalars()
print("scalars() = ScalarResult:", type(results), results)

user_ids = results.all()  # 두번 호출 불가(임시 데이터라 fetch 이후 사라짐)
print("scalars().all():", type(user_ids), user_ids)

results = session.query(User).filter_by(name='ed').all()
print("all():", type(results), results)

last_user = results[-1]
print(f"last_user[id={last_user.id}]:", last_user)

# refresh 가 자동으로 수행됨(expire_on_commit=True)
print(f"TAIL: new User[id={ed_user.id}]:", ed_user)

assert ed_user is last_user, "ed is instance before insert, last is instance after insert"

# 7) scalars() 와 all() 의 차이

#  scalars() : ScalarResult 생성
#  #  값을 얻으려면 all() 사용
#  #  1번만 (호출) 가져올 수 있다 (제너레이터 방식)

#  all() : MapResult 를 이용해 List[Any] 생성
#  #  1번만 호출 가능한 것은 동일
#  cf. scalar() vs one()
#  #  scalar() 한 행의 첫 컬럼만
#  #  one() 한 행만 가져오기
#  왜 Scalar 가 필요한지 이유는 Result 의 fetch 과정을 단축하기 위해서가 아닌가 짐작해본다
#  가령, 컬럼 개수만큼 loop 문이 skip 된다던지.

from sqlalchemy import text

query = text("SELECT * FROM users WHERE name=:name_1")

# sqlalchemy.engine.result.ScalarResult
# 첫번째 컬럼값만 가져와 scalars 생성
results = session.execute(query, {"name_1": 'ed'}).scalars()
user_id = results.all()  # all을 두번 호출하면 에러
print("scalars().all():", user_ids)

# List
results = session.execute(query, {"name_1": 'ed'}).all()
print("scalars() = ScalarResult:", type(results), results)

last_user = results[-1]
print(f"last_user[id={last_user.id}]:", User(**last_user))

# 8) 변경된 객체의 상태 변화

#  change 이벤트 발생시
#  #  update 변경 객체는 transient 상태가 되고 (session.dirty)
#  #  insert 생성 객체는 pending 상태로 추가됨 (session.new)
#  commit 이벤트 발생시
#  #  session 의 dirty/new 변경들이 DB 에 저장되고
#  #  transient/pending 상태 객체들은 persistent 상태로 바뀐다

##############################
##  “object states” - transient, pending, and persistent
##

session.add_all([
    User(name='wendy', fullname='Wendy Williams', nickname='windy'),
    User(name='mary', fullname='Mary Contrary', nickname='mary'),
    User(name='fred', fullname='Fred Flintstone', nickname='freddy')
])

ed_user.nickname = 'eddie'
print(f"before commit: ed_user[{ed_user.id}]:", ed_user)
# before commit: ed_user[13]: <User(name='ed', fullname='Ed Jones', nickname='eddie')>

# transient => UPDATE
print("dirty:", session.dirty)
# dirty: IdentitySet([<User(name='ed', fullname='Ed Jones', nickname='eddie')>])

# pending => INSERT
print("pending:", session.new)
# pending: IdentitySet([
# <User(name='wendy', fullname='Wendy Williams', nickname='windy')>,
# <User(name='mary', fullname='Mary Contrary', nickname='mary')>,
# <User(name='fred', fullname='Fred Flintstone', nickname='freddy')>
# ])

# persistent
session.commit()  # flush

print(f"after commit: ed_user[{ed_user.id}]:", ed_user)
# after commit: ed_user[13]: <User(name='ed', fullname='Ed Jones', nickname='eddie')>

# 9) filter 조건절과 컬럼 연산자
# where 조건절에 filter 사용 (Future 스타일과 동일)
##############################
##  ColumnOperator: and, or
##

from sqlalchemy import and_, or_

session.query(User).filter(and_(User.name == "ed", User.id > 1)).delete()
session.commit()

# 10) 트랜잭션의 롤백 (변경 취소)
#  rollback: 이전 commit 상태로 되돌리기
#  session 에 fake_user 변경(생성) 내용이 없어짐
#  session.new 비워짐
##############################
##  Rolling Back
##

# transient: update
ed_user.name = 'Edwardo'
print("before rollback:", ed_user.name)
# before rollback: Edwardo

# new user
fake_user = User(name='fakeuser', fullname='Invalid', nickname='12345')
# pending: insert
session.add(fake_user)

# flush and select
session.query(User).filter(User.name.in_(['Edwardo', 'fakeuser'])).all()

# rollback
session.rollback()

# recovery before rollback
print("after rollback:", ed_user.name)
# after rollback: ed

assert fake_user not in session, "fake_user must be absent"
# pass

session.query(User).filter(User.name.in_(['ed', 'fakeuser'])).all()
# name='ed' 만 출력

#  11) 별칭(alias) 사용한 질의
##############################
##  Querying
##

# cast class
for instance in session.query(User).order_by(User.id):
    print(instance.name, instance.fullname)

# unpack Result
for name, fullname in session.query(User.name, User.fullname):
    print(name, fullname)

# MappingResult{ User, name }
for row in session.query(User, User.name).all():
    print(row.User, row.name)

from sqlalchemy.orm import aliased

user_alias = aliased(User, name='user_alias')
print(type(user_alias), user_alias)

for row in session.query(user_alias, user_alias.name).all():
    print(row.user_alias)

# SELECT user_alias.*, user_alias.name AS user_alias_name__1
# FROM users AS user_alias

#  참고: 컬럼 alias 는 label 사용
#  employees = db.session.query(
#  EmployeeModel.id,
#  EmployeeModel.name.label(
#  "emp_name")  #we are using emp_name alias for column name
#  ).filter(EmployeeModel.department == 'finance').all()
#
#  result = db.session.query(
#  SubjectModel.name,
#  func.sum(SubjectModel.score).label("total_score")).filter(
#  SubjectModel.name == 'Math').group_by(SubjectModel.name).all()

#  참고: with 절 CTE 사용 (Common Table Expression)
#  2.0 스타일 Subqueries and CTEs
#  1.x 스타일 CTE
#  """
#  WITH anon_1 AS
#  (INSERT INTO t (c1, c2) VALUES (:param_1, :param_2))
#  SELECT t.c1, t.c2
#  FROM t
#  """
#
#  #  insert 한 후 select 출력하기
#
#  from sqlalchemy import table, column, select
#  t = table('t', column('c1'), column('c2'))
#
#  ins = t.insert().values({"c1": "x", "c2": "y"}).cte()
#
#  stmt = select(t).add_cte(ins)

# 12) 컬럼 연산자를 이용한 query
#  Result 슬라이스 [1:3] : offset() 과 limit() 를 사용할 수도 있음
#  filter_by() vs filter()
#  #  filter 가 더 범용적임 (query 의 모든 컬럼을 대상으로 사용)
#  컬럼 연산자: DB 의 where 조건절 연산자에 해당
#  #  eq_, neq_, gt_, lt_ 등의 산술연산 조건
#  #  like, ilike, match(contains) 문자열 매칭 조건
#  #  in_ 등의 집합연산 조건
##############################
##  Column Operators
##

# offset & limit
for u in session.query(User).order_by(User.id)[1:3]:
    print(u)

# filter_by: query 의 class 의 fields 기준으로 컬럼 매핑
for name, in session.query(User.name).filter_by(fullname='Ed Jones'):
    print(name)

# filter: 기준 class 없이 컬럼 매핑 (Subquery 등에도 이용)
for name, in session.query(User.name).filter(User.fullname == 'Ed Jones'):
    print(name)

# multi filters 는 and_ 관계와 동일
for user in session.query(User).\
         filter(User.name=='ed').\
         filter(User.fullname=='Ed Jones'):
    print(user)

# 그 밖에 컬럼 연산자들..
#
# eq_: query.filter(User.name == 'ed')
# neq_: query.filter(User.name != 'ed')
# LIKE: query.filter(User.name.like('%ed%'))
# case-insensitive LIKE: query.filter(User.name.ilike('%ed%'))

# in_: query.filter(User.name.in_(['ed', 'wendy', 'jack']))
# match (=contains): query.filter(User.name.match('wendy'))

# works with query objects too:
query.filter(
    User.name.in_(session.query(User.name).filter(User.name.like('%ed%'))))

# use tuple_() for composite (multi-column) queries
from sqlalchemy import tuple_

query.filter(
    tuple_(User.name, User.nickname).\
    in_([('ed', 'edsnickname'), ('wendy', 'windy')])
)

# 13) 결과 읽어오기: all, first, one, scalar
#  empty 결과에 대해 Error 피하려면 one_or_none() 사용
##############################
##  Returning Lists and Scalars
##

# List[User]
query = session.query(User).filter(User.name.like('%ed')).order_by(User.id)
query.all()

# resultset[0]
query.first()

# 1 row or empty
user = query.filter(User.id == 99).one()  # Error
user = query.filter(User.id == 99).one_or_none()

# scalar: one()[0]
query = session.query(User.id).filter(User.name == 'ed').\
   order_by(User.id)
query.scalar()

#  14) SQL 문장 활용하기
#  session.query 의 일부분으로 사용하거나
#  from_statement 로 SQL 문장 전체를 정의할 수 있음
#  params 으로 파라미터 설정
##############################
##  Using Textual SQL (Literal strings)
##

from sqlalchemy import text

for user in session.query(User).\
            filter(text("id<224")).\
            order_by(text("id")).all():
    print(user.name)

# 조건문 일부만 사용
session.query(User).filter(text("id<:value and name=:name")).\
    params(value=224, name='fred').order_by(User.id).one()

session.query(User).from_statement(
    text("SELECT * FROM users where name=:name")).params(name='ed').all()

stmt = text("SELECT name, id, fullname, nickname "
            "FROM users where name=:name")
stmt = stmt.columns(User.name, User.id, User.fullname, User.nickname)
session.query(User).from_statement(stmt).params(name='ed').all()

#  15) Counting 함수
#  func.count 외에도 sum, avg, max, min 등 …
##############################
##  Counting
##

session.query(User).filter(User.name.like('%ed')).count()

from sqlalchemy import func

session.query(func.count(User.name), User.name).group_by(User.name).all()

session.query(func.count('*')).select_from(User).scalar()
session.query(func.count(User.id)).scalar()

#  16) Relationship 정의 (JOIN)
#  User 모델의 하위로 EmailAddress 모델 정의
#  User.emails
#  EmailAddress.user => User.emails
##############################
##  Building a Relationship
##

from sqlalchemy import ForeignKey, Table, MetaData
from sqlalchemy.orm import relationship

# Base.metadata.clear()


class EmailAddress(Base):
    __tablename__ = 'email_addresses'
    id = Column(Integer, primary_key=True)
    email = Column(String(50), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="emails")

    __table_args__ = {"extend_existing": True}

    def __repr__(self):
        return "<EmailAddress(email='%s')>" % self.email


User.emails = relationship("EmailAddress",
                           order_by=EmailAddress.id,
                           back_populates="user")

# 17) JOIN 테이블 생성
##############################
##  create JOIN relation table
##
"""
CREATE TABLE email_addresses (
  id INTEGER NOT NULL AUTO_INCREMENT, 
  email VARCHAR(50) NOT NULL, 
  user_id INTEGER, 
  PRIMARY KEY (id), 
  FOREIGN KEY(user_id) REFERENCES users (id)
)
"""

Base.metadata.create_all(engine)

for k in Base.metadata.tables:
    print(k)

#  18) 개별 또는 전체 테이블 제거(drop)
#  전체 제거: metadata.drop_all(engine)
#  개별 제거: metadata.tables[ ‘{테이블 이름}’ ].drop(engine)
##############################
##  drop, drop_all
##

# Base 로 선언된 모든 테이블
for k in Base.metadata.tables:
    print(k, type(Base.metadata.tables[k]))

# drop users table
user_table = Base.metadata.tables['users']
print(user_table, user_table.columns.keys())
# user_table.drop(engine, checkFirst=True)

# drop email_addresses table
email_table = Base.metadata.tables['email_addresses']
print(email_table, email_table.columns.keys())
# email_table.drop(engine, checkFirst=True)

# create_all 은 생성, drop_all 은 제거
Base.metadata.drop_all(engine,
                       tables=[user_table, email_table],
                       checkfirst=True)

# DROP TABLE email_addresses
# DROP TABLE users

#  19) JOIN 데이터 insert
##############################
##  Working with Related Objects
##

jack = User(name='jack', fullname='Jack Bean', nickname='gjffdd')
print(jack.addresses)

jack.addresses = [
    Address(email_address='jack@google.com'),
    Address(email_address='j25@yahoo.com')
]

session.add(jack)
session.commit()

jack = session.query(User).filter_by(name='jack').one()
print(jack.id, jack.addresses)

#  20) JOIN 질의
##############################
##  Querying with Joins
##

for u, a in session.query(User, Address).\
                    filter(User.id==Address.user_id).\
                    filter(Address.email_address=='jack@google.com').\
                    all():
    print(u)
    print('\t', a)


session.query(User).join(Address).\
        filter(Address.email_address=='jack@google.com').\
        all()

# query.join(Address, User.id==Address.user_id)          # explicit condition
# query.join(User.addresses)                             # specify relationship from left to right
# query.join(Address, User.addresses)                    # same, with explicit target
# query.join(User.addresses.and_(Address.name != 'foo')) # use relationship + additional ON criteria

# query.outerjoin(User.addresses)   # LEFT OUTER JOIN

#  21) 서브 쿼리, 라벨(as 키워드)
#  서브 쿼리: subquery
#  subquery alias: aliased
#  컬럼 alias: label
##############################
##  Using Subqueries
##

from sqlalchemy.sql import func
stmt = session.query(Address.user_id, func.count('*').\
        label('address_count')).\
        group_by(Address.user_id).subquery()

for u, count in session.query(User, stmt.c.address_count).\
    outerjoin(stmt, User.id==stmt.c.user_id).order_by(User.id):
    print(u, count)


stmt = session.query(Address).\
                filter(Address.email_address != 'j25@yahoo.com').\
                subquery()
addr_alias = aliased(Address, stmt)
for user, address in session.query(User, addr_alias).\
        join(addr_alias, User.addresses):
    print(user)
    print(address)

#  22) exists 조건 사용
##############################
##  Using EXISTS
##  - any, has
##

from sqlalchemy.sql import exists

stmt = exists().where(Address.user_id == User.id)
for name, in session.query(User.name).filter(stmt):
    print(name)

for name, in session.query(User.name).\
        filter(User.addresses.any()):
    print(name)

#  23) 삭제
##############################
##  Deleting
##

session.delete(jack)
session.query(User).filter_by(name='jack').count()

session.query(Address).filter(
    Address.email_address.in_(['jack@google.com', 'j25@yahoo.com'])).count()

#  24) Delete, 캐스케이드 삭제
##############################
##  Configuring delete/delete-orphan Cascade
##

session.close()

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    pass


class Address(Base):
    __tablename__ = 'addresses'
    pass


jack = session.get(User, 5)

del jack.addresses[1]

session.query(Address).filter(
    Address.email_address.in_(['jack@google.com', 'j25@yahoo.com'])).count()

session.delete(jack)

session.query(User).filter_by(name='jack').count()

session.query(Address).filter(
    Address.email_address.in_(['jack@google.com', 'j25@yahoo.com'])).count()
