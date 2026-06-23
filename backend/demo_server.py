"""
智链解纷 - 后端服务器（MySQL版）
数据库：MySQL 8.0 (zjfl)
运行：python demo_server.py
"""
from fastapi import FastAPI, HTTPException, Depends, Header, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import hashlib, secrets, base64, io, time, os, uuid
import pymysql
from contextlib import contextmanager

# ── MySQL 数据库连接配置 ────────────────────────────────────
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", 3306)),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "lzz1212147474"),
    "database": os.environ.get("DB_NAME", "zjfl"),
    "charset": "utf8mb4",
    "autocommit": True,
    "cursorclass": pymysql.cursors.DictCursor,
}

@contextmanager
def get_db():
    """获取数据库连接上下文"""
    conn = pymysql.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()

# ── FastAPI 应用 ────────────────────────────────────────────
app = FastAPI(
    title="智链解纷 API",
    description="中国-东盟跨境商事纠纷在线解决平台",
    version="1.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 静态文件挂载 ─────────────────────────────────────────────
from fastapi.staticfiles import StaticFiles
upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

# ── 工具函数 ────────────────────────────────────────────────
def make_response(data=None, message="success", code=200):
    return {"code": code, "message": message, "data": data}

def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未授权访问")
    token = authorization.split(" ")[1]
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT u.* FROM users u
                JOIN tokens t ON t.user_id = u.id
                WHERE t.token = %s AND t.expires_at > NOW()
            """, (token,))
            user = cur.fetchone()
    if not user:
        raise HTTPException(status_code=401, detail="Token 无效或已过期")
    return user

def gen_token():
    return secrets.token_hex(32)

def hash_password(password: str) -> str:
    """使用 bcrypt 哈希密码（兼容旧 SHA-256 格式）"""
    try:
        import bcrypt
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        return f"bcrypt:{hashed}"
    except ImportError:
        # fallback: SHA-256 + salt
        import hashlib
        salt = secrets.token_hex(16)
        hashed = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()
        return f"{salt}${hashed}"

def verify_password(password: str, password_hash: str) -> bool:
    """验证密码（支持 bcrypt 和旧 SHA-256 格式）"""
    if password_hash.startswith('bcrypt:'):
        try:
            import bcrypt
            hashed = password_hash[7:]  # 去掉 'bcrypt:' 前缀
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except ImportError:
            return False
    elif '$' in password_hash:
        import hashlib
        try:
            salt, hashed = password_hash.split('$', 1)
            return hashlib.sha256((salt + password).encode('utf-8')).hexdigest() == hashed
        except ValueError:
            return False
    # 兼容旧明文格式（数据库中已存在的明文密码）
    return password_hash == password

def row_to_dict(row):
    """将数据库行转为普通dict，处理datetime等类型"""
    if not row:
        return row
    d = dict(row)
    for k, v in d.items():
        if isinstance(v, datetime):
            d[k] = v.isoformat()
        elif isinstance(v, timedelta):
            d[k] = str(v)
    return d

def rows_to_list(rows):
    return [row_to_dict(r) for r in rows]

# ── 内存存储（Mock 数据）─────────────────────────────────────
_mock_notes: list = []  # 案件笔记，内存 mock
_note_id_counter = 0

def _next_note_id():
    global _note_id_counter
    _note_id_counter += 1
    return _note_id_counter

# ── 通知辅助函数 ────────────────────────────────────────────
def create_notification(user_id: int, title: str, content: str, notif_type: str = "system"):
    """向指定用户创建一条系统通知
    notif_type 可选: case, meeting, system, message
    """
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO notifications (user_id, type, title, content, is_read)
                   VALUES (%s, %s, %s, %s, 0)""",
                (user_id, notif_type, title, content)
            )

# ── 验证码接口 ──────────────────────────────────────────────
@app.get("/api/v1/captcha/image", summary="获取图形验证码")
def get_captcha():
    try:
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new('RGB', (120, 40), color=(240, 248, 255))
        draw = ImageDraw.Draw(img)
        code = "DEMO"
        draw.text((25, 10), code, fill=(30, 120, 200))
        for _ in range(30):
            import random
            x, y = random.randint(0, 120), random.randint(0, 40)
            draw.point((x, y), fill=(random.randint(100, 200), random.randint(100, 200), random.randint(100, 200)))
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        img_b64 = base64.b64encode(buf.getvalue()).decode()
        captcha_id = secrets.token_hex(8)
        return make_response({"captcha_id": captcha_id, "image": f"data:image/png;base64,{img_b64}"})
    except Exception:
        captcha_id = secrets.token_hex(8)
        return make_response({"captcha_id": captcha_id, "image": "", "hint": "演示模式：验证码输入任意值即可"})

# ── 认证接口 ────────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: str
    password: str
    captcha_id: Optional[str] = None
    captcha_code: Optional[str] = None

@app.post("/api/v1/auth/login", summary="用户登录")
def login(req: LoginRequest):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE email = %s AND status = 'active'", (req.email,))
            user = cur.fetchone()
    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="邮箱或密码错误")

    # 获取调解员/翻译员/分析师的专业信息
    # 优先从 mediators 表获取，其次从 User 表的 mediator_domain 获取
    specialty = None
    if user["role"] == "mediator":
        with get_db() as conn:
            with conn.cursor() as cur:
                # 先尝试从 mediators 表获取
                cur.execute("SELECT specialty FROM mediators WHERE user_id = %s", (user["id"],))
                mediator = cur.fetchone()
                if mediator and mediator.get("specialty"):
                    specialty = mediator.get("specialty")
                # 如果没有，从 User 表的 mediator_domain 字段获取
                elif user.get("mediator_domain"):
                    specialty = user.get("mediator_domain")

    token = gen_token()
    expires_at = datetime.now() + timedelta(days=7)
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO tokens (token, user_id, expires_at) VALUES (%s, %s, %s)",
                (token, user["id"], expires_at)
            )
    return make_response({
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 604800,
        "refresh_token": token,  # 演示模式下复用 access_token
        "user": {
            "id": user["id"],
            "username": user["email"],
            "email": user["email"],
            "real_name": user["real_name"],
            "role": user["role"],
            "specialty": specialty,
            "enterprise_id": user.get("enterprise_id"),
            "must_change_password": False,
            "language": user.get("language", "zh-CN")
        }
    })

@app.post("/api/v1/auth/logout", summary="退出登录")
def logout(authorization: Optional[str] = Header(None), user=Depends(get_current_user)):
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM tokens WHERE user_id = %s", (user["id"],))
    return make_response(message="已退出登录")

@app.get("/api/v1/auth/me", summary="获取当前用户信息")
def get_me(user=Depends(get_current_user)):
    # 获取调解员/翻译员/分析师的专业信息
    # 优先从 mediators 表获取，其次从 User 表的 mediator_domain 获取
    specialty = None
    if user["role"] == "mediator":
        with get_db() as conn:
            with conn.cursor() as cur:
                # 先尝试从 mediators 表获取
                cur.execute("SELECT specialty FROM mediators WHERE user_id = %s", (user["id"],))
                mediator = cur.fetchone()
                if mediator and mediator.get("specialty"):
                    specialty = mediator.get("specialty")
                # 如果没有，从 User 表的 mediator_domain 字段获取
                elif user.get("mediator_domain"):
                    specialty = user.get("mediator_domain")
    return make_response({
        "id": user["id"],
        "username": user["email"],
        "email": user["email"],
        "real_name": user["real_name"],
        "role": user["role"],
        "specialty": specialty,
        "enterprise_id": user.get("enterprise_id"),
        "language": user.get("language", "zh-CN"),
        "must_change_password": False,
        "notify_email": bool(user.get("notify_email", 1)),
        "notify_sms": bool(user.get("notify_sms", 0)),
    })

class RegisterRequest(BaseModel):
    email: str
    password: str
    real_name: str
    enterprise_name: str
    credit_code: str
    contact_phone: str
    legal_person: str

@app.post("/api/v1/auth/register", summary="企业注册")
def register(req: RegisterRequest):
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                # 检查邮箱是否已注册
                cur.execute("SELECT id FROM users WHERE email = %s", (req.email,))
                if cur.fetchone():
                    raise HTTPException(status_code=400, detail="该邮箱已注册")
                # 检查企业信用代码是否已存在
                cur.execute("SELECT id FROM enterprises WHERE credit_code = %s", (req.credit_code,))
                ent = cur.fetchone()
                if not ent:
                    cur.execute(
                        "INSERT INTO enterprises (name, credit_code, legal_person, contact_phone, audit_status, status) VALUES (%s, %s, %s, %s, 'approved', 'active')",
                        (req.enterprise_name, req.credit_code, req.legal_person, req.contact_phone)
                    )
                    ent_id = cur.lastrowid
                else:
                    ent_id = ent["id"]
                # 创建用户
                cur.execute(
                    "INSERT INTO users (email, password_hash, real_name, role, enterprise_id, status) VALUES (%s, %s, %s, 'enterprise_admin', %s, 'active')",
                    (req.email, hash_password(req.password), req.real_name, ent_id)
                )
                new_id = cur.lastrowid
        return make_response({"message": "注册成功（演示模式：已自动激活）", "user_id": new_id})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"注册失败: {str(e)}")

