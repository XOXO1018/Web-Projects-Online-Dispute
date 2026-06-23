"""
图形验证码接口
"""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import random
import string
import uuid
import io
from PIL import Image, ImageDraw, ImageFont
import base64

from app.core.redis_client import redis_client
from app.core.response import success

router = APIRouter()


def generate_captcha_image(text: str) -> bytes:
    """生成图形验证码图片"""
    width, height = 120, 40
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # 随机背景噪点
    for _ in range(50):
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.point([x, y], fill=(random.randint(150, 200),) * 3)

    # 干扰线
    for _ in range(3):
        x1 = random.randint(0, width // 2)
        y1 = random.randint(0, height)
        x2 = random.randint(width // 2, width)
        y2 = random.randint(0, height)
        draw.line([(x1, y1), (x2, y2)], fill=(random.randint(100, 180),) * 3, width=1)

    # 绘制文字
    font_size = 24
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    for i, char in enumerate(text):
        x = 10 + i * 25 + random.randint(-3, 3)
        y = random.randint(5, 12)
        color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
        draw.text((x, y), char, fill=color, font=font)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@router.get("/image")
async def get_captcha():
    """获取图形验证码"""
    code = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    token = str(uuid.uuid4())

    # 存储验证码, 5分钟有效
    await redis_client.set(f"captcha:{token}", code.lower(), expire=300)

    img_bytes = generate_captcha_image(code)
    img_b64 = base64.b64encode(img_bytes).decode()

    return success({
        "token": token,
        "image": f"data:image/png;base64,{img_b64}",
    })
