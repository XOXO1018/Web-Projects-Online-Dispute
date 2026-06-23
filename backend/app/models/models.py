"""
数据库模型定义 - 所有核心表
"""
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, Numeric,
    ForeignKey, Enum as SAEnum, JSON, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


# ==================== 枚举类型 ====================

class UserRole(str, enum.Enum):
    PLATFORM_ADMIN = "platform_admin"     # 平台管理员
    ENTERPRISE_ADMIN = "enterprise_admin"  # 企业管理员
    LEGAL = "legal"                        # 法务
    SALESPERSON = "salesperson"            # 业务员
    MEDIATOR = "mediator"                  # 调解员


class UserStatus(str, enum.Enum):
    PENDING = "pending"      # 待审核
    ACTIVE = "active"        # 已激活
    DISABLED = "disabled"    # 已禁用


class AuditStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class CaseStatus(str, enum.Enum):
    NEGOTIATING = "negotiating"          # 协商中
    MEDIATING = "mediating"              # 调解中
    CLOSED_NEGOTIATION = "closed_negotiation"  # 协商成功
    CLOSED_MEDIATION = "closed_mediation"      # 调解成功
    CLOSED_FAILED = "closed_failed"            # 调解失败
    ARCHIVED = "archived"                      # 已归档


class ContractType(str, enum.Enum):
    GOODS_SALE = "goods_sale"          # 货物买卖
    CROSS_BORDER_ECOM = "cross_border_ecom"  # 跨境电商
    LOGISTICS = "logistics"            # 物流运输
    OTHER = "other"                    # 其他


class DisputeMethod(str, enum.Enum):
    NEGOTIATION = "negotiation"  # 协商
    MEDIATION = "mediation"      # 调解
    ARBITRATION = "arbitration"  # 仲裁


class EvidenceType(str, enum.Enum):
    CONTRACT = "contract"        # 合同
    BILL_OF_LADING = "bill_of_lading"  # 提单
    CUSTOMS = "customs"          # 报关单
    INVOICE = "invoice"          # 发票
    CHAT_RECORD = "chat_record"  # 聊天记录
    OTHER = "other"              # 其他


class MessageType(str, enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    VOICE = "voice"
    SYSTEM = "system"


class NotificationType(str, enum.Enum):
    INTERNAL = "internal"  # 站内信
    EMAIL = "email"
    SMS = "sms"


class MediationStatus(str, enum.Enum):
    PENDING = "pending"       # 待分配
    ASSIGNED = "assigned"     # 已分配
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"   # 已完成
    FAILED = "failed"         # 失败


# ==================== 数据库模型 ====================

class Enterprise(Base):
    """企业信息表"""
    __tablename__ = "enterprises"

    id = Column(Integer, primary_key=True, index=True)
    credit_code = Column(String(18), unique=True, nullable=False, comment="统一社会信用代码")
    name = Column(String(200), nullable=False, comment="企业名称")
    legal_person = Column(String(50), nullable=False, comment="法人姓名")
    legal_id_card = Column(String(255), nullable=False, comment="法人身份证号(AES加密)")
    business_license = Column(String(100), nullable=False, comment="营业执照号")
    contact_phone = Column(String(255), nullable=False, comment="联系人手机号(AES加密)")
    contact_email = Column(String(200), nullable=False, comment="联系邮箱")
    audit_status = Column(SAEnum(AuditStatus), default=AuditStatus.PENDING, nullable=False)
    audit_note = Column(Text, comment="审核备注")
    country = Column(String(50), default="CN", comment="所属国家")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    users = relationship("User", back_populates="enterprise")
    cases = relationship("Case", back_populates="enterprise")


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    enterprise_id = Column(Integer, ForeignKey("enterprises.id"), nullable=True, comment="所属企业ID(调解员和平台管理员为null)")
    username = Column(String(50), unique=True, nullable=False)
    phone = Column(String(255), nullable=False, comment="手机号(AES加密)")
    email = Column(String(200), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), nullable=False)
    real_name = Column(String(50), nullable=False)
    id_card = Column(String(255), comment="身份证号(AES加密)")
    status = Column(SAEnum(UserStatus), default=UserStatus.PENDING)
    must_change_password = Column(Boolean, default=False, comment="是否强制修改密码")
    # 调解员专属字段
    mediator_domain = Column(String(200), comment="调解专业领域")
    mediator_intro = Column(Text, comment="调解员简介")
    mediator_success_rate = Column(Numeric(5, 2), default=0.0, comment="成功率(%)")
    mediator_rating = Column(Numeric(3, 2), default=5.0, comment="评分(0-5)")
    mediator_case_count = Column(Integer, default=0, comment="调解案件总数")
    # 通知偏好
    notify_email = Column(Boolean, default=True)
    notify_sms = Column(Boolean, default=False)
    # 多语言
    language = Column(String(10), default="zh-CN")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    enterprise = relationship("Enterprise", back_populates="users")
    sent_messages = relationship("NegotiationMessage", back_populates="sender")
    notifications = relationship("Notification", back_populates="user")
    logs = relationship("OperationLog", back_populates="user")

    __table_args__ = (
        Index("ix_users_email", "email"),
        Index("ix_users_role", "role"),
        Index("ix_users_enterprise_id", "enterprise_id"),
    )


