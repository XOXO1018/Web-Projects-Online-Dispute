-- =============================================
-- 智链解纷 数据库初始化脚本
-- PostgreSQL 15+
-- =============================================

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================
-- 枚举类型
-- =============================================

DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('platform_admin', 'enterprise_admin', 'legal', 'salesperson', 'mediator');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE user_status AS ENUM ('pending', 'active', 'disabled');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE audit_status AS ENUM ('pending', 'approved', 'rejected');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE case_status AS ENUM (
        'negotiating', 'mediating',
        'closed_negotiation', 'closed_mediation', 'closed_failed', 'archived'
    );
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE contract_type AS ENUM ('goods_sale', 'cross_border_ecom', 'logistics', 'other');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE dispute_method AS ENUM ('negotiation', 'mediation', 'arbitration');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE evidence_type AS ENUM ('contract', 'bill_of_lading', 'customs', 'invoice', 'chat_record', 'other');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE message_type AS ENUM ('text', 'image', 'voice', 'system');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE notification_type AS ENUM ('internal', 'email', 'sms');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE mediation_status AS ENUM ('pending', 'assigned', 'in_progress', 'completed', 'failed');
EXCEPTION WHEN duplicate_object THEN null; END $$;

-- =============================================
-- 表结构
-- =============================================