# ── 案件接口 ────────────────────────────────────────────────
@app.get("/api/v1/cases", summary="获取案件列表")
def list_cases(
    page: int = 1, page_size: int = 10,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    user=Depends(get_current_user)
):
    with get_db() as conn:
        with conn.cursor() as cur:
            where = ["1=1"]
            params = []
            if user["role"] not in ("platform_admin", "mediator"):
                where.append("c.enterprise_id = %s")
                params.append(user.get("enterprise_id"))
            if status:
                where.append("c.status = %s")
                params.append(status)
            if keyword:
                where.append("(c.case_number LIKE %s OR c.opponent_name LIKE %s)")
                params.extend([f"%{keyword}%", f"%{keyword}%"])

            where_clause = " AND ".join(where)
            cur.execute(f"SELECT COUNT(*) as cnt FROM cases c WHERE {where_clause}", params)
            total = cur.fetchone()["cnt"]

            offset = (page - 1) * page_size
            cur.execute(
                f"SELECT c.* FROM cases c WHERE {where_clause} ORDER BY c.created_at DESC LIMIT %s OFFSET %s",
                params + [page_size, offset]
            )
            items = rows_to_list(cur.fetchall())
    return make_response({"total": total, "page": page, "page_size": page_size, "items": items})

@app.get("/api/v1/cases/stats", summary="案件统计")
def case_stats(user=Depends(get_current_user)):
    with get_db() as conn:
        with conn.cursor() as cur:
            base_where = ""
            params = []
            if user["role"] not in ("platform_admin", "mediator"):
                base_where = " WHERE enterprise_id = %s"
                params.append(user.get("enterprise_id"))

            cur.execute(f"SELECT COUNT(*) as cnt FROM cases{base_where}", params)
            total = cur.fetchone()["cnt"]

            statuses = ["negotiating", "mediating", "closed_success", "closed_fail"]
            status_counts = {}
            for s in statuses:
                cur.execute(f"SELECT COUNT(*) as cnt FROM cases WHERE status = %s{base_where.replace('WHERE', 'AND') if base_where else ''}", [s] + params)
                status_counts[s] = cur.fetchone()["cnt"]

            cur.execute(f"SELECT COALESCE(SUM(amount), 0) as total_amount FROM cases{base_where}", params)
            total_amount = float(cur.fetchone()["total_amount"])

    return make_response({
        "total": total,
        "negotiating": status_counts.get("negotiating", 0),
        "mediating": status_counts.get("mediating", 0),
        "closed_success": status_counts.get("closed_success", 0),
        "closed_fail": status_counts.get("closed_fail", 0),
        "total_amount": total_amount,
        "monthly_trend": [
            {"month": "2026-01", "count": 1},
            {"month": "2026-02", "count": 2},
            {"month": "2026-03", "count": 3},
            {"month": "2026-04", "count": total},
        ],
        "country_distribution": [
            {"country": "VN", "count": 1},
            {"country": "TH", "count": 1},
            {"country": "MY", "count": 1},
        ]
    })

@app.get("/api/v1/cases/{case_id}", summary="获取案件详情")
def get_case(case_id: int, user=Depends(get_current_user)):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM cases WHERE id = %s", (case_id,))
            case = cur.fetchone()
            if not case:
                raise HTTPException(status_code=404, detail="案件不存在")

            # 调解员只能查看自己介入过的案件
            if user["role"] == "mediator":
                cur.execute(
                    """SELECT COUNT(*) as cnt FROM (
                        SELECT id FROM messages WHERE case_id = %s AND sender_id = %s AND sender_role = 'mediator' AND message_type = 'system'
                        UNION
                        SELECT id FROM mediation_requests WHERE case_id = %s AND mediator_id IN (SELECT id FROM mediators WHERE user_id = %s)
                    ) as t""",
                    (case_id, user["id"], case_id, user["id"])
                )
                if cur.fetchone()["cnt"] == 0:
                    raise HTTPException(status_code=403, detail="您尚未介入此案件，无权查看")

            # 查询证据数量
            cur.execute("SELECT COUNT(*) as cnt FROM evidence WHERE case_id = %s", (case_id,))
            evidence_count = cur.fetchone()["cnt"]

            # 查询消息数量
            cur.execute("SELECT COUNT(*) as cnt FROM messages WHERE case_id = %s", (case_id,))
            message_count = cur.fetchone()["cnt"]

            # 构建真实时间轴
            timeline = [
                {"time": case["created_at"].isoformat() if isinstance(case["created_at"], datetime) else str(case.get("created_at", "")), "event": "案件创建", "operator": "系统", "type": "create"},
            ]
            cur.execute("SELECT * FROM evidence WHERE case_id = %s ORDER BY created_at", (case_id,))
            for e in cur.fetchall():
                timeline.append({"time": str(e.get("created_at", "")), "event": f"上传证据: {e.get('file_name', '')}", "operator": "用户", "type": "evidence"})
            cur.execute("SELECT * FROM mediation_requests WHERE case_id = %s ORDER BY created_at", (case_id,))
            for med in cur.fetchall():
                timeline.append({"time": str(med.get("created_at", "")), "event": f"调解申请: {med.get('status', '')}", "operator": "系统", "type": "mediation"})
            cur.execute("SELECT * FROM messages WHERE case_id = %s AND message_type = 'system' ORDER BY created_at", (case_id,))
            for m in cur.fetchall():
                timeline.append({"time": str(m.get("created_at", "")), "event": str(m.get("content", ""))[:80], "operator": m.get("sender_name", "系统"), "type": "system"})
            timeline.sort(key=lambda x: x["time"], reverse=False)

    case_detail = row_to_dict(case)
    case_detail["timeline"] = timeline
    case_detail["evidence_count"] = evidence_count
    case_detail["message_count"] = message_count
    return make_response(case_detail)

class CaseCreateRequest(BaseModel):
    opponent_name: str
    opponent_country: str
    contract_type: str
    amount: float
    dispute_desc: str
    expected_method: str
    contract_date: Optional[str] = None
    incident_date: Optional[str] = None

