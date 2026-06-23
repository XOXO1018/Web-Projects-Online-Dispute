"""清理后重新测试调解员系统"""
import pymysql
import json
import urllib.request

BASE_URL = "http://localhost:8000"

def api_call(method, path, data=None, token=None):
    url = BASE_URL + path
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if data:
        body = json.dumps(data).encode()
    else:
        body = None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}

# 清理测试数据
print("清理测试数据...")
conn = pymysql.connect(host='localhost', user='root', password='lzz1212147474', charset='utf8mb4', database='zjfl')
cur = conn.cursor()
# 清理 case_id=2 的所有调解数据（使用一个新的案件）
cur.execute("DELETE FROM messages WHERE case_id = 2 AND sender_role = 'mediator'")
cur.execute("UPDATE cases SET status = 'negotiating', mediator_id = NULL WHERE id = 2")
cur.execute("DELETE FROM mediation_requests WHERE case_id = 2")
conn.commit()
conn.close()
print("清理完成")

# 1. 企业用户登录
print("\n1. 企业用户登录 (demo@zjfl.com)")
result = api_call("POST", "/api/v1/auth/login", {"email": "demo@zjfl.com", "password": "Demo@12345"})
enterprise_token = result["data"]["access_token"]
print(f"   登录成功")

# 2. 调解员登录 (陈美华 - mediator_id=2, user_id=4)
print("\n2. 调解员登录 (mediator_chen@zjfl.com)")
result = api_call("POST", "/api/v1/auth/login", {"email": "mediator_chen@zjfl.com", "password": "Mediator@123"})
mediator_token = result["data"]["access_token"]
mediator_user = result["data"]["user"]
print(f"   登录成功: {mediator_user['real_name']}")

# 3. 调解员查看案件列表 (介入前)
print("\n3. 调解员查看案件列表 (介入前)")
result = api_call("GET", "/api/v1/mediators/my-cases", token=mediator_token)
items_before = result.get('data', {}).get('items', [])
total_before = result.get('data', {}).get('total', 0)
print(f"   案件数量: {total_before}")
for item in items_before:
    print(f"   - {item.get('case_number')} (status={item.get('status')})")

# 4. 企业选择陈美华调解员介入案件2
print("\n4. 企业选择调解员介入 (case_id=2, mediator_id=2 - 陈美华)")
result = api_call("POST", "/api/v1/negotiation/mediator-intervene",
                  {"case_id": 2, "mediator_id": 2}, token=enterprise_token)
print(f"   结果: {result.get('message', result.get('error', 'N/A'))}")
print(f"   成功: {result.get('code') == 200}")

# 5. 调解员再次查看案件列表
print("\n5. 调解员再次查看案件列表 (介入后)")
result = api_call("GET", "/api/v1/mediators/my-cases", token=mediator_token)
items_after = result.get('data', {}).get('items', [])
total_after = result.get('data', {}).get('total', 0)
print(f"   案件数量: {total_after}")
for item in items_after:
    print(f"   - {item.get('case_number')} (status={item.get('status')})")

# 6. 结果验证
print("\n6. 结果验证")
print(f"   调解员介入前案件数: {total_before}")
print(f"   调解员介入后案件数: {total_after}")
print(f"   新增案件数: {total_after - total_before}")

# 检查数据库记录
conn = pymysql.connect(host='localhost', user='root', password='lzz1212147474', charset='utf8mb4', database='zjfl')
cur = conn.cursor(pymysql.cursors.DictCursor)
cur.execute("SELECT * FROM messages WHERE case_id = 2 AND sender_role = 'mediator' ORDER BY id DESC LIMIT 1")
msg = cur.fetchone()
if msg:
    print(f"\n7. 数据库验证")
    print(f"   消息: sender_id={msg['sender_id']}, sender_name={msg['sender_name']}")
    print(f"   内容: {msg['content']}")
cur.execute("SELECT id, status, mediator_id FROM cases WHERE id = 2")
case = cur.fetchone()
print(f"   案件: status={case['status']}, mediator_id={case['mediator_id']}")
conn.close()

if total_after > total_before:
    print("\n[OK] 测试通过！调解员可以看到企业邀请的案件！")
else:
    print("\n[FAIL] 测试失败！")
