"""初始化 ZJFL 数据库和表结构"""
import pymysql
import secrets
import hashlib

conn = pymysql.connect(host='localhost', user='root', password='lzz1212147474', charset='utf8mb4')
cursor = conn.cursor()

def hash_password(password: str) -> str:
    """使用 SHA-256 + salt 哈希（演示模式）"""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()
    return f"{salt}${hashed}"

# 创建数据库
cursor.execute("CREATE DATABASE IF NOT EXISTS zjfl DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
cursor.execute("USE zjfl")

# 清理可能存在的旧表（按外键依赖顺序删除）
cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
for tbl in ['tokens', 'notifications', 'messages', 'evidence', 'meetings', 'mediation_requests', 'mediators', 'cases', 'users', 'enterprises']:
    cursor.execute(f"DROP TABLE IF EXISTS {tbl}")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

# 建表SQL
cursor.execute("""
CREATE TABLE enterprises (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    credit_code VARCHAR(50) NOT NULL,
    legal_person VARCHAR(100) DEFAULT NULL,
    contact_phone VARCHAR(30) DEFAULT NULL,
    address VARCHAR(500) DEFAULT NULL,
    audit_status ENUM('pending','approved','rejected') DEFAULT 'pending',
    status ENUM('active','disabled') DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_credit_code (credit_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
""")

cursor.execute("""
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(200) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    real_name VARCHAR(100) NOT NULL,
    role ENUM('platform_admin','enterprise_admin','enterprise_user','mediator') NOT NULL DEFAULT 'enterprise_admin',
    enterprise_id INT DEFAULT NULL,
    mediator_domain VARCHAR(500) DEFAULT NULL COMMENT '调解专业领域(回退)',
    status ENUM('active','disabled','pending') DEFAULT 'active',
    language VARCHAR(20) DEFAULT 'zh-CN',
    notify_email TINYINT(1) DEFAULT 1,
    notify_sms TINYINT(1) DEFAULT 0,
    avatar VARCHAR(500) DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_email (email),
    KEY idx_enterprise (enterprise_id),
    CONSTRAINT fk_user_enterprise FOREIGN KEY (enterprise_id) REFERENCES enterprises(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
""")

cursor.execute("""
CREATE TABLE mediators (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT DEFAULT NULL,
    name VARCHAR(100) NOT NULL,
    specialty VARCHAR(500) DEFAULT NULL,
    success_rate DECIMAL(5,2) DEFAULT 0.00,
    rating DECIMAL(3,1) DEFAULT 0.0,
    cases_count INT DEFAULT 0,
    bio TEXT,
    status ENUM('active','disabled') DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_mediator_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
""")

cursor.execute("""
CREATE TABLE cases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_number VARCHAR(50) NOT NULL,
    enterprise_id INT NOT NULL,
    mediator_id INT DEFAULT NULL,
    opponent_name VARCHAR(200) NOT NULL,
    opponent_country VARCHAR(100) NOT NULL,
    contract_type VARCHAR(100) DEFAULT NULL,
    amount DECIMAL(15,2) DEFAULT 0.00,
    dispute_desc TEXT,
    expected_method ENUM('negotiation','mediation','litigation') DEFAULT 'mediation',
    status ENUM('negotiating','mediating','closed_success','closed_fail','draft') DEFAULT 'draft',
    contract_date DATE DEFAULT NULL,
    incident_date DATE DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_case_number (case_number),
    KEY idx_enterprise (enterprise_id),
    KEY idx_mediator (mediator_id),
    KEY idx_status (status),
    CONSTRAINT fk_case_enterprise FOREIGN KEY (enterprise_id) REFERENCES enterprises(id),
    CONSTRAINT fk_case_mediator FOREIGN KEY (mediator_id) REFERENCES mediators(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
""")

cursor.execute("""
CREATE TABLE evidence (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    file_name VARCHAR(500) NOT NULL,
    evidence_type VARCHAR(100) DEFAULT NULL,
    file_hash VARCHAR(128) DEFAULT NULL,
    storage_voucher VARCHAR(200) DEFAULT NULL,
    file_path VARCHAR(1000) DEFAULT NULL,
    file_size BIGINT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    KEY idx_case (case_id),
    CONSTRAINT fk_evidence_case FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
""")

cursor.execute("""
CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    sender_id INT DEFAULT NULL,
    sender_name VARCHAR(100) NOT NULL,
    sender_role VARCHAR(50) DEFAULT NULL,
    message_type ENUM('text','file','image','system') DEFAULT 'text',
    content TEXT,
    file_name VARCHAR(255) DEFAULT NULL,
    file_size VARCHAR(50) DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    KEY idx_case (case_id),
    KEY idx_created (created_at),
    CONSTRAINT fk_message_case FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
""")

cursor.execute("""
CREATE TABLE mediation_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    demand_text TEXT,
    mediator_id INT DEFAULT NULL,
    status ENUM('pending','mediator_selected','mediating','completed','failed') DEFAULT 'pending',
    result VARCHAR(200) DEFAULT NULL,
    agreement_id VARCHAR(100) DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_case (case_id),
    KEY idx_status (status),
    CONSTRAINT fk_medreq_case FOREIGN KEY (case_id) REFERENCES cases(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
""")

cursor.execute("""
CREATE TABLE meetings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    mediator_id INT DEFAULT NULL,
    channel_name VARCHAR(100) NOT NULL,
    scheduled_time DATETIME NOT NULL,
    note TEXT,
    status ENUM('scheduled','ongoing','ended','cancelled') DEFAULT 'scheduled',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_case (case_id),
    KEY idx_mediator (mediator_id),
    KEY idx_status (status),
    CONSTRAINT fk_meeting_case FOREIGN KEY (case_id) REFERENCES cases(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
""")

cursor.execute("""
CREATE TABLE notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    type ENUM('case','meeting','system','message') DEFAULT 'system',
    title VARCHAR(200) NOT NULL,
    content TEXT,
    is_read TINYINT(1) DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    KEY idx_user_read (user_id, is_read),
    KEY idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
""")

cursor.execute("""
CREATE TABLE tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    token VARCHAR(128) NOT NULL,
    user_id INT NOT NULL,
    expires_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_token (token),
    KEY idx_expires (expires_at),
    CONSTRAINT fk_token_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
""")

# 插入初始演示数据
cursor.execute("""
INSERT INTO enterprises (id, name, credit_code, legal_person, contact_phone, audit_status, status) VALUES
(1, '演示贸易有限公司', '91110105DEMO0001', '张明', '13800000001', 'approved', 'active'),
(2, '测试科技有限公司', '91110105TEST0002', '李华', '13800000002', 'pending', 'active')
""")

# 插入用户数据（使用哈希密码）
cursor.execute("""
INSERT INTO users (id, email, password_hash, real_name, role, enterprise_id, status) VALUES
(1, 'admin@zjfl.com', %s, '平台管理员', 'platform_admin', NULL, 'active'),
(2, 'demo@zjfl.com', %s, '演示企业管理元', 'enterprise_admin', 1, 'active'),
(3, 'mediator_li@zjfl.com', %s, '李建国', 'mediator', NULL, 'active'),
(4, 'mediator_chen@zjfl.com', %s, '陈美华', 'mediator', NULL, 'active'),
(5, 'mediator_zhang@zjfl.com', %s, '张文远', 'mediator', NULL, 'active'),
(6, 'mediator_lin@zjfl.com', %s, '林晓敏', 'mediator', NULL, 'active'),
(7, 'mediator_wang@zjfl.com', %s, '王建明', 'mediator', NULL, 'active'),
(8, 'liyunmei@zjfl.com', %s, '李云梅', 'mediator', NULL, 'active'),
(9, 'zhuanting@zjfl.com', %s, '朱安婷', 'mediator', NULL, 'active'),
(10, 'xiaoyijun@zjfl.com', %s, '肖怡君', 'mediator', NULL, 'active'),
(11, 'tangbowen@zjfl.com', %s, '唐博闻', 'mediator', NULL, 'active'),
(12, 'tangxinyang@zjfl.com', %s, '唐心阳', 'mediator', NULL, 'active'),
(13, 'litongtong@zjfl.com', %s, '黎彤彤', 'mediator', NULL, 'active'),
(14, 'menghaidong@zjfl.com', %s, '蒙海东', 'mediator', NULL, 'active'),
(15, 'anqi@zjfl.com', %s, '安奇', 'mediator', NULL, 'active'),
(16, 'chenjianning@zjfl.com', %s, '陈建凝', 'mediator', NULL, 'active')
""", [
    hash_password('admin123'),
    hash_password('Demo@12345'),
    hash_password('Mediator@123'),
    hash_password('Mediator@123'),
    hash_password('Mediator@123'),
    hash_password('Mediator@123'),
    hash_password('Mediator@123'),
    hash_password('Mediator@123'),
    hash_password('Mediator@123'),
    hash_password('Mediator@123'),
    hash_password('Mediator@123'),
    hash_password('Mediator@123'),
    hash_password('Mediator@123'),
    hash_password('Mediator@123'),
    hash_password('Mediator@123'),
    hash_password('Mediator@123'),
])

cursor.execute("""
INSERT INTO cases (id, case_number, enterprise_id, opponent_name, opponent_country, contract_type, amount, dispute_desc, expected_method, status, created_at) VALUES
(1, 'CASE202504170001', 1, '越南河内贸易有限公司', 'VN', 'goods_sale', 85000.00, '对方未按合同约定时间交货，导致我方损失', 'mediation', 'negotiating', '2026-04-10 09:00:00'),
(2, 'CASE202504150002', 1, '泰国曼谷物流公司', 'TH', 'logistics', 32000.00, '货物在运输途中损毁，对方拒绝赔偿', 'mediation', 'mediating', '2026-04-08 14:30:00'),
(3, 'CASE202504050003', 1, '马来西亚吉隆坡电子科技', 'MY', 'cross_border_ecom', 15600.00, '平台交易纠纷，已协商达成一致', 'negotiation', 'closed_success', '2026-03-20 10:00:00')
""")

cursor.execute("""
INSERT INTO mediators (id, user_id, name, specialty, success_rate, rating, cases_count, bio, status) VALUES
(1, 3, '李建国', '货物买卖/国际贸易', 92.5, 4.9, 156, '前商务部国际贸易仲裁员，从事跨境贸易纠纷调解20年', 'active'),
(2, 4, '陈美华', '跨境电商/知识产权', 88.3, 4.8, 98, '电子商务法律专家，精通东盟各国电商法规', 'active'),
(3, 5, '张文远', '物流运输/保险', 90.1, 4.7, 203, '国际物流法律顾问，熟悉多式联运公约', 'active'),
(4, 6, '林晓敏', '投资合作/合同纠纷', 85.7, 4.6, 74, '东南亚投资法律专家，持有多国律师执照', 'active'),
(5, 7, '王建明', '金融结算/信用证', 94.2, 4.9, 112, '银行国际结算部前主管，信用证纠纷权威', 'active'),
(6, 8, '李云梅', '法学', 87.0, 4.7, 68, '资深法律专家，专注跨境贸易纠纷调解', 'active'),
(7, 9, '朱安婷', '法学', 89.5, 4.8, 52, '法学硕士，擅长合同纠纷处理', 'active'),
(8, 10, '肖怡君', '法学', 85.0, 4.6, 45, '执业律师，专注国际商事调解', 'active'),
(9, 11, '唐博闻', '法学', 88.0, 4.7, 60, '法律顾问，精通贸易法与仲裁程序', 'active'),
(10, 12, '唐心阳', '商务英语/翻译', 90.0, 4.9, 38, '专业翻译，精通中英双语商务沟通', 'active'),
(11, 13, '黎彤彤', '商务英语/翻译', 88.5, 4.8, 32, '资深翻译，参与多起跨境调解案件', 'active'),
(12, 14, '蒙海东', '数学与应用数学/数据分析', 86.0, 4.6, 28, '数据分析师，提供纠纷量化分析支持', 'active'),
(13, 15, '安奇', '数学与应用数学/数据分析', 84.5, 4.5, 25, '数学专业，专注纠纷数据模型分析', 'active'),
(14, 16, '陈建凝', '数学与应用数学/数据分析', 87.5, 4.7, 30, '统计专家，提供调解决策数据支持', 'active')
""")

cursor.execute("""
INSERT INTO notifications (id, user_id, type, title, content, is_read, created_at) VALUES
(1, 2, 'case', '案件状态更新', '案件 CASE202504170001 已进入调解阶段，请关注进展', 0, '2026-04-17 08:30:00'),
(2, 2, 'meeting', '调解会议通知', '您有一场调解会议将于明天 14:00 开始，请提前准备', 0, '2026-04-16 15:00:00'),
(3, 2, 'system', '系统公告', '智链解纷平台V1.1版本已发布，新增多语言支持', 1, '2026-04-15 09:00:00')
""")

cursor.execute("""
INSERT INTO evidence (id, case_id, file_name, evidence_type, file_hash, storage_voucher, created_at) VALUES
(1, 1, 'purchase_contract_2026.pdf', '合同', 'a1b2c3d4e5f6...', 'CERT-2026-0001', '2026-04-10 09:30:00'),
(2, 1, 'delivery_schedule.xlsx', '提单', 'b2c3d4e5f6a1...', 'CERT-2026-0002', '2026-04-10 09:35:00'),
(3, 1, 'wechat_chat_record.jpg', '聊天记录', 'c3d4e5f6a1b2...', 'CERT-2026-0003', '2026-04-11 14:20:00')
""")

cursor.execute("""
INSERT INTO messages (id, case_id, sender_id, sender_name, sender_role, message_type, content, created_at) VALUES
(1, 1, 2, '演示企业管理元', 'enterprise_admin', 'text', '您好，我们是原告方，关于本次货物买卖合同纠纷，希望贵方能够认真对待。', '2026-04-12 10:00:00'),
(2, 1, NULL, '越南河内贸易', 'opponent', 'text', '我们理解贵方的诉求，但延误交货是由于不可抗力因素导致，我们愿意就赔偿金额进行协商。', '2026-04-12 10:15:00'),
(3, 1, 2, '演示企业管理元', 'enterprise_admin', 'text', '请贵方提供相关证明文件，我们将认真审查。如协商无法达成一致，我们将申请专业调解。', '2026-04-12 10:30:00')
""")

conn.commit()

# 验证
cursor.execute("SHOW TABLES")
tables = cursor.fetchall()
print("Tables created:")
for t in tables:
    print(f"  - {t[0]}")

for tbl in ['enterprises', 'users', 'cases', 'mediators', 'notifications', 'evidence', 'messages']:
    cursor.execute(f"SELECT COUNT(*) FROM {tbl}")
    cnt = cursor.fetchone()[0]
    print(f"  {tbl}: {cnt} rows")

cursor.close()
conn.close()
print("Database init complete!")
