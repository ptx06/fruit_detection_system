import pymysql

# 数据库连接信息
HOST = 'localhost'
USER = 'root'
PASSWORD = 'my142857SQL@&'
DATABASE = 'fruit_system'

# 连接数据库
conn = pymysql.connect(
    host=HOST,
    user=USER,
    password=PASSWORD,
    database=DATABASE,
    charset='utf8mb4'
)

# 创建游标
cursor = conn.cursor()

try:
    # 添加 bio 字段
    cursor.execute("ALTER TABLE users ADD COLUMN bio TEXT NULL DEFAULT NULL")
    print("添加 bio 字段成功")
    
    # 添加 avatar 字段
    cursor.execute("ALTER TABLE users ADD COLUMN avatar VARCHAR(255) NULL DEFAULT NULL")
    print("添加 avatar 字段成功")
    
    # 提交事务
    conn.commit()
    print("事务提交成功")
except Exception as e:
    print(f"执行失败: {e}")
    # 回滚事务
    conn.rollback()
finally:
    # 关闭游标和连接
    cursor.close()
    conn.close()
    print("数据库连接已关闭")