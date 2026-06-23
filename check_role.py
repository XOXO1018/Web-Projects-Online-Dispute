import pymysql
conn = pymysql.connect(host='localhost', user='root', password='lzz1212147474', database='zjfl', charset='utf8mb4')
cur = conn.cursor()
cur.execute('SHOW COLUMNS FROM users WHERE Field = "role"')
result = cur.fetchone()
print('Role column definition:', result)
conn.close()
