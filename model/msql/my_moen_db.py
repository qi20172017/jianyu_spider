from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from model.db_connects import MYSQL_ENGINE

# 创建对象的基类:
MyBase = declarative_base()

# 初始化数据库连接:
MyENGINE = create_engine(MYSQL_ENGINE)
MySESSION = scoped_session(sessionmaker(bind=MyENGINE))