@app.post("/api/v1/cases", summary="创建新案件")
def create_case(req: CaseCreateRequest, user=Depends(get_current_user)):
    import random
    from datetime import date
    case_number = f"CASE{date.today().strftime('%Y%m%d')}{random.randint(1000, 9999)}"
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO cases (case_number, enterprise_id, opponent_name, opponent_country,
                       contract_type, amount, dispute_desc, expected_method, status, contract_date, incident_date)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'negotiating', %s, %s)""",
                    (case_number, user.get("enterprise_id", 1), req.opponent_name, req.opponent_country,
                     req.contract_type, req.amount, req.dispute_desc, req.expected_method,
                     req.contract_date, req.incident_date)
                )
                new_id = cur.lastrowid
                cur.execute("SELECT * FROM cases WHERE id = %s", (new_id,))
                new_case = cur.fetchone()
        return make_response(row_to_dict(new_case), message="案件创建成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建案件失败: {str(e)}")

# ── 证据接口 ────────────────────────────────────────────────
@app.get("/api/v1/cases/{case_id}/evidence", summary="获取案件证据列表")
def list_evidence(case_id: int, user=Depends(get_current_user)):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM evidence WHERE case_id = %s ORDER BY created_at", (case_id,))
            items = rows_to_list(cur.fetchall())
    return make_response(items)

@app.post("/api/v1/cases/{case_id}/evidence", summary="上传证据文件（模拟）")
def upload_evidence(case_id: int, user=Depends(get_current_user)):
    try:
        file_hash = hashlib.sha256(secrets.token_bytes(32)).hexdigest()
        storage_voucher = f"CERT-{datetime.now().strftime('%Y%m%d')}-{secrets.token_hex(2)}"
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO evidence (case_id, file_name, evidence_type, file_hash, storage_voucher)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (case_id, "demo_evidence.pdf", "合同", file_hash[:20] + "...", storage_voucher)
                )
                new_id = cur.lastrowid
                cur.execute("SELECT * FROM evidence WHERE id = %s", (new_id,))
                new_evidence = cur.fetchone()
        return make_response(row_to_dict(new_evidence), message="证据上传成功，SHA-256哈希已生成并存证")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"证据上传失败: {str(e)}")

@app.delete("/api/v1/cases/{case_id}/evidence/{evidence_id}", summary="删除证据")
def delete_evidence(case_id: int, evidence_id: int, user=Depends(get_current_user)):
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM evidence WHERE id = %s AND case_id = %s", (evidence_id, case_id))
                if not cur.fetchone():
                    raise HTTPException(status_code=404, detail="证据不存在")
                cur.execute("DELETE FROM evidence WHERE id = %s AND case_id = %s", (evidence_id, case_id))
        return make_response(message="证据已删除")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除证据失败: {str(e)}")

# ── 协商消息接口 ────────────────────────────────────────────
@app.get("/api/v1/cases/{case_id}/messages", summary="获取协商消息")
def list_messages(case_id: int, user=Depends(get_current_user)):
    with get_db() as conn:
        with conn.cursor() as cur:
            # 调解员只能查看自己介入过的案件
            if user["role"] == "mediator":
                cur.execute(
                    """SELECT COUNT(*) as cnt FROM (
                        SELECT id FROM messages WHERE case_id = %s AND sender_id = %s AND sender_role = 'mediator' AND message_type = 'system'
                        UNION
                        SELECT id FROM mediation_requests WHERE case_id = %s AND mediator_id IN (SELECT id FROM mediators WHERE user_id = %s)
                    ) as t""",
                    (case_id, user["id"], case_id, user["id"])
                )
                if cur.fetchone()["cnt"] == 0:
                    raise HTTPException(status_code=403, detail="您尚未介入此案件，无权查看")
            
            cur.execute("SELECT * FROM messages WHERE case_id = %s ORDER BY created_at", (case_id,))
            items = rows_to_list(cur.fetchall())
    return make_response(items)

class MessageRequest(BaseModel):
    content: str
    message_type: str = "text"
    file_name: str | None = None
    file_size: str | None = None

@app.post("/api/v1/cases/{case_id}/messages", summary="发送协商消息")
def send_message(case_id: int, req: MessageRequest, user=Depends(get_current_user)):
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                # 确保 messages 表有 file_name 和 file_size 列
                cur.execute("""
                    INSERT INTO messages (case_id, sender_id, sender_name, sender_role, message_type, content, file_name, file_size)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (case_id, user["id"], user["real_name"], user["role"], req.message_type, req.content,
                      req.file_name, req.file_size))
                new_id = cur.lastrowid
                cur.execute("SELECT * FROM messages WHERE id = %s", (new_id,))
                msg = cur.fetchone()
        return make_response(row_to_dict(msg))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发送消息失败: {str(e)}")

# ── 文件上传接口 ────────────────────────────────────────────
@app.post("/api/v1/upload/image", summary="上传图片用于协商室")
async def upload_image(file: UploadFile = File(...), user=Depends(get_current_user)):
    """上传图片用于协商室"""
    if file.content_type not in ["image/jpeg", "image/png", "image/gif", "image/webp"]:
        raise HTTPException(400, {"code": 400, "msg": "Only image files are allowed"})
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(400, {"code": 400, "msg": "File too large (max 10MB)"})
    ext = file.filename.rsplit('.', 1)[-1] if '.' in file.filename else 'jpg'
    filename = f"chat_{int(time.time())}_{uuid.uuid4().hex[:8]}.{ext}"
    chat_upload_dir = os.path.join(os.path.dirname(__file__), "uploads", "chat")
    os.makedirs(chat_upload_dir, exist_ok=True)
    filepath = os.path.join(chat_upload_dir, filename)
    with open(filepath, "wb") as f:
        f.write(contents)
    url = f"/uploads/chat/{filename}"
    return make_response({"url": url, "filename": file.filename, "size": len(contents), "type": "image"})

@app.post("/api/v1/upload/file", summary="上传文件用于协商室")
async def upload_file(file: UploadFile = File(...), user=Depends(get_current_user)):
    """上传文件用于协商室"""
    ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "xls", "xlsx", "jpg", "jpeg", "png", "gif", "webp", "zip", "rar", "txt", "csv"}
    ALLOWED_CONTENT_TYPES = [
        "application/pdf", "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "image/jpeg", "image/png", "image/gif", "image/webp",
        "application/zip", "application/x-rar-compressed",
        "text/plain", "text/csv",
    ]
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else 'bin'
    if ext not in ALLOWED_EXTENSIONS and (file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES):
        raise HTTPException(400, {"code": 400, "msg": f"不支持的文件类型: {ext}"})
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(400, {"code": 400, "msg": "File too large (max 10MB)"})
    ext = file.filename.rsplit('.', 1)[-1] if '.' in file.filename else 'bin'
    filename = f"file_{int(time.time())}_{uuid.uuid4().hex[:8]}.{ext}"
    chat_upload_dir = os.path.join(os.path.dirname(__file__), "uploads", "chat")
    os.makedirs(chat_upload_dir, exist_ok=True)
    filepath = os.path.join(chat_upload_dir, filename)
    with open(filepath, "wb") as f:
        f.write(contents)
    url = f"/uploads/chat/{filename}"
    return make_response({"url": url, "filename": file.filename, "size": len(contents), "type": "file"})

# ── 案件归档端点 ──────────────────────────────────────────────
@app.put("/api/v1/cases/{case_id}/archive", summary="归档案件")
def archive_case(case_id: int, user=Depends(get_current_user)):
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, status FROM cases WHERE id = %s", (case_id,))
                case = cur.fetchone()
                if not case:
                    raise HTTPException(status_code=404, detail="案件不存在")
                if case["status"] not in ("closed_success", "closed_fail"):
                    raise HTTPException(status_code=400, detail="只有已结案的案件才能归档")
                cur.execute("UPDATE cases SET status = 'archived' WHERE id = %s", (case_id,))
        return make_response(message="案件已归档")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"归档失败: {str(e)}")

# ── 案件状态更新 ────────────────────────────────────────────
@app.put("/api/v1/cases/{case_id}/status", summary="更新案件状态")
def update_case_status(case_id: int, data: dict, user=Depends(get_current_user)):
    """调解员或管理员更新案件状态，支持 closed_success / closed_fail"""
    new_status = data.get("status", "")
    valid_statuses = ("negotiating", "mediating", "closed_success", "closed_fail", "draft")
    if new_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"无效状态，可选: {', '.join(valid_statuses)}")
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, status, enterprise_id FROM cases WHERE id = %s", (case_id,))
                case = cur.fetchone()
                if not case:
                    raise HTTPException(status_code=404, detail="案件不存在")
                cur.execute("UPDATE cases SET status = %s WHERE id = %s", (new_status, case_id))
        return make_response({"case_id": case_id, "status": new_status}, message="案件状态已更新")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新状态失败: {str(e)}")

# ── 案件笔记 ────────────────────────────────────────────────
@app.get("/api/v1/cases/{case_id}/notes", summary="获取案件笔记列表")
def list_case_notes(case_id: int, user=Depends(get_current_user)):
    """获取指定案件的笔记列表（内存 mock）"""
    notes = [n for n in _mock_notes if n["case_id"] == case_id]
    return make_response(notes)

@app.post("/api/v1/cases/{case_id}/notes", summary="添加案件笔记")
def create_case_note(case_id: int, data: dict, user=Depends(get_current_user)):
    """添加一条案件笔记，支持文本/图片/文件类型"""
    note_type = data.get("type", "text")  # text / image / file
    content = data.get("content", "")
    if note_type != "text" and not content:
        raise HTTPException(status_code=400, detail="笔记内容不能为空")
    note_id = _next_note_id()
    note = {
        "id": note_id,
        "case_id": case_id,
        "type": note_type,
        "content": content,
        "created_by": user["id"],
        "created_by_name": user.get("real_name", ""),
        "created_at": datetime.now().isoformat(),
    }
    _mock_notes.append(note)
    return make_response(note, message="笔记已添加")

@app.delete("/api/v1/cases/{case_id}/notes/{note_id}", summary="删除案件笔记")
def delete_case_note(case_id: int, note_id: int, user=Depends(get_current_user)):
    """删除一条案件笔记"""
    global _mock_notes
    original_len = len(_mock_notes)
    _mock_notes = [n for n in _mock_notes if not (n["id"] == note_id and n["case_id"] == case_id)]
    if len(_mock_notes) < original_len:
        return make_response(message="笔记已删除")
    raise HTTPException(status_code=404, detail="笔记不存在")

# ── 协商端点 ────────────────────────────────────────────────
class NegotiationStartRequest(BaseModel):
    case_id: int
    opponent_email: str

@app.post("/api/v1/negotiation/start", summary="发起协商")
def start_negotiation(req: NegotiationStartRequest, user=Depends(get_current_user)):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM cases WHERE id = %s", (req.case_id,))
            case = cur.fetchone()
            if not case:
                raise HTTPException(status_code=404, detail="案件不存在")
    return make_response({"case_id": req.case_id, "status": "negotiating"}, message="协商已发起，对方将收到邀请邮件")