-- 企业表
CREATE TABLE IF NOT EXISTS enterprises (
    id SERIAL PRIMARY KEY,
    credit_code VARCHAR(18) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    legal_person VARCHAR(50) NOT NULL,
    legal_id_card VARCHAR(255) NOT NULL,
    business_license VARCHAR(100) NOT NULL,
    contact_phone VARCHAR(255) NOT NULL,
    contact_email VARCHAR(200) NOT NULL,
    audit_status audit_status DEFAULT 'pending',
    audit_note TEXT,
    country VARCHAR(50) DEFAULT 'CN',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    enterprise_id INTEGER REFERENCES enterprises(id) ON DELETE SET NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    phone VARCHAR(255) NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL,
    real_name VARCHAR(50) NOT NULL,
    id_card VARCHAR(255),
    status user_status DEFAULT 'pending',
    must_change_password BOOLEAN DEFAULT FALSE,
    mediator_domain VARCHAR(200),
    mediator_intro TEXT,
    mediator_success_rate NUMERIC(5,2) DEFAULT 0.00,
    mediator_rating NUMERIC(3,2) DEFAULT 5.00,
    mediator_case_count INTEGER DEFAULT 0,
    notify_email BOOLEAN DEFAULT TRUE,
    notify_sms BOOLEAN DEFAULT FALSE,
    language VARCHAR(10) DEFAULT 'zh-CN',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS ix_users_email ON users(email);
CREATE INDEX IF NOT EXISTS ix_users_role ON users(role);
CREATE INDEX IF NOT EXISTS ix_users_enterprise_id ON users(enterprise_id);

-- 案件表
CREATE TABLE IF NOT EXISTS cases (
    id SERIAL PRIMARY KEY,
    case_number VARCHAR(30) UNIQUE NOT NULL,
    enterprise_id INTEGER NOT NULL REFERENCES enterprises(id),
    created_by_user_id INTEGER NOT NULL REFERENCES users(id),
    opponent_name VARCHAR(200) NOT NULL,
    opponent_country VARCHAR(50) NOT NULL,
    contract_type contract_type NOT NULL,
    amount NUMERIC(15,2) NOT NULL,
    dispute_desc TEXT NOT NULL,
    contract_date TIMESTAMPTZ NOT NULL,
    incident_date TIMESTAMPTZ NOT NULL,
    expected_method dispute_method NOT NULL,
    status case_status DEFAULT 'negotiating',
    negotiation_started_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ,
    close_summary TEXT,
    timeline JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS ix_cases_enterprise_id ON cases(enterprise_id);
CREATE INDEX IF NOT EXISTS ix_cases_status ON cases(status);
CREATE INDEX IF NOT EXISTS ix_cases_case_number ON cases(case_number);

-- 证据表
CREATE TABLE IF NOT EXISTS evidences (
    id SERIAL PRIMARY KEY,
    case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    uploaded_by_user_id INTEGER NOT NULL REFERENCES users(id),
    file_name VARCHAR(255) NOT NULL,
    file_url VARCHAR(500) NOT NULL,
    file_size INTEGER,
    file_mime VARCHAR(100),
    file_hash VARCHAR(64) NOT NULL,
    evidence_type evidence_type NOT NULL,
    timestamp_cert VARCHAR(500),
    storage_voucher VARCHAR(200),
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_evidences_case_id ON evidences(case_id);

-- 协商消息表
CREATE TABLE IF NOT EXISTS negotiation_messages (
    id SERIAL PRIMARY KEY,
    case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    sender_id INTEGER NOT NULL REFERENCES users(id),
    message_type message_type DEFAULT 'text',
    content TEXT,
    voice_text TEXT,
    is_system BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_messages_case_id ON negotiation_messages(case_id);

-- 协商结果表
CREATE TABLE IF NOT EXISTS negotiation_results (
    id SERIAL PRIMARY KEY,
    case_id INTEGER UNIQUE REFERENCES cases(id),
    summary TEXT NOT NULL,
    memo_url VARCHAR(500),
    plaintiff_signed BOOLEAN DEFAULT FALSE,
    plaintiff_signed_by VARCHAR(50),
    plaintiff_signed_at TIMESTAMPTZ,
    defendant_signed BOOLEAN DEFAULT FALSE,
    defendant_signed_by VARCHAR(50),
    defendant_signed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 调解申请表
CREATE TABLE IF NOT EXISTS mediation_requests (
    id SERIAL PRIMARY KEY,
    case_id INTEGER NOT NULL REFERENCES cases(id),
    applicant_id INTEGER NOT NULL REFERENCES users(id),
    selected_mediator_id INTEGER REFERENCES users(id),
    mediator_assigned_id INTEGER REFERENCES users(id),
    demand_text TEXT NOT NULL,
    status mediation_status DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- 调解会议表
CREATE TABLE IF NOT EXISTS mediation_meetings (
    id SERIAL PRIMARY KEY,
    request_id INTEGER NOT NULL REFERENCES mediation_requests(id),
    meeting_link VARCHAR(500),
    channel_name VARCHAR(100),
    scheduled_time TIMESTAMPTZ NOT NULL,
    actual_start_time TIMESTAMPTZ,
    actual_end_time TIMESTAMPTZ,
    recording_url VARCHAR(500),
    transcript_text TEXT,
    mediator_opinion TEXT,
    status VARCHAR(20) DEFAULT 'scheduled',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 调解协议表
CREATE TABLE IF NOT EXISTS mediation_agreements (
    id SERIAL PRIMARY KEY,
    case_id INTEGER NOT NULL REFERENCES cases(id),
    agreement_content TEXT,
    agreement_pdf_url VARCHAR(500),
    signed_by_plaintiff BOOLEAN DEFAULT FALSE,
    plaintiff_sign_time TIMESTAMPTZ,
    plaintiff_signer_name VARCHAR(50),
    signed_by_defendant BOOLEAN DEFAULT FALSE,
    defendant_sign_time TIMESTAMPTZ,
    defendant_signer_name VARCHAR(50),
    signed_at TIMESTAMPTZ,
    esign_cert_id VARCHAR(200),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 通知表
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    type notification_type DEFAULT 'internal',
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    related_case_id INTEGER REFERENCES cases(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS ix_notifications_is_read ON notifications(is_read);

-- 操作日志表
CREATE TABLE IF NOT EXISTS operation_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id INTEGER,
    detail JSONB,
    ip VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_logs_user_id ON operation_logs(user_id);

-- 验证码表
CREATE TABLE IF NOT EXISTS verification_codes (
    id SERIAL PRIMARY KEY,
    target VARCHAR(200) NOT NULL,
    code VARCHAR(10) NOT NULL,
    purpose VARCHAR(50),
    is_used BOOLEAN DEFAULT FALSE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
