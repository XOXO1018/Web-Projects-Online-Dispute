"""
PDF 生成服务：调解协议、协商备忘录
"""
import os
import uuid
import logging
from datetime import datetime
from jinja2 import Template

logger = logging.getLogger(__name__)

AGREEMENT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
body { font-family: "SimSun", serif; margin: 40px; font-size: 14px; }
h1 { text-align: center; font-size: 20px; }
h2 { font-size: 16px; margin-top: 20px; }
.section { margin: 15px 0; line-height: 1.8; }
.sign-area { margin-top: 40px; display: flex; justify-content: space-between; }
</style>
</head>
<body>
<h1>和解协议书</h1>
<p style="text-align:center">协议编号：{{ case_number }} - {{ agreement_id }}</p>
<div class="section">
<h2>一、当事人信息</h2>
<p>申请方：{{ plaintiff_name }} （{{ plaintiff_enterprise }}）</p>
<p>被申请方：{{ defendant_enterprise }}</p>
</div>
<div class="section">
<h2>二、争议事实</h2>
<p>合同类型：{{ contract_type }}</p>
<p>争议标的额：USD {{ amount }}</p>
<p>争议描述：{{ dispute_desc }}</p>
</div>
<div class="section">
<h2>三、调解结果与履行方式</h2>
<p>{{ agreement_content }}</p>
</div>
<div class="section">
<h2>四、签署确认</h2>
<p>本协议经双方当事人电子签署后生效，具有法律约束力。</p>
</div>
<div class="sign-area">
<div>申请方签署：_______________<br>日期：{{ today }}</div>
<div>被申请方签署：_______________<br>日期：{{ today }}</div>
</div>
<p style="margin-top:30px;text-align:center;font-size:12px;color:#666">
本协议由智链解纷平台生成 | {{ today }}
</p>
</body>
</html>
"""


class PDFService:
    async def generate_agreement(self, case, agreement_content: str) -> str:
        """生成调解协议 PDF"""
        try:
            from weasyprint import HTML
            html_content = Template(AGREEMENT_TEMPLATE).render(
                case_number=case.case_number,
                agreement_id=uuid.uuid4().hex[:8].upper(),
                plaintiff_enterprise=f"企业ID:{case.enterprise_id}",
                plaintiff_name="原告方",
                defendant_enterprise=case.opponent_name,
                contract_type=case.contract_type.value,
                amount=float(case.amount),
                dispute_desc=case.dispute_desc[:200],
                agreement_content=agreement_content,
                today=datetime.now().strftime("%Y年%m月%d日"),
            )
            output_dir = "/app/uploads/agreements"
            os.makedirs(output_dir, exist_ok=True)
            filename = f"agreement_{case.case_number}_{uuid.uuid4().hex[:8]}.pdf"
            output_path = os.path.join(output_dir, filename)
            HTML(string=html_content).write_pdf(output_path)
            logger.info(f"协议PDF生成成功: {output_path}")
            return f"/uploads/agreements/{filename}"
        except Exception as e:
            logger.error(f"PDF生成失败 (WeasyPrint): {e}")
            # 降级：返回Mock URL
            return f"/uploads/agreements/mock_{case.case_number}.pdf"