class NegotiationConfirmRequest(BaseModel):
    case_id: int
    result: str  # "success" 或 "failed"

@app.post("/api/v1/negotiation/confirm-result", summary="确认协商结果")
def confirm_negotiation_result(req: NegotiationConfirmRequest, user=Depends(get_current_user)):
    try:
        new_status = "closed_success" if req.result == "success" else "closed_fail"
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, status FROM cases WHERE id = %s", (req.case_id,))
                case = cur.fetchone()
                if not case:
                    raise HTTPException(status_code=404, detail="案件不存在")
                cur.execute("UPDATE cases SET status = %s WHERE id = %s", (new_status, req.case_id))
        return make_response({"case_id": req.case_id, "status": new_status}, message="协商结果已确认")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"确认结果失败: {str(e)}")

@app.post("/api/v1/negotiation/sign-memo", summary="签署协商备忘录")
def sign_memo(data: dict, user=Depends(get_current_user)):
    try:
        case_id = data.get("case_id")
        memo_content = data.get("memo_content", "")
        if not case_id:
            raise HTTPException(status_code=400, detail="缺少案件ID")
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM cases WHERE id = %s", (case_id,))
                if not cur.fetchone():
                    raise HTTPException(status_code=404, detail="案件不存在")
                # 记录签署备忘录的系统消息
                cur.execute("""
                    INSERT INTO messages (case_id, sender_id, sender_name, sender_role, message_type, content)
                    VALUES (%s, %s, %s, 'enterprise', 'system', %s)
                """, (case_id, user["id"], user["real_name"], f"[备忘录签署] {memo_content[:200]}"))
        return make_response(message="备忘录签署成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"签署备忘录失败: {str(e)}")

# ── 调解端点 ────────────────────────────────────────────────
class MediationApplyRequest(BaseModel):
    case_id: int
    demand_text: str

@app.post("/api/v1/mediation/apply", summary="申请调解")
def apply_mediation(req: MediationApplyRequest, user=Depends(get_current_user)):
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                # 创建调解申请
                cur.execute(
                    "INSERT INTO mediation_requests (case_id, demand_text, status) VALUES (%s, %s, 'pending')",
                    (req.case_id, req.demand_text)
                )
                request_id = cur.lastrowid
                # 更新案件状态
                cur.execute("UPDATE cases SET status = 'mediating' WHERE id = %s", (req.case_id,))
        return make_response({"request_id": request_id, "case_id": req.case_id}, message="调解申请已提交")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"申请调解失败: {str(e)}")

class SelectMediatorRequest(BaseModel):
    request_id: int
    mediator_id: int

@app.post("/api/v1/mediation/select-mediator", summary="选择调解员")
def select_mediator(req: SelectMediatorRequest, user=Depends(get_current_user)):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM mediators WHERE id = %s", (req.mediator_id,))
            mediator = cur.fetchone()
            if not mediator:
                raise HTTPException(status_code=404, detail="调解员不存在")
            cur.execute(
                "UPDATE mediation_requests SET mediator_id = %s, status = 'mediator_selected' WHERE id = %s",
                (req.mediator_id, req.request_id)
            )
    return make_response({
        "request_id": req.request_id,
        "mediator_id": req.mediator_id,
        "mediator_name": mediator["name"],
        "status": "mediator_selected"
    }, message="调解员已选定，等待安排会议")

class MediationOpinionRequest(BaseModel):
    meeting_id: int
    opinion: str
    success: bool
    agreement_content: Optional[str] = None

@app.post("/api/v1/mediation/opinion", summary="提交调解意见")
def submit_opinion(req: MediationOpinionRequest, user=Depends(get_current_user)):
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                # 查找对应的会议和调解申请
                cur.execute("SELECT * FROM meetings WHERE id = %s", (req.meeting_id,))
                meeting = cur.fetchone()
                if not meeting:
                    raise HTTPException(status_code=404, detail="会议不存在")
                
                # 更新调解申请结果
                if req.success:
                    agreement_id = secrets.token_hex(4)
                    cur.execute(
                        "UPDATE mediation_requests SET status = 'completed', result = %s, agreement_id = %s WHERE case_id = %s AND status != 'completed'",
                        (req.opinion, agreement_id, meeting["case_id"])
                    )
                    cur.execute("UPDATE cases SET status = 'closed_success' WHERE id = %s", (meeting["case_id"],))
                else:
                    cur.execute(
                        "UPDATE mediation_requests SET status = 'failed', result = %s WHERE case_id = %s AND status != 'completed'",
                        (req.opinion, meeting["case_id"])
                    )
                    cur.execute("UPDATE cases SET status = 'closed_fail' WHERE id = %s", (meeting["case_id"],))
                
                # 更新会议状态
                cur.execute("UPDATE meetings SET status = 'ended' WHERE id = %s", (req.meeting_id,))
        return make_response({
            "meeting_id": req.meeting_id,
            "success": req.success,
            "agreement_id": secrets.token_hex(4) if req.success else None
        }, message="调解意见已提交")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提交调解意见失败: {str(e)}")

class ScheduleMeetingRequest(BaseModel):
    request_id: int
    scheduled_time: str
    note: Optional[str] = None

@app.post("/api/v1/mediation/schedule-meeting", summary="调解员安排会议")
def schedule_meeting(req: ScheduleMeetingRequest, user=Depends(get_current_user)):
    if user["role"] != "mediator":
        raise HTTPException(status_code=403, detail="仅调解员可安排会议")
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                # 获取调解员信息
                cur.execute("SELECT * FROM mediators WHERE user_id = %s", (user["id"],))
                mediator = cur.fetchone()
                if not mediator:
                    raise HTTPException(status_code=404, detail="调解员信息不存在")
                
                # 兼容处理：request_id 可能是 mediation_requests.id 或 case_id
                case_id = req.request_id
                cur.execute("SELECT id, case_number FROM cases WHERE id = %s", (case_id,))
                case_info = cur.fetchone()
                if not case_info:
                    raise HTTPException(status_code=404, detail="案件不存在")
                
                # 生成频道名
                channel_name = f"mediation_{case_id}_{secrets.token_hex(4)[:8]}"
                
                # 创建会议记录
                cur.execute(
                    """INSERT INTO meetings (case_id, mediator_id, channel_name, scheduled_time, note, status)
                       VALUES (%s, %s, %s, %s, %s, 'scheduled')""",
                    (case_id, mediator["id"], channel_name, req.scheduled_time, req.note or "")
                )
                meeting_id = cur.lastrowid
                
                # 更新案件状态为调解中
                cur.execute("UPDATE cases SET status = 'mediating' WHERE id = %s", (case_id,))
                
                # 尝试更新调解申请（如果存在）
                cur.execute("UPDATE mediation_requests SET status = 'mediating' WHERE case_id = %s", (case_id,))
                
                # 发送会议安排通知给申请企业用户
                cur.execute(
                    "SELECT id, case_number, enterprise_id FROM cases WHERE id = %s",
                    (case_id,)
                )
                case_detail = cur.fetchone()
                if case_detail and case_detail.get("enterprise_id"):
                    cur.execute(
                        "SELECT id FROM users WHERE enterprise_id = %s AND role IN ('enterprise_admin','enterprise_user') AND status = 'active'",
                        (case_detail["enterprise_id"],)
                    )
                    enterprise_users = cur.fetchall()
                    for eu in enterprise_users:
                        create_notification(
                            eu["id"],
                            f"会议安排通知 - {case_detail['case_number']}",
                            f"调解员已安排一场调解会议，计划时间：{req.scheduled_time}。请及时查收并准时参加。",
                            notif_type="meeting"
                        )
        return make_response({
            "meeting_id": meeting_id,
            "channel_name": channel_name,
            "scheduled_time": req.scheduled_time,
            "status": "scheduled"
        }, message="会议已安排")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"安排会议失败: {str(e)}")

@app.get("/api/v1/mediation/meetings/{meeting_id}/token", summary="获取会议令牌")
def get_meeting_token(meeting_id: int, user=Depends(get_current_user)):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM meetings WHERE id = %s", (meeting_id,))
            meeting = cur.fetchone()
            if not meeting:
                raise HTTPException(status_code=404, detail="会议不存在")
            
            # 生成 mock Agora token
            token = secrets.token_hex(16)
    
    return make_response({
        "token": token,
        "channel_name": meeting["channel_name"],
        "uid": user["id"]
    }, message="获取令牌成功")

