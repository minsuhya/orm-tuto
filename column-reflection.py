from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import text

# SQLAlchemy 엔진 생성
engine = create_engine('sqlite:///mydatabase.db')

# 메타데이터 및 연결된 테이블 생성
metadata = MetaData(bind=engine)
my_table = Table('my_table', metadata, autoload=True, autoload_with=engine)

# 동적 모델 클래스 생성
Base = declarative_base()

class MyDynamicModel(Base):
    __table__ = my_table

# 세션 생성
Session = sessionmaker(bind=engine)
session = Session()

# 예제 쿼리 실행
query = session.query(MyDynamicModel).filter(MyDynamicModel.column_name == 'some_value')
result = query.all()
