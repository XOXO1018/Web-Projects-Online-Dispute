import pymysql

conn = pymysql.connect(
    host='localhost', port=3306, user='root',
    password='lzz1212147474', database='zjfl',
    charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
)
cur = conn.cursor()
cur.execute(
    "ALTER TABLE users MODIFY COLUMN role "
    "ENUM('platform_admin','enterprise_admin','enterprise_user','mediator','translator','analyst') "
    "NOT NULL DEFAULT 'enterprise_admin'"
)
conn.commit()
print('OK - role enum updated')

cur.execute('SHOW COLUMNS FROM users WHERE Field=%s', ('role',))
print(cur.fetchone())

cur.close()
conn.close()
