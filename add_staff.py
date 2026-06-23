import pymysql
conn = pymysql.connect(host='localhost', user='root', password='lzz1212147474', database='zjfl', charset='utf8mb4')
cur = conn.cursor()

# 需要添加的翻译员和数据分析师
# 注意：mediators 表没有 staff_type 字段，我们直接插入到 mediators 表
# 但 API 显示的 staff_type 可能需要通过其他方式获取或修改

staff_list = [
    # 翻译员 - 商务英语
    ('tangxinyang@zljf.com', '唐心阳', '商务英语'),
    ('litongtong@zljf.com', '黎彤彤', '商务英语'),
    # 数据分析师 - 数学与应用数学
    ('menghaidong@zljf.com', '蒙海东', '数学与应用数学专业'),
    ('anqi@zljf.com', '安奇', '数学与应用数学专业'),
    ('chenjianning@zljf.com', '陈建凝', '数学与应用数学专业'),
]

# 先检查是否已存在
for email, name, specialty in staff_list:
    cur.execute('SELECT id FROM users WHERE email = %s', (email,))
    existing_user = cur.fetchone()
    if existing_user:
        print(f'User already exists: {email}')
        continue
    
    # 创建用户
    cur.execute('''
        INSERT INTO users (email, password_hash, real_name, role, status)
        VALUES (%s, %s, %s, %s, %s)
    ''', (email, 'temp_hash', name, 'mediator', 'active'))
    user_id = cur.lastrowid
    
    # 创建调解员记录
    cur.execute('''
        INSERT INTO mediators (user_id, name, specialty, rating, success_rate, cases_count, bio, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ''', (user_id, name, specialty, 5.0, 0, 0, '', 'active'))
    
    print(f'Created: {name} ({email}) - {specialty}')

conn.commit()

# 验证所有调解员
print()
print('All mediators now:')
cur.execute('SELECT u.id, u.email, m.name, m.specialty FROM users u JOIN mediators m ON u.id = m.user_id')
for row in cur.fetchall():
    print(f'  ID: {row[0]}, Email: {row[1]}, Name: {row[2]}, Specialty: {row[3]}')

conn.close()
print()
print('Done!')
