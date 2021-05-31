from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from model.db_connects import PG_ENGINE

# 创建对象的基类:
PgBase = declarative_base()

# 初始化数据库连接:
PgENGINE = create_engine(PG_ENGINE)
PgSESSION = scoped_session(sessionmaker(bind=PgENGINE))