class Case(Base):
    """案件表"""
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String(30), unique=True, nullable=False, comment="案件编号 CASE+年月日+4位随机数")
    enterprise_id = Column(Integer, ForeignKey("enterprises.id"), nullable=False)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    opponent_name = Column(String(200), nullable=False, comment="对方企业名称")
    opponent_country = Column(String(50), nullable=False, comment="对方国家")
    contract_type = Column(SAEnum(ContractType), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False, comment="争议标的额(USD)")
    dispute_desc = Column(Text, nullable=False, comment="争议事实描述")
    contract_date = Column(DateTime(timezone=True), nullable=False)
    incident_date = Column(DateTime(timezone=True), nullable=False)
    expected_method = Column(SAEnum(DisputeMethod), nullable=False)
    status = Column(SAEnum(CaseStatus), default=CaseStatus.NEGOTIATING)
    negotiation_started_at = Column(DateTime(timezone=True), comment="协商开始时间")
    closed_at = Column(DateTime(timezone=True), comment="结案时间")
    close_summary = Column(Text, comment="结案摘要")
    timeline = Column(JSON, default=list, comment="时间轴记录")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    enterprise = relationship("Enterprise", back_populates="cases")
    creator = relationship("User", foreign_keys=[created_by_user_id])
    evidences = relationship("Evidence", back_populates="case")
    messages = relationship("NegotiationMessage", back_populates="case")
    mediation_requests = relationship("MediationRequest", back_populates="case")
    agreements = relationship("MediationAgreement", back_populates="case")

    __table_args__ = (
        Index("ix_cases_enterprise_id", "enterprise_id"),
        Index("ix_cases_status", "status"),
        Index("ix_cases_case_number", "case_number"),
    )


class Evidence(Base):
    """证据文件表"""
    __tablename__ = "evidences"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    uploaded_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_url = Column(String(500), nullable=False)
    file_size = Column(Integer, comment="文件大小(字节)")
    file_mime = Column(String(100))
    file_hash = Column(String(64), nullable=False, comment="SHA-256哈希")
    evidence_type = Column(SAEnum(EvidenceType), nullable=False)
    timestamp_cert = Column(String(500), comment="时间戳证书")
    storage_voucher = Column(String(200), comment="存证编号")
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    case = relationship("Case", back_populates="evidences")
    uploader = relationship("User", foreign_keys=[uploaded_by_user_id])

    __table_args__ = (Index("ix_evidences_case_id", "case_id"),)


class NegotiationMessage(Base):
    """协商消息表"""
    __tablename__ = "negotiation_messages"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message_type = Column(SAEnum(MessageType), default=MessageType.TEXT)
    content = Column(Text, comment="消息内容(文字消息为文本, 图片/语音为URL)")
    voice_text = Column(Text, comment="语音转文字结果")
    is_system = Column(Boolean, default=False, comment="是否为系统消息")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    case = relationship("Case", back_populates="messages")
    sender = relationship("User", back_populates="sent_messages")

    __table_args__ = (Index("ix_messages_case_id", "case_id"),)


