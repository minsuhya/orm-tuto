#!/usr/bin/env python
# -*- coding: utf-8 -*-

# sqlalchemy 2.0 Future Style

# 1) 모델 선언

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'user_account'
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    fullname = Column(String(50))

    addresses = relationship("Address",
                             back_populates="user",
                             cascade="all, delete-orphan")

    def __repr__(self):
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r}"


class Address(Base):
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)
    email_address = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey('user_account.id'), nullable=False)

    user = relationship("User", back_populates="addresses")

    def __repr__(self):
        return f"Address(id={self.id!r}, email_address={self.email_address!r})"


# 2) DB 연결
# connection url 사용, create_engine() 함수 사용, future=True 옵션 사용

from urllib.parse import quote_plus as urlquote

from sqlalchemy import create_engine

db_string = f"mysql+pymysql://rupi:{urlquote('rupi@@1234')}@localhost:33062/rupi_db"
engine = create_engine(db_string, future=True, echo=True)

# 3) 테이블 생성 (DDL)

# create_all() 함수 사용: Base.metadata.create_all(engine)
# Base 기반으로 선언한 모델들을 DB에 실체화 수행
# 테이블, 시퀀스 등의 DB 모델 생성
# 반대로, drop_all() 함수 사용: Base.metadata.drop_all(engine)

Base.metadata.create_all(engine)

# 4) 데이터 개체 생성 및 저장: Session 객체 사용

## Session 객체 생성
## Session 객체의 add() 메서드로 개체 추가
## 트랜잭션 관리를 위해 with 구문 사용

from sqlalchemy.orm import Session

with Session(engine) as session:

    # new users
    spongebob = User(name="spongebob",
                     fullname="Spongebob Squarepants",
                     addresses=[Address(email_address="sample@gmail.com")])
    sandy = User(name="sandy",
                 fullname="Sandy Cheeks",
                 addresses=[
                     Address(email_address="sandy@sqlalchemy.org"),
                     Address(email_address="sandy@squirrelpower.org")
                 ])
    patrick = User(name="patrick", fullname="Patrick Star")

    # insert & commit - 처음 생성하고 주석처리
    #  session.add_all([spongebob, sandy, patrick])
    #  session.commit()

# 5) 간단한 질의(select)

#  ScalarResult 는 Row 를 yield 하는 generator
#  #  FilterResult 베이스로 ScalarResult, MappingResult, AsyncResult 있음
#  #  값을 얻으려면 all, one, first 등을 쓰던지, loop 구문 사용
#  #  scalars( stmt ) 는 stmt.scalars() 와 같음
#  select 로 질의 대상 지정, where 로 filter 조건 적용
#  #  조건절에 SQL 에 대응하는 다양한 컬럼 연산자 사용

from sqlalchemy import select

session = Session(engine)

# where 조건절, in_ 컬럼 연산자 사용
stmt = select(User).where(User.name.in_(["sandy", "patrick"]))

# ScalarResult: Generator[Row]
for user in session.scalars(stmt):
    print(user)

# 6) JOIN 질의

#  선언된 모델 Address 의 relationship 을 사용해 JOIN 가능
#  #  JOIN 의 on 조건을 relationship 설정에서 불러옴
#  #  또는 직접 JOIN 대상 모델(class)을 지정할 수도 있음
#  #  ex) query(Address).join(User, User.id==Address.user_id)
#  where 조건절은 여러번 반복 가능 (and_ 결합)

stmt = (select(Address).join(
    Address.user).where(Address.email_address == "sandy@sqlalchemy.org"))
sandy_address = session.scalars(stmt).one_or_none()

print("fetchOne():", sandy_address)

# 7) insert, update, delete

#  Model 에 의해 insert, update 변경 사항이 추적된다
#  #  execution 대기열에 저장했다가 commit 할 때 실행됨
#  #  cf. SQLModel 의 경우엔 session.add() 로 명시해야 함

stmt = select(User).where(User.name == "patrick")
patrick = session.scalars(stmt).one()

# insert: Address 생성
patrick.addresses.append(Address(email_address="patrickstar@sqlalchemy.org"))

# update: Address.email_address 값 변경
sandy_address.email_address = "sandy@sqlalchemy.org"

session.commit()

# 8) delete, flush

#  session 에서 Pk 값으로 직접 가져오기
#  Model 에서 remove 되면 delete stmt 로 실행 대기줄에 추가
#  #  cf. session.delete: 직접적으로 delete stmt 추가

#  flush 는 DB transaction 에 전달만 한 상태 (persist 이전 단계)

#  flush 는 commit 이 아님 (commit 의 부분 동작)
#  #  select 한 경우, 자신의 transaction 에는 변경 상태로 읽히지만
#  #  다른 transaction 에는 해당 안됨
#  commit 할 때, flush 상태의 변경들도 함께 commit 됨
#  autoflush 옵션 적용시에는 사용할 필요가 없다

# 한번 삭제 테스트 완료 후 주석처리
#  sandy = session.get(User, 2)  # pk 값으로 가져오기
#  sandy.addresses.remove(sandy_address)
#  session.flush()
#  session.delete(patrick)
#  session.commit()

# 9) scalars 질의
# 앞의 7) 단계에서 삭제한 sandy_address 삭제 확인

stmt = (select(Address).join(Address.user).where(User.name == 'sandy').where(
    Address.email_address == 'sandy@sqlalchemy.org'))
sandy_address = session.scalars(stmt).one_or_none()
print(sandy_address)
