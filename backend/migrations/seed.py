"""
数据库初始化脚本：创建管理员账号和预置调解员
运行方式：python seed.py
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
from app.core.config import settings
from app.core.security import hash_password, encrypt_field
from app.models.models import User, UserRole, UserStatus, Enterprise, AuditStatus


async def seed():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    # 导入所有模型以触发表创建
    from app.core.database import Base
    import app.models.models  # noqa

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ 数据库表创建完成")

    async with AsyncSessionLocal() as db:
        # ---- 创建平台管理员 ----
        existing = await db.execute(
            select(User).where(User.email == settings.ADMIN_EMAIL)
        )
        if not existing.scalar_one_or_none():
            admin = User(
                username=settings.ADMIN_USERNAME,
                phone=encrypt_field("13800000000"),
                email=settings.ADMIN_EMAIL,
                password_hash=hash_password(settings.ADMIN_PASSWORD),
                role=UserRole.PLATFORM_ADMIN,
                real_name="平台管理员",
                status=UserStatus.ACTIVE,
                must_change_password=True,
            )
            db.add(admin)
            print(f"✅ 管理员账号已创建: {settings.ADMIN_EMAIL} / {settings.ADMIN_PASSWORD}")
        else:
            print("ℹ️  管理员账号已存在，跳过")

        # ---- 预置调解员 ----
        mediators_data = [
            {
                "real_name": "李建国",
                "email": "mediator_li@zjfl.com",
                "phone": "13900000001",
                "domain": "货物买卖、跨境电商",
                "intro": "具有15年跨境贸易纠纷调解经验，擅长中越、中泰贸易纠纷调解，成功率达92%。",
                "success_rate": 92.0,
                "rating": 4.9,
            },
            {
                "real_name": "陈秀华",
                "email": "mediator_chen@zjfl.com",
                "phone": "13900000002",
                "domain": "物流运输、货物损毁",
                "intro": "前国际贸易法律顾问，精通CISG及东盟各国贸易法律，专注物流纠纷调解。",
                "success_rate": 88.5,
                "rating": 4.8,
            },
            {
                "real_name": "Nguyen Van An",
                "email": "mediator_nguyen@zjfl.com",
                "phone": "13900000003",
                "domain": "中越贸易纠纷",
                "intro": "越南籍双语调解员，熟悉越南法律和贸易实践，专注处理中越跨境贸易纠纷。",
                "success_rate": 85.0,
                "rating": 4.7,
            },
            {
                "real_name": "王德明",
                "email": "mediator_wang@zjfl.com",
                "phone": "13900000004",
                "domain": "合同纠纷、应收账款",
                "intro": "国际商事调解委员会认证调解员，处理跨境合同纠纷案件300+。",
                "success_rate": 90.0,
                "rating": 4.85,
            },
            {
                "real_name": "Somchai Thanakit",
                "email": "mediator_somchai@zjfl.com",
                "phone": "13900000005",
                "domain": "中泰贸易纠纷、知识产权",
                "intro": "泰国籍调解员，具备中泰双语能力，专注泰国-东盟贸易纠纷及知识产权争议解决。",
                "success_rate": 82.0,
                "rating": 4.6,
            },
        ]

        for m_data in mediators_data:
            existing_m = await db.execute(
                select(User).where(User.email == m_data["email"])
            )
            if not existing_m.scalar_one_or_none():
                mediator = User(
                    username=f"mediator_{m_data['email'].split('@')[0]}",
                    phone=encrypt_field(m_data["phone"]),
                    email=m_data["email"],
                    password_hash=hash_password("Mediator@123"),
                    role=UserRole.MEDIATOR,
                    real_name=m_data["real_name"],
                    status=UserStatus.ACTIVE,
                    mediator_domain=m_data["domain"],
                    mediator_intro=m_data["intro"],
                    mediator_success_rate=m_data["success_rate"],
                    mediator_rating=m_data["rating"],
                )
                db.add(mediator)
                print(f"✅ 调解员已创建: {m_data['real_name']} ({m_data['email']})")
            else:
                print(f"ℹ️  调解员已存在，跳过: {m_data['email']}")

        # ---- 演示企业 ----
        if settings.DEMO_MODE:
            demo_ent_result = await db.execute(
                select(Enterprise).where(Enterprise.credit_code == "91110000000000000X")
            )
            if not demo_ent_result.scalar_one_or_none():
                demo_ent = Enterprise(
                    credit_code="91110000000000000X",
                    name="演示贸易有限公司",
                    legal_person="张三",
                    legal_id_card=encrypt_field("110101199001011234"),
                    business_license="91110000000000000X",
                    contact_phone=encrypt_field("13800138000"),
                    contact_email="demo@zjfl.com",
                    audit_status=AuditStatus.APPROVED,
                )
                db.add(demo_ent)
                await db.flush()

                demo_user = User(
                    enterprise_id=demo_ent.id,
                    username="demo_admin",
                    phone=encrypt_field("13800138000"),
                    email="demo@zjfl.com",
                    password_hash=hash_password("Demo@12345"),
                    role=UserRole.ENTERPRISE_ADMIN,
                    real_name="张三",
                    status=UserStatus.ACTIVE,
                )
                db.add(demo_user)
                print("✅ 演示企业账号已创建: demo@zjfl.com / Demo@12345")

        await db.commit()
    print("\n🎉 数据库初始化完成！")
    print(f"   管理员：{settings.ADMIN_EMAIL} / {settings.ADMIN_PASSWORD}")
    print("   调解员：mediator_li@zjfl.com 等5位 / Mediator@123")
    if settings.DEMO_MODE:
        print("   演示企业：demo@zjfl.com / Demo@12345")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