@app.get("/api/v1/mediator/meetings", summary="调解员获取自己的会议列表")
def get_my_meetings(user=Depends(get_current_user)):
    """返回当前调解员负责的所有会议，含案件信息"""
    if user["role"] != "mediator":
        raise HTTPException(status_code=403, detail="仅调解员可访问")
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM mediators WHERE user_id = %s", (user["id"],))
            m = cur.fetchone()
            if not m:
                return make_response([])
            cur.execute("""
                SELECT mt.id, mt.case_id, mt.channel_name, mt.scheduled_time, mt.status, mt.note,
                       c.case_number
                FROM meetings mt
                LEFT JOIN cases c ON mt.case_id = c.id
                WHERE mt.mediator_id = %s
                ORDER BY mt.scheduled_time DESC
            """, (m["id"],))
            rows = rows_to_list(cur.fetchall())
    return make_response(rows)

@app.get("/api/v1/cases/{case_id}/meetings", summary="获取案件的会议列表")
def get_case_meetings(case_id: int, user=Depends(get_current_user)):
    """返回指定案件下的所有会议"""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT mt.id, mt.case_id, mt.channel_name, mt.scheduled_time, mt.status, mt.note,
                       u.real_name as mediator_name
                FROM meetings mt
                LEFT JOIN mediators med ON mt.mediator_id = med.id
                LEFT JOIN users u ON med.user_id = u.id
                WHERE mt.case_id = %s
                ORDER BY mt.scheduled_time DESC
            """, (case_id,))
            rows = rows_to_list(cur.fetchall())
    return make_response(rows)

# ── 签署协议 / 导出材料 ────────────────────────────────────
@app.post("/api/v1/mediation/agreements/{agreement_id}/sign", summary="签署调解协议")
def sign_agreement(agreement_id: str, sms_code: str = None, user=Depends(get_current_user)):
    """签署调解协议（演示模式：直接通过）"""
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM mediation_requests WHERE agreement_id = %s", (agreement_id,))
                med_req = cur.fetchone()
                if not med_req:
                    raise HTTPException(status_code=404, detail="调解协议不存在")
                cur.execute(
                    "UPDATE mediation_requests SET status = 'signed' WHERE id = %s",
                    (med_req["id"],)
                )
        return make_response({"agreement_id": agreement_id, "signed": True}, message="协议签署成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"签署协议失败: {str(e)}")

@app.get("/api/v1/mediation/export/{case_id}", summary="导出调解材料")
def export_materials(case_id: int, user=Depends(get_current_user)):
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM cases WHERE id = %s", (case_id,))
                case = cur.fetchone()
                if not case:
                    raise HTTPException(status_code=404, detail="案件不存在")
                cur.execute("SELECT * FROM evidence WHERE case_id = %s ORDER BY created_at", (case_id,))
                evidence = rows_to_list(cur.fetchall())
                cur.execute("SELECT * FROM mediation_requests WHERE case_id = %s ORDER BY created_at", (case_id,))
                mediations = rows_to_list(cur.fetchall())
        return make_response({
            "case": row_to_dict(case),
            "evidence": evidence,
            "mediations": mediations,
            "export_time": datetime.now().isoformat(),
        }, message="材料导出成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出材料失败: {str(e)}")


# ── 用户端点 ────────────────────────────────────────────────
@app.get("/api/v1/users/send-sign-code", summary="发送签署验证码（演示模式）")
def send_sign_code(user=Depends(get_current_user)):
    """演示模式：直接返回成功，不实际发送短信"""
    return make_response({"code": "000000", "expires_in": 300}, message="验证码已发送（演示模式：000000）")

class UpdateUserRequest(BaseModel):
    real_name: Optional[str] = None
    language: Optional[str] = None
    notify_email: Optional[bool] = None
    notify_sms: Optional[bool] = None

@app.put("/api/v1/users/me", summary="更新用户信息")
def update_me(req: UpdateUserRequest, user=Depends(get_current_user)):
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                updates = []
                params = []
                if req.real_name is not None:
                    updates.append("real_name = %s")
                    params.append(req.real_name)
                if req.language is not None:
                    updates.append("language = %s")
                    params.append(req.language)
                if req.notify_email is not None:
                    updates.append("notify_email = %s")
                    params.append(int(req.notify_email))
                if req.notify_sms is not None:
                    updates.append("notify_sms = %s")
                    params.append(int(req.notify_sms))
                if updates:
                    params.append(user["id"])
                    cur.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = %s", params)
                cur.execute("SELECT real_name FROM users WHERE id = %s", (user["id"],))
                result = cur.fetchone()
        return make_response({"real_name": result["real_name"]}, message="更新成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新用户信息失败: {str(e)}")

@app.post("/api/v1/auth/change-password", summary="修改密码")
def change_password(data: dict, user=Depends(get_current_user)):
    old_pwd = data.get("old_password", "")
    new_pwd = data.get("new_password", "")
    if not verify_password(old_pwd, user["password_hash"]):
        raise HTTPException(status_code=400, detail="原密码错误")
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE users SET password_hash = %s WHERE id = %s", (hash_password(new_pwd), user["id"]))
        return make_response(message="密码修改成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"修改密码失败: {str(e)}")

@app.get("/api/v1/mediators", summary="获取调解员列表")
def list_mediators(user=Depends(get_current_user)):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM mediators WHERE status = 'active' ORDER BY rating DESC")
            items = rows_to_list(cur.fetchall())
    return make_response(items)

@app.get("/api/v1/mediators/recommend/{case_id}", summary="推荐调解员/翻译员/数据分析师")
def recommend_mediators(case_id: int, user=Depends(get_current_user)):
    """返回所有可用的调解员、翻译员、数据分析师"""
    with get_db() as conn:
        with conn.cursor() as cur:
            # 返回所有活跃的调解员（包括翻译员、数据分析师），按评分排序
            cur.execute("SELECT * FROM mediators WHERE status = 'active' ORDER BY rating DESC")
            items = rows_to_list(cur.fetchall())
    return make_response(items, message="获取所有可用的调解员/翻译员/数据分析师")

@app.get("/api/v1/mediators/me", summary="获取当前调解员信息")
def get_mediator_me(user=Depends(get_current_user)):
    if user["role"] != "mediator":
        raise HTTPException(status_code=403, detail="仅调解员可访问")
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM mediators WHERE user_id = %s", (user["id"],))
            m = cur.fetchone()
            if not m:
                # 如果 mediator 记录不存在，根据 users 表信息自动创建
                cur.execute("SELECT real_name FROM users WHERE id = %s", (user["id"],))
                u = cur.fetchone()
                name = u["real_name"] if u else user.get("real_name", "")
                cur.execute(
                    """INSERT INTO mediators (user_id, name, specialty, status)
                       VALUES (%s, %s, '', 'active')""",
                    (user["id"], name)
                )
                conn.commit()
                cur.execute("SELECT * FROM mediators WHERE user_id = %s", (user["id"],))
                m = cur.fetchone()
            data = row_to_dict(m)
    return make_response(data)

@app.put("/api/v1/mediators/me", summary="更新当前调解员信息")
def update_mediator_me(req_body: dict = Body(...), user=Depends(get_current_user)):
    if user["role"] != "mediator":
        raise HTTPException(status_code=403, detail="仅调解员可访问")
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM mediators WHERE user_id = %s", (user["id"],))
            m = cur.fetchone()
            if not m:
                raise HTTPException(status_code=404, detail="调解员记录不存在")
            fields = []
            params = []
            for field in ["name", "specialty", "bio"]:
                if field in req_body:
                    fields.append(f"{field} = %s")
                    params.append(req_body[field])
            if fields:
                params.append(m["id"])
                cur.execute(f"UPDATE mediators SET {', '.join(fields)} WHERE id = %s", params)
                conn.commit()
            cur.execute("SELECT * FROM mediators WHERE id = %s", (m["id"],))
            data = row_to_dict(cur.fetchone())
    return make_response(data, message="调解员信息已更新")

@app.get("/api/v1/mediators/my-cases", summary="获取调解员介入的案件列表")
def list_mediator_cases(
    page: int = 1, page_size: int = 10,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    user=Depends(get_current_user)
):
    if user["role"] != "mediator":
        raise HTTPException(status_code=403, detail="仅调解员可访问")
    with get_db() as conn:
        with conn.cursor() as cur:
            # 查找该调解员介入过的案件
            # 方式1: 通过 messages 表中 sender_role='mediator' 且 sender_id=user.id（调解员用户ID）
            # 方式2: 通过 mediation_requests 表中 mediator_id 匹配当前调解员
            where_parts = [
                "(m.sender_id = %s AND m.sender_role = 'mediator' AND m.message_type = 'system' AND c.id = m.case_id)",
                " OR ",
                "(mr.mediator_id IN (SELECT id FROM mediators WHERE user_id = %s) AND c.id = mr.case_id)"
            ]
            base_query = """
                SELECT DISTINCT c.*, 
                    (SELECT id FROM messages WHERE case_id = c.id AND sender_role = 'mediator' ORDER BY id DESC LIMIT 1) as _msg_id
                FROM cases c
                LEFT JOIN messages m ON c.id = m.case_id
                LEFT JOIN mediation_requests mr ON c.id = mr.case_id
                WHERE (m.sender_id = %s AND m.sender_role = 'mediator' AND m.message_type = 'system')
                   OR mr.mediator_id IN (SELECT id FROM mediators WHERE user_id = %s)
            """
            params = [user["id"], user["id"]]
            
            if status:
                base_query += " AND c.status = %s"
                params.append(status)
            if keyword:
                base_query += " AND (c.case_number LIKE %s OR c.opponent_name LIKE %s)"
                params.extend([f"%{keyword}%", f"%{keyword}%"])

            # 计数查询
            count_query = f"SELECT COUNT(DISTINCT c.id) as cnt FROM cases c LEFT JOIN messages m ON c.id = m.case_id LEFT JOIN mediation_requests mr ON c.id = mr.case_id WHERE (m.sender_id = %s AND m.sender_role = 'mediator' AND m.message_type = 'system') OR mr.mediator_id IN (SELECT id FROM mediators WHERE user_id = %s)"
            count_params = [user["id"], user["id"]]
            if status:
                count_query += " AND c.status = %s"
                count_params.append(status)
            if keyword:
                count_query += " AND (c.case_number LIKE %s OR c.opponent_name LIKE %s)"
                count_params.extend([f"%{keyword}%", f"%{keyword}%"])
            
            cur.execute(count_query, count_params)
            total = cur.fetchone()["cnt"]

            offset = (page - 1) * page_size
            final_query = f"{base_query} ORDER BY c.updated_at DESC LIMIT %s OFFSET %s"
            cur.execute(final_query, params + [page_size, offset])
            items = rows_to_list(cur.fetchall())
    return make_response({"total": total, "page": page, "page_size": page_size, "items": items})

# ── 通知接口 ────────────────────────────────────────────────
@app.get("/api/v1/notifications", summary="获取通知列表")
def list_notifications(
    page: int = 1, page_size: int = 20, unread_only: bool = False,
    user=Depends(get_current_user)
):
    with get_db() as conn:
        with conn.cursor() as cur:
            # 查询条件
            where = "WHERE user_id = %s"
            params: list = [user["id"]]
            if unread_only:
                where += " AND is_read = 0"
            # 总数
            cur.execute(f"SELECT COUNT(*) as cnt FROM notifications {where}", params)
            total = cur.fetchone()["cnt"]
            # 未读总数（始终查询）
            cur.execute(
                "SELECT COUNT(*) as cnt FROM notifications WHERE user_id = %s AND is_read = 0",
                (user["id"],)
            )
            unread = cur.fetchone()["cnt"]
            # 分页查询
            offset = (page - 1) * page_size
            cur.execute(
                f"SELECT * FROM notifications {where} ORDER BY created_at DESC LIMIT %s OFFSET %s",
                params + [page_size, offset]
            )
            notifs = rows_to_list(cur.fetchall())
    return make_response({"items": notifs, "total": total, "unread_count": unread})

@app.patch("/api/v1/notifications/read-all", summary="全部标记已读")
def mark_all_read(user=Depends(get_current_user)):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE notifications SET is_read = 1 WHERE user_id = %s", (user["id"],))
    return make_response(message="全部已读")

@app.patch("/api/v1/notifications/{notif_id}/read", summary="标记通知为已读")
def mark_read(notif_id: int, user=Depends(get_current_user)):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE notifications SET is_read = 1 WHERE id = %s AND user_id = %s", (notif_id, user["id"]))
    return make_response(message="已标记为已读")

# ── 管理员接口 ──────────────────────────────────────────────
@app.get("/api/v1/admin/dashboard", summary="管理后台统计")
def admin_dashboard(user=Depends(get_current_user)):
    if user["role"] != "platform_admin":
        raise HTTPException(status_code=403, detail="权限不足")
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) as cnt FROM enterprises")
            total_enterprises = cur.fetchone()["cnt"]
            cur.execute("SELECT COUNT(*) as cnt FROM enterprises WHERE audit_status = 'pending'")
            pending_audit = cur.fetchone()["cnt"]
            cur.execute("SELECT COUNT(*) as cnt FROM cases")
            total_cases = cur.fetchone()["cnt"]
            cur.execute("SELECT COUNT(*) as cnt FROM cases WHERE status IN ('negotiating','mediating')")
            active_cases = cur.fetchone()["cnt"]
            cur.execute("SELECT COUNT(*) as cnt FROM mediators WHERE status = 'active'")
            active_mediators = cur.fetchone()["cnt"]
            cur.execute("SELECT COUNT(*) as cnt FROM mediators")
            total_mediators = cur.fetchone()["cnt"]
            cur.execute("SELECT COUNT(*) as cnt FROM users")
            total_users = cur.fetchone()["cnt"]
            cur.execute("SELECT COUNT(*) as cnt FROM cases WHERE MONTH(created_at) = MONTH(NOW()) AND YEAR(created_at) = YEAR(NOW())")
            this_month_cases = cur.fetchone()["cnt"]
            cur.execute("SELECT COUNT(*) as cnt FROM cases WHERE status = 'closed_success'")
            closed_success = cur.fetchone()["cnt"]
            cur.execute("SELECT COUNT(*) as cnt FROM cases WHERE status IN ('closed_success', 'closed_fail')")
            total_closed = cur.fetchone()["cnt"]
            success_rate = round(closed_success / total_closed * 100, 1) if total_closed > 0 else 0
    return make_response({
        "total_enterprises": total_enterprises,
        "pending_audit": pending_audit,
        "total_cases": total_cases,
        "active_mediators": active_mediators,
        "total_mediators": total_mediators,
        "total_users": total_users,
        "active_cases": active_cases,
        "this_month_cases": this_month_cases,
        "success_rate": success_rate
    })

@app.get("/api/v1/admin/enterprises", summary="企业列表（管理员）")
def admin_enterprises(
    audit_status: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = 1, page_size: int = 20,
    user=Depends(get_current_user)
):
    if user["role"] != "platform_admin":
        raise HTTPException(status_code=403, detail="权限不足")
    with get_db() as conn:
        with conn.cursor() as cur:
            where = ["1=1"]
            params: list = []
            if audit_status:
                where.append("audit_status = %s")
                params.append(audit_status)
            if keyword:
                where.append("(name LIKE %s OR credit_code LIKE %s OR legal_person LIKE %s)")
                params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])
            where_clause = " AND ".join(where)
            cur.execute(f"SELECT COUNT(*) as cnt FROM enterprises WHERE {where_clause}", params)
            total = cur.fetchone()["cnt"]
            offset = (page - 1) * page_size
            cur.execute(
                f"SELECT id, name, credit_code, legal_person, contact_phone, audit_status, status, created_at FROM enterprises WHERE {where_clause} ORDER BY created_at DESC LIMIT %s OFFSET %s",
                params + [page_size, offset]
            )
            items = rows_to_list(cur.fetchall())
    return make_response({"total": total, "page": page, "page_size": page_size, "items": items})

@app.get("/api/v1/admin/cases", summary="案件列表（管理员）")
def admin_cases(page: int = 1, page_size: int = 10, status: Optional[str] = None, keyword: Optional[str] = None, user=Depends(get_current_user)):
    if user["role"] != "platform_admin":
        raise HTTPException(status_code=403, detail="权限不足")
    with get_db() as conn:
        with conn.cursor() as cur:
            where = ["1=1"]
            params: list = []
            if status:
                where.append("c.status = %s")
                params.append(status)
            if keyword:
                where.append("(c.case_number LIKE %s OR c.opponent_name LIKE %s)")
                params.extend([f"%{keyword}%", f"%{keyword}%"])
            where_clause = " AND ".join(where)
            cur.execute(f"SELECT COUNT(*) as cnt FROM cases c WHERE {where_clause}", params)
            total = cur.fetchone()["cnt"]
            offset = (page - 1) * page_size
            cur.execute(
                f"""SELECT c.*, e.name as enterprise_name FROM cases c
                   LEFT JOIN enterprises e ON c.enterprise_id = e.id
                   WHERE {where_clause}
                   ORDER BY c.created_at DESC LIMIT %s OFFSET %s""",
                params + [page_size, offset]
            )
            items = rows_to_list(cur.fetchall())
    return make_response({"total": total, "page": page, "page_size": page_size, "items": items})

@app.delete("/api/v1/admin/cases/{case_id}", summary="删除案件")
def delete_case(case_id: int, user=Depends(get_current_user)):
    if user["role"] != "platform_admin":
        raise HTTPException(status_code=403, detail="权限不足")
    try:
        with get_db() as conn:
            conn.begin()
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT id FROM cases WHERE id = %s", (case_id,))
                    if not cur.fetchone():
                        raise HTTPException(status_code=404, detail="案件不存在")
                    cur.execute("DELETE FROM messages WHERE case_id = %s", (case_id,))
                    cur.execute("DELETE FROM evidence WHERE case_id = %s", (case_id,))
                    cur.execute("DELETE FROM cases WHERE id = %s", (case_id,))
                conn.commit()
            except Exception:
                conn.rollback()
                raise
        return make_response(message="案件已删除")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除案件失败: {str(e)}")

@app.get("/api/v1/admin/users", summary="用户列表（管理员）")
def admin_list_users(
    role: Optional[str] = None,
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1, page_size: int = 20,
    user=Depends(get_current_user)
):
    if user["role"] != "platform_admin":
        raise HTTPException(status_code=403, detail="权限不足")
    with get_db() as conn:
        with conn.cursor() as cur:
            where = ["1=1"]
            params: list = []
            if role:
                where.append("u.role = %s")
                params.append(role)
            if status:
                where.append("u.status = %s")
                params.append(status)
            if keyword:
                where.append("(u.real_name LIKE %s OR u.email LIKE %s)")
                params.extend([f"%{keyword}%", f"%{keyword}%"])
            where_clause = " AND ".join(where)
            cur.execute(f"SELECT COUNT(*) as cnt FROM users u WHERE {where_clause}", params)
            total = cur.fetchone()["cnt"]
            offset = (page - 1) * page_size
            cur.execute(
                f"""SELECT u.id, u.email as username, u.email, u.real_name, u.role,
                          u.enterprise_id, e.name as enterprise_name, u.status, u.created_at,
                          m.specialty
                     FROM users u
                     LEFT JOIN enterprises e ON u.enterprise_id = e.id
                     LEFT JOIN mediators m ON u.id = m.user_id
                     WHERE {where_clause}
                     ORDER BY u.id ASC LIMIT %s OFFSET %s""",
                params + [page_size, offset]
            )
            all_users = rows_to_list(cur.fetchall())
            # 角色统计（根据 specialty 细分 mediator）
            cur.execute("""
                SELECT
                    CASE
                        WHEN u.role = 'mediator' AND (m.specialty LIKE '%翻译%' OR m.specialty LIKE '%英语%') THEN 'translator'
                        WHEN u.role = 'mediator' AND (m.specialty LIKE '%数学%' OR m.specialty LIKE '%分析%' OR m.specialty LIKE '%数据%') THEN 'analyst'
                        ELSE u.role
                    END AS role_type,
                    COUNT(*) as cnt
                FROM users u
                LEFT JOIN mediators m ON u.id = m.user_id
                GROUP BY role_type
            """)
            role_counts = {row["role_type"]: row["cnt"] for row in cur.fetchall()}
    return make_response({"total": total, "page": page, "page_size": page_size, "items": all_users, "role_counts": role_counts})

@app.put("/api/v1/admin/users/{user_id}/status", summary="切换用户状态")
def toggle_user_status(user_id: int, data: dict, user=Depends(get_current_user)):
    if user["role"] != "platform_admin":
        raise HTTPException(status_code=403, detail="权限不足")
    new_status = data.get("status", "active")
    if new_status not in ("active", "disabled"):
        raise HTTPException(status_code=400, detail="无效状态")
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE users SET status = %s WHERE id = %s", (new_status, user_id))
    return make_response(message=f"用户状态已更新为 {new_status}")

# ── 管理员操作接口 ──────────────────────────────────────────
@app.post("/api/v1/admin/enterprises/{enterprise_id}/audit", summary="审核企业")
def audit_enterprise(enterprise_id: int, data: dict, user=Depends(get_current_user)):
    if user["role"] != "platform_admin":
        raise HTTPException(status_code=403, detail="权限不足")
    action = data.get("action", "approve")
    new_status = "approved" if action == "approve" else "rejected"
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE enterprises SET audit_status = %s WHERE id = %s",
                (new_status, enterprise_id)
            )
    return make_response(message=f"企业已{'通过审核' if action == 'approve' else '拒绝'}")

@app.get("/api/v1/admin/mediators", summary="管理员获取调解员列表")
def admin_list_mediators(page: int = 1, page_size: int = 50, staff_type: Optional[str] = None, user=Depends(get_current_user)):
    if user["role"] != "platform_admin":
        raise HTTPException(status_code=403, detail="权限不足")
    with get_db() as conn:
        with conn.cursor() as cur:
            where_clause = ""
            params = []
            # staff_type 过滤：目前 mediators 表无 staff_type 列，
            # 通过 users.role 来区分 mediator / translator / analyst
            if staff_type and staff_type in ("mediator", "translator", "analyst"):
                where_clause = "WHERE u.role = %s"
                params.append(staff_type)
            cur.execute(f"SELECT COUNT(*) as total FROM mediators m LEFT JOIN users u ON m.user_id = u.id {where_clause}", params)
            total = cur.fetchone()["total"]
            offset = (page - 1) * page_size
            query_params = params + [page_size, offset]
            cur.execute(f"""
                SELECT m.*, u.email, u.real_name, u.role as user_role
                FROM mediators m
                LEFT JOIN users u ON m.user_id = u.id
                {where_clause}
                ORDER BY m.id DESC LIMIT %s OFFSET %s
            """, query_params)
            rows = cur.fetchall()
            items = []
            for r in rows:
                items.append({
                    "id": r["id"],
                    "real_name": r.get("real_name") or r["name"],
                    "email": r.get("email", ""),
                    "domain": r.get("specialty", ""),
                    "success_rate": float(r["success_rate"]) if r.get("success_rate") is not None else 0,
                    "rating": float(r["rating"]) if r.get("rating") is not None else 0,
                    "status": r["status"],
                    "staff_type": r.get("user_role", "mediator"),  # 用 user.role 作为 staff_type
                })
    return make_response(items)

@app.post("/api/v1/admin/mediators", summary="创建调解员")
def create_mediator(data: dict, user=Depends(get_current_user)):
    if user["role"] != "platform_admin":
        raise HTTPException(status_code=403, detail="权限不足")

    real_name = data.get("real_name", "").strip()
    email = data.get("email", "").strip()
    phone = data.get("phone", "").strip()
    domain = data.get("domain", "").strip()
    intro = data.get("intro", "").strip()
    staff_type = data.get("staff_type", "mediator").strip()
    if staff_type not in ("mediator", "translator", "analyst"):
        staff_type = "mediator"

    if not real_name or not email:
        raise HTTPException(status_code=400, detail="姓名和邮箱不能为空")

    # 创建用户账号（生成随机初始密码）
    import string as _string
    initial_pwd = ''.join(secrets.choice(_string.ascii_letters + _string.digits + '!@#$%') for _ in range(12))
    new_id = None
    try:
        with get_db() as conn:
            conn.begin()
            try:
                with conn.cursor() as cur:
                    # 检查邮箱是否已存在
                    cur.execute("SELECT id FROM users WHERE email = %s", (email,))
                    existing = cur.fetchone()
                    if existing:
                        raise HTTPException(status_code=400, detail="该邮箱已被注册")

                    cur.execute(
                        """INSERT INTO users (email, password_hash, real_name, role, status)
                           VALUES (%s, %s, %s, %s, 'active')""",
                        (email, hash_password(initial_pwd), real_name, staff_type)
                    )
                    new_user_id = cur.lastrowid

                    # 创建调解员记录
                    cur.execute(
                        """INSERT INTO mediators (user_id, name, specialty, success_rate, rating, cases_count, bio, status)
                           VALUES (%s, %s, %s, 0, 5.0, 0, %s, 'active')""",
                        (new_user_id, real_name, domain, intro)
                    )
                    new_id = cur.lastrowid
                conn.commit()
            except HTTPException:
                conn.rollback()
                raise
            except Exception:
                conn.rollback()
                raise
        return make_response({"id": new_id}, message=f"调解员账号已创建，初始密码为 {initial_pwd}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建调解员失败: {str(e)}")

@app.delete("/api/v1/admin/mediators/{mediator_id}", summary="删除调解员")
def delete_mediator(mediator_id: int, user=Depends(get_current_user)):
    if user["role"] != "platform_admin":
        raise HTTPException(status_code=403, detail="权限不足")
    try:
        with get_db() as conn:
            conn.begin()
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT id, user_id FROM mediators WHERE id = %s", (mediator_id,))
                    m = cur.fetchone()
                    if not m:
                        raise HTTPException(status_code=404, detail="调解员不存在")
                    cur.execute("DELETE FROM mediators WHERE id = %s", (mediator_id,))
                    if m.get("user_id"):
                        cur.execute("DELETE FROM users WHERE id = %s", (m["user_id"],))
                conn.commit()
            except Exception:
                conn.rollback()
                raise
        return make_response(message="调解员已删除")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除调解员失败: {str(e)}")

@app.put("/api/v1/admin/mediators/{mediator_id}", summary="更新调解员信息")
def update_mediator(mediator_id: int, data: dict, user=Depends(get_current_user)):
    """更新调解员/人员的姓名、专业领域、评分等信息"""
    if user["role"] != "platform_admin":
        raise HTTPException(status_code=403, detail="权限不足")
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, user_id FROM mediators WHERE id = %s", (mediator_id,))
                m = cur.fetchone()
                if not m:
                    raise HTTPException(status_code=404, detail="人员不存在")
                # 可更新的字段
                name = data.get("name") or data.get("real_name")
                specialty = data.get("specialty") or data.get("domain")
                rating = data.get("rating")
                bio = data.get("bio") or data.get("intro")
                staff_type = data.get("staff_type")
                # 构建动态 UPDATE
                updates = []
                params = []
                if name is not None:
                    updates.append("name = %s")
                    params.append(name)
                    # 同步更新 users.real_name
                    cur.execute("UPDATE users SET real_name = %s WHERE id = %s", (name, m["user_id"]))
                if specialty is not None:
                    updates.append("specialty = %s")
                    params.append(specialty)
                if rating is not None:
                    try:
                        rating_val = float(rating)
                        updates.append("rating = %s")
                        params.append(rating_val)
                    except (ValueError, TypeError):
                        pass
                if bio is not None:
                    updates.append("bio = %s")
                    params.append(bio)
                if staff_type is not None and staff_type in ("mediator", "translator", "analyst"):
                    # 同步更新 users.role 以保持类型一致
                    cur.execute("UPDATE users SET role = %s WHERE id = %s", (staff_type, m["user_id"]))
                if updates:
                    params.append(mediator_id)
                    cur.execute(f"UPDATE mediators SET {', '.join(updates)} WHERE id = %s", params)
        return make_response(message="人员信息已更新")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新人员信息失败: {str(e)}")

@app.put("/api/v1/admin/mediators/{mediator_id}/status", summary="更新调解员状态")
def update_mediator_status(mediator_id: int, data: dict, user=Depends(get_current_user)):
    if user["role"] != "platform_admin":
        raise HTTPException(status_code=403, detail="权限不足")
    new_status = data.get("status", "active")
    if new_status not in ("active", "vacation", "disabled"):
        raise HTTPException(status_code=400, detail="无效状态，可选: active/vacation/disabled")
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM mediators WHERE id = %s", (mediator_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="调解员不存在")
            cur.execute("UPDATE mediators SET status = %s WHERE id = %s", (new_status, mediator_id))
            if new_status == "disabled":
                cur.execute("UPDATE users SET status = 'disabled' WHERE id = (SELECT user_id FROM mediators WHERE id = %s)", (mediator_id,))
            elif new_status == "active":
                cur.execute("UPDATE users SET status = 'active' WHERE id = (SELECT user_id FROM mediators WHERE id = %s)", (mediator_id,))
    return make_response(message=f"调解员状态已更新为 {new_status}")

@app.get("/api/v1/cases/{case_id}/progress", summary="获取案件进程")
def get_case_progress(case_id: int, user=Depends(get_current_user)):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM cases WHERE id = %s", (case_id,))
            case = cur.fetchone()
            if not case:
                raise HTTPException(status_code=404, detail="案件不存在")
            cur.execute("SELECT * FROM evidence WHERE case_id = %s ORDER BY created_at", (case_id,))
            evidence = rows_to_list(cur.fetchall())
            cur.execute("SELECT * FROM messages WHERE case_id = %s ORDER BY created_at", (case_id,))
            messages = rows_to_list(cur.fetchall())
            cur.execute("SELECT * FROM mediation_requests WHERE case_id = %s ORDER BY created_at", (case_id,))
            mediations = rows_to_list(cur.fetchall())
    timeline = [
        {"time": case["created_at"].isoformat() if isinstance(case["created_at"], datetime) else str(case.get("created_at", "")), "event": "案件创建", "type": "create"},
    ]
    for e in evidence:
        timeline.append({"time": str(e.get("created_at", "")), "event": f"上传证据: {e.get('file_name', '')}", "type": "evidence"})
    for m in messages:
        timeline.append({"time": str(m.get("created_at", "")), "event": f"{m.get('sender_name', '')}: {str(m.get('content', ''))[:50]}", "type": "message"})
    for med in mediations:
        timeline.append({"time": str(med.get("created_at", "")), "event": f"调解申请: {med.get('status', '')}", "type": "mediation"})
    timeline.sort(key=lambda x: x["time"], reverse=False)
    return make_response({
        "case": row_to_dict(case),
        "timeline": timeline,
        "evidence_count": len(evidence),
        "message_count": len(messages),
        "mediations": mediations,
    })

@app.get("/api/v1/users/online-status", summary="检查用户在线状态")
def check_online_status(user=Depends(get_current_user)):
    """检查当前用户以外是否有人在线（基于最近token活跃时间）"""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) as cnt FROM tokens WHERE user_id != %s AND expires_at > NOW()", (user["id"],))
            online_count = cur.fetchone()["cnt"]
    return make_response({"online": online_count > 0, "online_count": online_count})

class MediatorInterveneRequest(BaseModel):
    case_id: int
    mediator_id: int

@app.post("/api/v1/negotiation/mediator-intervene", summary="调解员介入协商")
def mediator_intervene(req: MediatorInterveneRequest, user=Depends(get_current_user)):
    try:
        with get_db() as conn:
            conn.begin()
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM mediators WHERE id = %s", (req.mediator_id,))
                    mediator = cur.fetchone()
                    if not mediator:
                        raise HTTPException(status_code=404, detail="调解员不存在")
                    cur.execute("SELECT * FROM cases WHERE id = %s", (req.case_id,))
                    case = cur.fetchone()
                    if not case:
                        raise HTTPException(status_code=404, detail="案件不存在")
                    
                    # 发送系统消息 - sender_id 存 users.id（用于调解员查询自己的案件）
                    cur.execute("""
                        INSERT INTO messages (case_id, sender_id, sender_name, sender_role, message_type, content)
                        VALUES (%s, %s, %s, %s, 'system', %s)
                    """, (req.case_id, mediator["user_id"], mediator["name"], "mediator",
                          f"调解员 {mediator['name']} 已介入本次协商"))
                    
                    # 更新案件状态为调解中，并关联调解员
                    cur.execute(
                        "UPDATE cases SET status = 'mediating', mediator_id = %s WHERE id = %s",
                        (req.mediator_id, req.case_id)
                    )
                    
                    # 创建或更新调解申请记录
                    cur.execute(
                        "SELECT id FROM mediation_requests WHERE case_id = %s ORDER BY id DESC LIMIT 1",
                        (req.case_id,)
                    )
                    existing_req = cur.fetchone()
                    if existing_req:
                        cur.execute(
                            "UPDATE mediation_requests SET mediator_id = %s, status = 'mediator_selected' WHERE id = %s",
                            (req.mediator_id, existing_req["id"])
                        )
                    else:
                        cur.execute(
                            "INSERT INTO mediation_requests (case_id, mediator_id, status) VALUES (%s, %s, 'mediator_selected')",
                            (req.case_id, req.mediator_id)
                        )
                    
                    cur.execute("SELECT * FROM messages WHERE case_id = %s ORDER BY id DESC LIMIT 1", (req.case_id,))
                    msg = cur.fetchone()
                conn.commit()
            except Exception:
                conn.rollback()
                raise
        return make_response(row_to_dict(msg), message=f"调解员 {mediator['name']} 已介入")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"调解员介入失败: {str(e)}")

# ── 健康检查 ────────────────────────────────────────────────
@app.get("/api/health", summary="健康检查")
def health():
    # 检查数据库连接
    db_ok = False
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
            db_ok = True
    except Exception:
        pass
    return {
        "status": "ok" if db_ok else "degraded",
        "service": "智链解纷 API",
        "database": "MySQL" if db_ok else "disconnected",
        "time": datetime.now().isoformat(),
        "mode": "PRODUCTION (MySQL)"
    }

@app.get("/", summary="API根路径")
def root():
    return {
        "name": "智链解纷 - 中国东盟跨境商事纠纷在线解决平台",
        "version": "1.1.0",
        "mode": "MySQL",
        "docs": "/api/docs",
        "health": "/api/health",
    }

# ── 启动时清理过期Token ─────────────────────────────────────
@app.on_event("startup")
def cleanup_expired_tokens():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM tokens WHERE expires_at < NOW()")
            deleted = cur.rowcount
    if deleted > 0:
        print(f"[启动] 已清理 {deleted} 个过期Token")

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("  智链解纷 后端服务器 (MySQL)")
    print("  数据库: zjfl @ localhost:3306")
    print("  API文档: http://localhost:8000/api/docs")
    print("  健康检查: http://localhost:8000/api/health")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
