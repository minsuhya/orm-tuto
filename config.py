SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://root:example@database1-db:9001/database1"
SQLALCHEMY_BINDS = {
        'db2': "postgres://postgres:example@database2-db:9002/database2",
        'db1': SQLALCHEMY_DATABASE_URI
        }
