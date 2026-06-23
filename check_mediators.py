import pymysql
conn = pymysql.connect(host='localhost', user='root', password='lzz1212147474', database='zjfl', charset='utf8mb4')
cur = conn.cursor()

# 检查所有调解员记录
cur.execute('SELECT u.id, u.email, m.name, m.specialty FROM users u JOIN mediators m ON u.id = m.user_id')
print('All mediators:')
for row in cur.fetchall():
    print(f'  ID: {row[0]}, Email: {row[1]}, Name: {row[2]}, Specialty: {row[3]}')

# 检查 mediator 角色的用户
cur.execute('SELECT id, email, real_name, role FROM users WHERE role = "mediator"')
print()
print('Users with mediator role:')
for row in cur.fetchall():
    print(f'  UserID: {row[0]}, Email: {row[1]}, Name: {row[2]}, Role: {row[3]}')

conn.close()
