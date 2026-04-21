from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from urllib.parse import quote_plus   # 新增导入

# MySQL 配置（请根据你的实际情况修改用户名、密码、主机、端口）
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "my142857SQL@&")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "fruit_system")

# 对用户名和密码进行 URL 编码，处理特殊字符
encoded_user = quote_plus(MYSQL_USER)
encoded_password = quote_plus(MYSQL_PASSWORD)

DATABASE_URL = f"mysql+pymysql://{encoded_user}:{encoded_password}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"

# engine = create_engine(DATABASE_URL, pool_pre_ping=True)
engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=True)  # 开启 SQL 语句回显
print(f"Connected to database: {engine.url}")  # 打印实际连接信息
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()