class NegotiationResult(Base):
    """协商结果记录"""
    __tablename__ = "negotiation_results"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), unique=True)
    summary = Column(Text, nullable=False, comment="协商结果摘要")
    memo_url = Column(String(500), comment="协商备忘录PDF URL")
    plaintiff_signed = Column(Boolean, default=False)
    plaintiff_signed_by = Column(String(50))
    plaintiff_signed_at = Column(DateTime(timezone=True))
    defendant_signed = Column(Boolean, default=False)
    defendant_signed_by = Column(String(50))
    defendant_signed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MediationRequest(Base):
    """调解申请表"""
    __tablename__ = "mediation_requests"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    applicant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    selected_mediator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    mediator_assigned_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    demand_text = Column(Text, nullable=False, comment="调解诉求")
    status = Column(SAEnum(MediationStatus), default=MediationStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    case = relationship("Case", back_populates="mediation_requests")
    applicant = relationship("User", foreign_keys=[applicant_id])
    selected_mediator = relationship("User", foreign_keys=[selected_mediator_id])
    assigned_mediator = relationship("User", foreign_keys=[mediator_assigned_id])
    meetings = relationship("MediationMeeting", back_populates="request")


class MediationMeeting(Base):
    """调解会议表"""
    __tablename__ = "mediation_meetings"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("mediation_requests.id"), nullable=False)
    meeting_link = Column(String(500), comment="会议链接")
    channel_name = Column(String(100), comment="Agora频道名")
    scheduled_time = Column(DateTime(timezone=True), nullable=False)
    actual_start_time = Column(DateTime(timezone=True))
    actual_end_time = Column(DateTime(timezone=True))
    recording_url = Column(String(500), comment="录制视频URL")
    transcript_text = Column(Text, comment="会议文字记录")
    mediator_opinion = Column(Text, comment="调解员意见")
    status = Column(String(20), default="scheduled", comment="scheduled/ongoing/ended")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    request = relationship("MediationRequest", back_populates="meetings")


class MediationAgreement(Base):
    """调解协议表"""
    __tablename__ = "mediation_agreements"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    agreement_content = Column(Text, comment="协议内容")
    agreement_pdf_url = Column(String(500), comment="协议PDF URL")
    signed_by_plaintiff = Column(Boolean, default=False)
    plaintiff_sign_time = Column(DateTime(timezone=True))
    plaintiff_signer_name = Column(String(50))
    signed_by_defendant = Column(Boolean, default=False)
    defendant_sign_time = Column(DateTime(timezone=True))
    defendant_signer_name = Column(String(50))
    signed_at = Column(DateTime(timezone=True), comment="完整签署时间")
    esign_cert_id = Column(String(200), comment="电子签章证书ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    case = relationship("Case", back_populates="agreements")


class Notification(Base):
    """通知消息表"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(SAEnum(NotificationType), default=NotificationType.INTERNAL)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    related_case_id = Column(Integer, ForeignKey("cases.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="notifications")

    __table_args__ = (
        Index("ix_notifications_user_id", "user_id"),
        Index("ix_notifications_is_read", "is_read"),
    )


class OperationLog(Base):
    """操作日志表"""
    __tablename__ = "operation_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False, comment="操作类型")
    resource_type = Column(String(50), comment="资源类型")
    resource_id = Column(Integer, comment="资源ID")
    detail = Column(JSON, comment="操作详情")
    ip = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="logs")

    __table_args__ = (Index("ix_logs_user_id", "user_id"),)


class VerificationCode(Base):
    """短信/邮件验证码"""
    __tablename__ = "verification_codes"

    id = Column(Integer, primary_key=True, index=True)
    target = Column(String(200), nullable=False, comment="手机号或邮箱")
    code = Column(String(10), nullable=False)
    purpose = Column(String(50), comment="sign_agreement/login/register")
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
