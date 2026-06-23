import pymysql
conn = pymysql.connect(host='localhost', user='root', password='lzz1212147474', database='zjfl', charset='utf8mb4')
cur = conn.cursor()

# 查看当前用户角色
print('Current users:')
cur.execute('SELECT u.id, u.email, u.real_name, m.specialty, u.role FROM users u LEFT JOIN mediators m ON u.id = m.user_id')
for row in cur.fetchall():
    print(f'  ID: {row[0]}, Email: {row[1]}, Name: {row[2]}, Specialty: {row[3]}, Role: {row[4]}')

print()

# 根据 specialty 更新用户角色
role_mapping = {
    '法学': 'mediator',
    '商务英语': 'translator',
    '数学与应用数学专业': 'analyst',
}

# 获取调解员关联的用户
cur.execute('''
    SELECT u.id, m.specialty 
    FROM users u 
    JOIN mediators m ON u.id = m.user_id
''')

for user_id, specialty in cur.fetchall():
    new_role = role_mapping.get(specialty, 'mediator')
    cur.execute('UPDATE users SET role = %s WHERE id = %s', (new_role, user_id))
    print(f'Updated user {user_id}: role -> {new_role} (specialty: {specialty})')

conn.commit()

print()
print('Updated users:')
cur.execute('SELECT u.id, u.email, u.real_name, m.specialty, u.role FROM users u LEFT JOIN mediators m ON u.id = m.user_id')
for row in cur.fetchall():
    print(f'  ID: {row[0]}, Email: {row[1]}, Name: {row[2]}, Specialty: {row[3]}, Role: {row[4]}')

conn.close()
print()
print('Done!')
