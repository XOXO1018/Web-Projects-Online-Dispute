const pptxgen = require("pptxgenjs");
const path = require("path");
const fs = require("fs");

// ============================================================
// vivo AIGC 赛事 PPT - 工友通
// ============================================================

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "工友通团队";
pres.title = "工友通 - 智能日程管理助手";
pres.subject = "2026年中国高校计算机大赛-AIGC创新赛";

// ============================================================
// 配色方案（参考vivo品牌）
// ============================================================
const VIVO_PURPLE = "6B3FA0";   // vivo紫色
const VIVO_BLUE   = "1E88E5";   // vivo蓝
const VIVO_DARK   = "1A1A2E";   // 深色背景
const VIVO_LIGHT  = "F5F0FF";   // 淡紫色背景
const VIVO_ACCENT = "9B59B6";   // 强调色
const WHITE       = "FFFFFF";
const DARK_TEXT   = "1A1A2E";
const GRAY_TEXT   = "666666";
const LIGHT_GRAY  = "E8E8E8";

// 辅助函数：创建阴影配置（每次调用返回新对象，避免对象复用问题）
const makeShadow = () => ({
  type: "outer", color: "000000", blur: 8, offset: 3, angle: 135, opacity: 0.12
});

// ============================================================
// Slide 1: 封面
// ============================================================
{
  let slide = pres.addSlide();
  slide.background = { color: VIVO_DARK };

  // 顶部紫色装饰条
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.15,
    fill: { color: VIVO_PURPLE }, line: { color: VIVO_PURPLE }
  });

  // 左侧装饰块
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 1.5, w: 0.3, h: 2.5,
    fill: { color: VIVO_PURPLE }, line: { color: VIVO_PURPLE }
  });

  // 主标题
  slide.addText([
    { text: "2026", options: { fontSize: 54, bold: true, color: VIVO_PURPLE, fontFace: "Microsoft YaHei" } },
    { text: "年中国高校计算机大赛", options: { fontSize: 54, bold: true, color: WHITE, fontFace: "Microsoft YaHei" } }
  ], { x: 0.6, y: 1.4, w: 9, h: 0.9 });

  slide.addText([
    { text: "-AIGC", options: { fontSize: 54, bold: true, color: VIVO_PURPLE, fontFace: "Arial" } },
    { text: "创新赛", options: { fontSize: 54, bold: true, color: WHITE, fontFace: "Microsoft YaHei" } }
  ], { x: 0.6, y: 2.2, w: 9, h: 0.9 });

  // 分隔线
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: 3.15, w: 4, h: 0.04,
    fill: { color: VIVO_PURPLE }, line: { color: VIVO_PURPLE }
  });

  // 作品名称
  slide.addText([
    { text: "作品名称：", options: { fontSize: 22, bold: true, color: VIVO_PURPLE, fontFace: "Microsoft YaHei" } },
    { text: "《工友通》", options: { fontSize: 22, bold: true, color: WHITE, fontFace: "Microsoft YaHei" } }
  ], { x: 0.6, y: 3.4, w: 9, h: 0.5 });

  // 团队名称
  slide.addText([
    { text: "团队名称：", options: { fontSize: 22, bold: true, color: VIVO_PURPLE, fontFace: "Microsoft YaHei" } },
    { text: "XXXXX（待填写）", options: { fontSize: 22, bold: true, color: WHITE, fontFace: "Microsoft YaHei" } }
  ], { x: 0.6, y: 3.9, w: 9, h: 0.5 });

  // 右下角装饰
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 8.5, y: 5.0, w: 1.5, h: 0.625,
    fill: { color: VIVO_PURPLE, transparency: 30 }, line: { color: VIVO_PURPLE, transparency: 30 }
  });
  slide.addText("应用赛道", { x: 8.5, y: 5.0, w: 1.5, h: 0.625, fontSize: 14, bold: true, color: WHITE, align: "center", valign: "middle", fontFace: "Microsoft YaHei" });
}

// ============================================================
// Slide 2: 目录页
// ============================================================
{
  let slide = pres.addSlide();
  slide.background = { color: WHITE };

  // 左侧色块
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 3.5, h: 5.625,
    fill: { color: VIVO_PURPLE }, line: { color: VIVO_PURPLE }
  });

  // 目录文字
  slide.addText("目录", { x: 0.4, y: 1.8, w: 2.5, h: 0.9, fontSize: 48, bold: true, color: WHITE, fontFace: "Microsoft YaHei" });
  slide.addText("CONTENTS", { x: 0.4, y: 2.6, w: 2.5, h: 0.5, fontSize: 16, color: WHITE, fontFace: "Arial", charSpacing: 3 });

  // 分隔线
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.4, y: 3.1, w: 1.5, h: 0.04,
    fill: { color: WHITE }, line: { color: WHITE }
  });

  // 目录项
  const tocItems = [
    { num: "01", text: "团队介绍" },
    { num: "02", text: "产品介绍" },
    { num: "03", text: "产品功能演示" }
  ];
  tocItems.forEach((item, i) => {
    const y = 1.5 + i * 1.3;
    slide.addText(item.num, { x: 4.0, y, w: 1.0, h: 0.8, fontSize: 40, bold: true, color: VIVO_PURPLE, fontFace: "Arial" });
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 5.1, y: y + 0.35, w: 0.5, h: 0.04,
      fill: { color: VIVO_PURPLE }, line: { color: VIVO_PURPLE }
    });
    slide.addText(item.text, { x: 5.7, y, w: 4, h: 0.8, fontSize: 24, bold: true, color: DARK_TEXT, fontFace: "Microsoft YaHei" });
  });
}

// ============================================================
// Slide 3: 团队介绍
// ============================================================
{
  let slide = pres.addSlide();
  slide.background = { color: VIVO_LIGHT };

  // 顶部色条
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.8,
    fill: { color: VIVO_PURPLE }, line: { color: VIVO_PURPLE }
  });
  slide.addText("01  团队介绍", { x: 0.4, y: 0.15, w: 9, h: 0.5, fontSize: 22, bold: true, color: WHITE, fontFace: "Microsoft YaHei" });

  // 标题
  slide.addText("团队介绍", { x: 0.5, y: 1.1, w: 9, h: 0.6, fontSize: 28, bold: true, color: VIVO_PURPLE, fontFace: "Microsoft YaHei" });

  // 团队信息卡片
  const infoItems = [
    { label: "团队名称", value: "XXXXX（待填写）" },
    { label: "团队成员", value: "成员1 - XXX大学  |  成员2 - XXX大学  |  成员3 - XXX大学  |  成员4 - XXX大学  |  成员5 - XXX大学" },
    { label: "指导教师", value: "XXX（待填写）" }
  ];
  infoItems.forEach((item, i) => {
    const y = 1.8 + i * 0.7;
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.5, y, w: 9, h: 0.6,
      fill: { color: WHITE }, line: { color: LIGHT_GRAY }, shadow: makeShadow()
    });
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.5, y, w: 0.08, h: 0.6,
      fill: { color: VIVO_PURPLE }, line: { color: VIVO_PURPLE }
    });
    slide.addText([
      { text: item.label + "：", options: { bold: true, color: VIVO_PURPLE, fontFace: "Microsoft YaHei", fontSize: 14 } },
      { text: item.value, options: { color: DARK_TEXT, fontFace: "Microsoft YaHei", fontSize: 14 } }
    ], { x: 0.7, y, w: 8.6, h: 0.6, valign: "middle" });
  });

  // 注：分工说明
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 4.0, w: 9, h: 1.4,
    fill: { color: WHITE }, line: { color: LIGHT_GRAY }, shadow: makeShadow()
  });
  slide.addText("注：团队成员须为报名参赛学生，同一学生禁止在不同团队重复报名。", { x: 0.7, y: 4.1, w: 8.6, h: 0.35, fontSize: 12, color: GRAY_TEXT, fontFace: "Microsoft YaHei" });
  slide.addText([
    { text: "1.  产品开发：1人", options: { breakLine: true } },
    { text: "2.  UI与交互设计：1人", options: { breakLine: true } },
    { text: "3.  前端开发：1人", options: { breakLine: true } },
    { text: "4.  后端开发：1~2人", options: {} }
  ], {
    x: 0.7, y: 4.45, w: 8.6, h: 0.9, fontSize: 12, color: DARK_TEXT, fontFace: "Microsoft YaHei",
    lineSpaceMult: 1.2
  });
}

// ============================================================
// Slide 4: 目录页（重复结构，作为章节页）
// ============================================================
{
  let slide = pres.addSlide();
  slide.background = { color: WHITE };
  slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 3.5, h: 5.625, fill: { color: VIVO_BLUE }, line: { color: VIVO_BLUE } });
  slide.addText("02", { x: 0.4, y: 1.8, w: 2.5, h: 0.9, fontSize: 48, bold: true, color: WHITE, fontFace: "Arial" });
  slide.addText("产品介绍", { x: 0.4, y: 2.7, w: 2.5, h: 0.6, fontSize: 28, bold: true, color: WHITE, fontFace: "Microsoft YaHei" });
  slide.addText("PRODUCT INTRO", { x: 0.4, y: 3.25, w: 2.5, h: 0.4, fontSize: 14, color: WHITE, fontFace: "Arial", charSpacing: 2 });
  slide.addShape(pres.shapes.RECTANGLE, { x: 0.4, y: 3.65, w: 1.5, h: 0.04, fill: { color: WHITE }, line: { color: WHITE } });
  slide.addText("02  产品介绍", { x: 4.0, y: 2.3, w: 5.5, h: 0.7, fontSize: 36, bold: true, color: VIVO_BLUE, fontFace: "Microsoft YaHei" });
  slide.addShape(pres.shapes.RECTANGLE, { x: 4.0, y: 3.0, w: 3, h: 0.04, fill: { color: VIVO_BLUE }, line: { color: VIVO_BLUE } });
  slide.addText("智能日程管理 · AI 赋能工友服务", { x: 4.0, y: 3.2, w: 5.5, h: 0.5, fontSize: 16, color: GRAY_TEXT, fontFace: "Microsoft YaHei" });
}

// ============================================================
// Slide 5: 产品介绍 - 总览
// ============================================================
{
  let slide = pres.addSlide();
  slide.background = { color: WHITE };

  slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.8, fill: { color: VIVO_BLUE }, line: { color: VIVO_BLUE } });
  slide.addText("02  产品介绍", { x: 0.4, y: 0.15, w: 9, h: 0.5, fontSize: 22, bold: true, color: WHITE, fontFace: "Microsoft YaHei" });

  slide.addText("产品介绍", { x: 0.5, y: 1.1, w: 9, h: 0.5, fontSize: 28, bold: true, color: VIVO_BLUE, fontFace: "Microsoft YaHei" });

  // 产品定位卡片
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.75, w: 9, h: 1.1,
    fill: { color: VIVO_LIGHT }, line: { color: VIVO_BLUE, pt: 1 }, shadow: makeShadow()
  });
  slide.addText([
    { text: "产品定位：", options: { bold: true, color: VIVO_BLUE, fontSize: 16, fontFace: "Microsoft YaHei" } },
    { text: "一款面向蓝领工人（安装、维修、疏通、清洗、检修等）的智能日程管理 App，融合", options: { color: DARK_TEXT, fontSize: 16, fontFace: "Microsoft YaHei" } },
    { text: " vivo 蓝心大模型", options: { bold: true, color: VIVO_BLUE, fontSize: 16, fontFace: "Microsoft YaHei" } },
    { text: "与", options: { color: DARK_TEXT, fontSize: 16, fontFace: "Microsoft YaHei" } },
    { text: " Ollama 本地 AI", options: { bold: true, color: VIVO_BLUE, fontSize: 16, fontFace: "Microsoft YaHei" } },
    { text: "，实现自然语言日程创建、个性化提醒与智能导航。", options: { color: DARK_TEXT, fontSize: 16, fontFace: "Microsoft YaHei" } }
  ], { x: 0.7, y: 1.85, w: 8.6, h: 0.9, valign: "middle" });

  // 目标用户
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 3.0, w: 9, h: 0.85,
    fill: { color: WHITE }, line: { color: LIGHT_GRAY }, shadow: makeShadow()
  });
  slide.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 3.0, w: 0.08, h: 0.85, fill: { color: VIVO_BLUE }, line: { color: VIVO_BLUE } });
  slide.addText([
    { text: "目标用户：", options: { bold: true, color: VIVO_BLUE, fontSize: 15, fontFace: "Microsoft YaHei" } },
    { text: "蓝领工人（安装工、维修工、疏通工、清洗工等），主要特征：操作手机时间碎片化、任务安排依赖口头记忆、文化程度参差不齐。", options: { color: DARK_TEXT, fontSize: 15, fontFace: "Microsoft YaHei" } }
  ], { x: 0.7, y: 3.05, w: 8.6, h: 0.75, valign: "middle" });

  // 核心场景
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 4.0, w: 9, h: 0.85,
    fill: { color: WHITE }, line: { color: LIGHT_GRAY }, shadow: makeShadow()
  });
  slide.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 4.0, w: 0.08, h: 0.85, fill: { color: VIVO_BLUE }, line: { color: VIVO_BLUE } });
  slide.addText([
    { text: "核心场景：", options: { bold: true, color: VIVO_BLUE, fontSize: 15, fontFace: "Microsoft YaHei" } },
    { text: "工人接单后，通过自然语言（如\"明天下午3点去XX小区安装热水器\"）快速创建日程，系统自动解析时间、地点、工作类型，生成个性化出发前准备清单，并提供一键导航。", options: { color: DARK_TEXT, fontSize: 15, fontFace: "Microsoft YaHei" } }
  ], { x: 0.7, y: 4.05, w: 8.6, h: 0.75, valign: "middle" });

  // 技术标签
  const tags = ["Android", "Ollama", "vivo蓝心大模型", "OkHttp3", "Baidu Maps", "Material Design"];
  tags.forEach((tag, i) => {
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.5 + i * 1.55, y: 5.05, w: 1.45, h: 0.4,
      fill: { color: VIVO_BLUE, transparency: 15 }, line: { color: VIVO_BLUE, pt: 0.5 }
    });
    slide.addText(tag, { x: 0.5 + i * 1.55, y: 5.05, w: 1.45, h: 0.4, fontSize: 10, color: VIVO_BLUE, align: "center", valign: "middle", fontFace: "Microsoft YaHei" });
  });
}

// ============================================================
// Slide 6: 章节页 - 产品功能演示
// ============================================================
{
  let slide = pres.addSlide();
  slide.background = { color: VIVO_ACCENT };
  slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 3.5, h: 5.625, fill: { color: "8E44AD" }, line: { color: "8E44AD" } });
  slide.addText("03", { x: 0.4, y: 1.8, w: 2.5, h: 0.9, fontSize: 48, bold: true, color: WHITE, fontFace: "Arial" });
  slide.addText("产品功能演示", { x: 0.4, y: 2.7, w: 2.8, h: 0.6, fontSize: 24, bold: true, color: WHITE, fontFace: "Microsoft YaHei" });
  slide.addText("DEMO", { x: 0.4, y: 3.25, w: 2.5, h: 0.4, fontSize: 14, color: WHITE, fontFace: "Arial", charSpacing: 3 });
  slide.addShape(pres.shapes.RECTANGLE, { x: 0.4, y: 3.65, w: 1.5, h: 0.04, fill: { color: WHITE }, line: { color: WHITE } });
  slide.addText("03  产品功能演示", { x: 4.0, y: 2.3, w: 5.5, h: 0.7, fontSize: 36, bold: true, color: WHITE, fontFace: "Microsoft YaHei" });
  slide.addShape(pres.shapes.RECTANGLE, { x: 4.0, y: 3.0, w: 3, h: 0.04, fill: { color: WHITE }, line: { color: WHITE } });
  slide.addText("AI 赋能 · 智能日程 · 个性化提醒", { x: 4.0, y: 3.2, w: 5.5, h: 0.5, fontSize: 16, color: "E8D5FF", fontFace: "Microsoft YaHei" });
}

// ============================================================
// Slide 7: 产品原创性
// ============================================================
{
  let slide = pres.addSlide();
  slide.background = { color: WHITE };

  slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.8, fill: { color: VIVO_ACCENT }, line: { color: VIVO_ACCENT } });
  slide.addText("03  产品功能演示", { x: 0.4, y: 0.15, w: 9, h: 0.5, fontSize: 22, bold: true, color: WHITE, fontFace: "Microsoft YaHei" });

  slide.addText("产品原创性说明", { x: 0.5, y: 1.05, w: 9, h: 0.5, fontSize: 26, bold: true, color: VIVO_ACCENT, fontFace: "Microsoft YaHei" });

  const sections = [
    {
      title: "产品解决的问题",
      points: [
        "蓝领工人日程管理混乱，依赖口头记忆和纸质记录，容易遗漏或冲突；",
        "工作内容多样（安装、维修、疏通、清洗等），出发前准备全凭经验，容易忘带工具配件；",
        "服务地点分散，导航操作繁琐，需频繁切换 App，体验割裂。"
      ]
    },
    {
      title: "创新点说明",
      points: [
        "一句话创建日程：自然语言输入，自动解析时间、地点、工作类型，无需手动填写表单；",
        "AI 个性化提醒：根据工作类型（安装/维修/清洗/疏通等）生成专属出发前准备清单，工具配件一目了然；",
        "双模型支持：支持 vivo 蓝心大模型（云端）与 Ollama 本地模型（离线），适配不同网络环境。"
      ]
    },
    {
      title: "差异化竞争优势",
      points: [
        "垂直场景深耕：专为蓝领工人设计，理解其工作语言和场景，而非通用日程管理；",
        "AI 驱动体验：AI 不是噱头，而是真正嵌入日程解析→提醒生成→出发准备全流程；",
        "本地优先：支持 Ollama 本地推理，保护工人隐私数据，适合无网/弱网环境。"
      ]
    }
  ];

  let y = 1.65;
  sections.forEach((sec, si) => {
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.5, y, w: 9, h: 0.4,
      fill: { color: VIVO_ACCENT, transparency: 10 }, line: { color: VIVO_ACCENT }
    });
    slide.addText((si + 1) + ". " + sec.title, { x: 0.7, y, w: 8.6, h: 0.4, fontSize: 14, bold: true, color: VIVO_ACCENT, fontFace: "Microsoft YaHei", valign: "middle" });
    y += 0.4;

    const lineHeight = 0.42;
    sec.points.forEach((pt) => {
      slide.addShape(pres.shapes.RECTANGLE, {
        x: 0.5, y, w: 9, h: lineHeight,
        fill: { color: WHITE }, line: { color: LIGHT_GRAY }
      });
      slide.addText(pt, { x: 0.7, y: y + 0.04, w: 8.6, h: lineHeight - 0.04, fontSize: 12, color: DARK_TEXT, fontFace: "Microsoft YaHei", valign: "middle" });
      y += lineHeight;
    });
    y += 0.1;
  });
}

// ============================================================
// Slide 8: 核心功能详解
// ============================================================
{
  let slide = pres.addSlide();
  slide.background = { color: WHITE };

  slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.8, fill: { color: VIVO_ACCENT }, line: { color: VIVO_ACCENT } });
  slide.addText("03  产品功能演示", { x: 0.4, y: 0.15, w: 9, h: 0.5, fontSize: 22, bold: true, color: WHITE, fontFace: "Microsoft YaHei" });

  slide.addText("核心功能详解", { x: 0.5, y: 1.05, w: 9, h: 0.5, fontSize: 26, bold: true, color: VIVO_ACCENT, fontFace: "Microsoft YaHei" });

  const features = [
    {
      title: "AI 日程解析",
      desc: "支持自然语言输入，自动提取时间、地点、工作类型。无论用户说\"明天下午三点去XX小区装热水器\"还是\"后天上午十点维修空调\"，系统均可精准解析。"
    },
    {
      title: "个性化提醒生成",
      desc: "根据工作类型生成专属准备清单：安装类→工具+配件清单；维修类→断电操作+备件；清洗类→防护措施+清洁剂；疏通类→管道工具+通风准备。"
    },
    {
      title: "一键导航",
      desc: "系统自动解析地址并调用百度地图规划路线，支持一键导航。到达后自动标记状态，提醒工人开始服务。"
    },
    {
      title: "双模型架构",
      desc: "默认使用 Ollama 本地模型（deepseek-r1:8b），保护隐私；支持切换至 vivo 蓝心大模型（云端），提供更强推理能力。"
    }
  ];

  const cardW = 4.3;
  features.forEach((f, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = 0.5 + col * (cardW + 0.4);
    const y = 1.65 + row * 1.9;

    slide.addShape(pres.shapes.RECTANGLE, {
      x, y, w: cardW, h: 1.75,
      fill: { color: VIVO_LIGHT }, line: { color: VIVO_ACCENT, pt: 0.5 }, shadow: makeShadow()
    });
    slide.addShape(pres.shapes.RECTANGLE, {
      x, y, w: cardW, h: 0.08,
      fill: { color: VIVO_ACCENT }, line: { color: VIVO_ACCENT }
    });
    slide.addText((i + 1) + ". " + f.title, { x: x + 0.2, y: y + 0.15, w: cardW - 0.4, h: 0.4, fontSize: 15, bold: true, color: VIVO_ACCENT, fontFace: "Microsoft YaHei" });
    slide.addText(f.desc, { x: x + 0.2, y: y + 0.55, w: cardW - 0.4, h: 1.1, fontSize: 11, color: DARK_TEXT, fontFace: "Microsoft YaHei", valign: "top" });
  });
}

// ============================================================
// Slide 9: 创新点详解
// ============================================================
{
  let slide = pres.addSlide();
  slide.background = { color: VIVO_LIGHT };

  slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.8, fill: { color: VIVO_ACCENT }, line: { color: VIVO_ACCENT } });
  slide.addText("03  产品功能演示", { x: 0.4, y: 0.15, w: 9, h: 0.5, fontSize: 22, bold: true, color: WHITE, fontFace: "Microsoft YaHei" });

  slide.addText("创新点详解", { x: 0.5, y: 1.05, w: 9, h: 0.5, fontSize: 26, bold: true, color: VIVO_ACCENT, fontFace: "Microsoft YaHei" });
  slide.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.55, w: 2, h: 0.04, fill: { color: VIVO_ACCENT }, line: { color: VIVO_ACCENT } });

  // 创新点列表
  const innovations = [
    {
      title: "自然语言 → 结构化日程",
      desc: "一句话创建日程，无需手动填写时间、地点、类型。传统 App 需要用户主动填表，工友通让 AI 替用户完成结构化过程。"
    },
    {
      title: "AI 驱动个性化准备清单",
      desc: "不只是提醒\"几点出发\"，而是根据工作类型提供具体准备建议（工具清单、配件清单、安全注意事项），降低因忘带工具导致的返工。"
    },
    {
      title: "本地优先，保护隐私",
      desc: "支持 Ollama 本地推理，工人的客户地址、工作记录全部保留在本地设备，不上传云端，解决蓝领工人对隐私泄露的顾虑。"
    }
  ];

  innovations.forEach((inn, i) => {
    const y = 1.8 + i * 1.2;
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.5, y, w: 9, h: 1.05,
      fill: { color: WHITE }, line: { color: LIGHT_GRAY }, shadow: makeShadow()
    });
    slide.addShape(pres.shapes.OVAL, {
      x: 0.7, y: y + 0.3, w: 0.45, h: 0.45,
      fill: { color: VIVO_ACCENT }, line: { color: VIVO_ACCENT }
    });
    slide.addText(String(i + 1), { x: 0.7, y: y + 0.3, w: 0.45, h: 0.45, fontSize: 16, bold: true, color: WHITE, align: "center", valign: "middle" });
    slide.addText(inn.title, { x: 1.35, y: y + 0.1, w: 8, h: 0.4, fontSize: 15, bold: true, color: VIVO_ACCENT, fontFace: "Microsoft YaHei" });
    slide.addText(inn.desc, { x: 1.35, y: y + 0.5, w: 8, h: 0.5, fontSize: 12, color: DARK_TEXT, fontFace: "Microsoft YaHei" });
  });
}

// ============================================================
// Slide 10: 目标用户分析
// ============================================================
{
  let slide = pres.addSlide();
  slide.background = { color: WHITE };

  slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.8, fill: { color: VIVO_ACCENT }, line: { color: VIVO_ACCENT } });
  slide.addText("03  产品功能演示", { x: 0.4, y: 0.15, w: 9, h: 0.5, fontSize: 22, bold: true, color: WHITE, fontFace: "Microsoft YaHei" });

  slide.addText("目标用户分析", { x: 0.5, y: 1.05, w: 9, h: 0.5, fontSize: 26, bold: true, color: VIVO_ACCENT, fontFace: "Microsoft YaHei" });
  slide.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.55, w: 2, h: 0.04, fill: { color: VIVO_ACCENT }, line: { color: VIVO_ACCENT } });

  const analyses = [
    {
      title: "核心目标用户",
      points: [
        "蓝领工人：安装工、维修工、疏通工、清洗工、检修工等；",
        "年龄跨度大（18~55岁），智能手机使用能力参差不齐；",
        "工作节奏快、任务密集，对\"快速记录\"需求强烈。"
      ]
    },
    {
      title: "中间使用环节",
      points: [
        "接单后立即记录：\"去哪里？干什么？几点？\"需快速转化为可执行日程；",
        "出发前准备：出发前需确认工具、配件、安全措施是否到位；",
        "到达后操作：标记到达、开始工作、完成任务，状态需实时同步。"
      ]
    },
    {
      title: "应用场景",
      points: [
        "场景1：工人早上收到派单，口头记住\"10点XX小区装热水器\"，打开 App 输入一句话即可创建日程；",
        "场景2：出发前，App 推送\"安装热水器：冲击钻、扳手、密封胶已备齐？\"准备清单提醒；",
        "场景3：到达后一键导航，App 提示\"已到达，开始服务\"，完成后标记完成。"
      ]
    },
    {
      title: "市场欢迎程度",
      points: [
        "目标用户规模庞大：中国蓝领工人群体超过3亿；",
        "传统工具功能单一，缺乏 AI 赋能，市场存在明显需求缺口；",
        "蓝领服务行业信息化程度低，潜在商业价值显著。"
      ]
    }
  ];

  const colW = 4.35;
  analyses.forEach((a, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = 0.5 + col * (colW + 0.3);
    const y = 1.75 + row * 1.85;

    slide.addShape(pres.shapes.RECTANGLE, {
      x, y, w: colW, h: 1.7,
      fill: { color: WHITE }, line: { color: LIGHT_GRAY }, shadow: makeShadow()
    });
    slide.addShape(pres.shapes.RECTANGLE, { x, y, w: 0.08, h: 1.7, fill: { color: VIVO_ACCENT }, line: { color: VIVO_ACCENT } });
    slide.addText(a.title, { x: x + 0.2, y: y + 0.1, w: colW - 0.4, h: 0.4, fontSize: 13, bold: true, color: VIVO_ACCENT, fontFace: "Microsoft YaHei" });
    const textContent = a.points.map((p, pi) => ({
      text: p,
      options: { bullet: true, breakLine: pi < a.points.length - 1, fontSize: 10, color: DARK_TEXT, fontFace: "Microsoft YaHei" }
    }));
    slide.addText(textContent, { x: x + 0.2, y: y + 0.5, w: colW - 0.4, h: 1.1, paraSpaceAfter: 4 });
  });
}

// ============================================================
// Slide 11: 产品提交说明
// ============================================================
{
  let slide = pres.addSlide();
  slide.background = { color: WHITE };

  slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.8, fill: { color: VIVO_ACCENT }, line: { color: VIVO_ACCENT } });
  slide.addText("03  产品功能演示", { x: 0.4, y: 0.15, w: 9, h: 0.5, fontSize: 22, bold: true, color: WHITE, fontFace: "Microsoft YaHei" });

  slide.addText("产品提交说明", { x: 0.5, y: 1.05, w: 9, h: 0.5, fontSize: 26, bold: true, color: VIVO_ACCENT, fontFace: "Microsoft YaHei" });
  slide.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.55, w: 2, h: 0.04, fill: { color: VIVO_ACCENT }, line: { color: VIVO_ACCENT } });

  // 提交说明
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.75, w: 9, h: 2.2,
    fill: { color: VIVO_LIGHT }, line: { color: VIVO_ACCENT, pt: 0.5 }
  });

  const submitNotes = [
    "1. 本次提交仅需展示团队的作品名称、核心功能及亮点即可，完整功能将于复赛阶段提交；",
    "2. 如团队计划迭代到更有潜力的大模型，请在提交时明确说明，并确保拥有该大模型的调用权限（API 密钥或调用许可）；",
    "3. 提交后，作品一切版权及权益归团队所有，vivo 大赛组委会承诺维护参赛者合法权益，详见官方协议。"
  ];

  submitNotes.forEach((note, i) => {
    slide.addText(note, {
      x: 0.7, y: 1.9 + i * 0.65, w: 8.6, h: 0.6,
      fontSize: 13, color: DARK_TEXT, fontFace: "Microsoft YaHei", valign: "middle"
    });
  });

  // 版权声明
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 4.1, w: 9, h: 1.25,
    fill: { color: WHITE }, line: { color: LIGHT_GRAY }, shadow: makeShadow()
  });
  slide.addText("版权声明", { x: 0.7, y: 4.2, w: 8.6, h: 0.35, fontSize: 13, bold: true, color: VIVO_ACCENT, fontFace: "Microsoft YaHei" });
  slide.addText("在同等条件下，vivo 大赛组委会（维旺迪斯科技有限公司、江西vivo通信有限公司）拥有优先购买权。团队需确保提交作品为原创，不得侵犯第三方知识产权。", {
    x: 0.7, y: 4.55, w: 8.6, h: 0.75, fontSize: 11, color: GRAY_TEXT, fontFace: "Microsoft YaHei"
  });
}

// ============================================================
// Slide 12: 评分标准表
// ============================================================
{
  let slide = pres.addSlide();
  slide.background = { color: WHITE };

  slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.8, fill: { color: VIVO_ACCENT }, line: { color: VIVO_ACCENT } });
  slide.addText("03  产品功能演示", { x: 0.4, y: 0.15, w: 9, h: 0.5, fontSize: 22, bold: true, color: WHITE, fontFace: "Microsoft YaHei" });

  slide.addText("AIGC创新应用作品评分标准（参考）", { x: 0.5, y: 1.05, w: 9, h: 0.5, fontSize: 24, bold: true, color: VIVO_ACCENT, fontFace: "Microsoft YaHei" });
  slide.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.55, w: 3.5, h: 0.04, fill: { color: VIVO_ACCENT }, line: { color: VIVO_ACCENT } });

  const tableData = [
    [
      { text: "评审维度", options: { fill: { color: VIVO_ACCENT }, color: WHITE, bold: true, align: "center", fontFace: "Microsoft YaHei", fontSize: 11 } },
      { text: "评审要点", options: { fill: { color: VIVO_ACCENT }, color: WHITE, bold: true, align: "center", fontFace: "Microsoft YaHei", fontSize: 11 } },
      { text: "评审标准", options: { fill: { color: VIVO_ACCENT }, color: WHITE, bold: true, align: "center", fontFace: "Microsoft YaHei", fontSize: 11 } }
    ],
    [
      { text: "产品定位", options: { rowspan: 4, fill: { color: "F3E8FF" }, color: VIVO_ACCENT, bold: true, align: "center", valign: "middle", fontFace: "Microsoft YaHei", fontSize: 11 } },
      { text: "选择定位", options: { fill: { color: WHITE }, color: DARK_TEXT, fontFace: "Microsoft YaHei", fontSize: 11 } },
      { text: "目标用户画像清晰，覆盖目标用户的核心需求，使用场景痛点明确，产品能够切实解决实际问题，差异化竞争优势明显。", options: { fill: { color: WHITE }, color: DARK_TEXT, fontFace: "Microsoft YaHei", fontSize: 11 } }
    ],
    [
      { text: "产品创新", options: { fill: { color: "F3E8FF" }, color: VIVO_ACCENT, bold: true, align: "center", valign: "middle", fontFace: "Microsoft YaHei", fontSize: 11 } },
      { text: "产品创新性来源：对传统思维的根本性突破，引入新技术/新方法/新思路，产生新价值。突破既有路径依赖，提出全新解决方案的可能性。", options: { fill: { color: WHITE }, color: DARK_TEXT, fontFace: "Microsoft YaHei", fontSize: 11 } }
    ],
    [
      { text: "产品完成度", options: { fill: { color: "F3E8FF" }, color: VIVO_ACCENT, bold: true, align: "center", valign: "middle", fontFace: "Microsoft YaHei", fontSize: 11 } },
      { text: "产品逻辑完整自洽，阶段性功能完备。", options: { fill: { color: WHITE }, color: DARK_TEXT, fontFace: "Microsoft YaHei", fontSize: 11 } }
    ],
    [
      { text: "产品体验", options: { fill: { color: "F3E8FF" }, color: VIVO_ACCENT, bold: true, align: "center", valign: "middle", fontFace: "Microsoft YaHei", fontSize: 11 } },
      { text: "产品交互自然，符合用户习惯，视觉设计美观，无明显使用障碍，能够提供超越常规的使用体验，并提供便捷的操作入口。", options: { fill: { color: WHITE }, color: DARK_TEXT, fontFace: "Microsoft YaHei", fontSize: 11 } }
    ],
    [
      { text: "应用价值", options: { rowspan: 2, fill: { color: "F3E8FF" }, color: VIVO_ACCENT, bold: true, align: "center", valign: "middle", fontFace: "Microsoft YaHei", fontSize: 11 } },
      { text: "技术可行性", options: { fill: { color: WHITE }, color: DARK_TEXT, fontFace: "Microsoft YaHei", fontSize: 11 } },
      { text: "产品能够实现性较强，具备转化为实际产品的路径，技术方案可行。", options: { fill: { color: WHITE }, color: DARK_TEXT, fontFace: "Microsoft YaHei", fontSize: 11 } }
    ],
    [
      { text: "前景规划", options: { fill: { color: "F3E8FF" }, color: VIVO_ACCENT, bold: true, align: "center", valign: "middle", fontFace: "Microsoft YaHei", fontSize: 11 } },
      { text: "目标用户规模足够广泛，使用场景足够明确，使用群体基数足够大，市场空间广阔。", options: { fill: { color: WHITE }, color: DARK_TEXT, fontFace: "Microsoft YaHei", fontSize: 11 } }
    ],
    [
      { text: "产品完成度", options: { rowspan: 2, fill: { color: "F3E8FF" }, color: VIVO_ACCENT, bold: true, align: "center", valign: "middle", fontFace: "Microsoft YaHei", fontSize: 11 } },
      { text: "线上全流程", options: { fill: { color: WHITE }, color: DARK_TEXT, fontFace: "Microsoft YaHei", fontSize: 11 } },
      { text: "主要提交或原型的产品原型、产品介绍及展示demo。", options: { fill: { color: WHITE }, color: DARK_TEXT, fontFace: "Microsoft YaHei", fontSize: 11 } }
    ],
    [
      { text: "线下答辩", options: { fill: { color: "F3E8FF" }, color: VIVO_ACCENT, bold: true, align: "center", valign: "middle", fontFace: "Microsoft YaHei", fontSize: 11 } },
      { text: "提交参赛团队完整的产品介绍（含视频或可运行demo）、技术架构说明，获取数据或评估价值的渠道和效果。", options: { fill: { color: WHITE }, color: DARK_TEXT, fontFace: "Microsoft YaHei", fontSize: 11 } }
    ],
    [
      { text: "大模型应用情况\n（含创意加分项）", options: { rowspan: 2, fill: { color: VIVO_ACCENT }, color: WHITE, bold: true, align: "center", valign: "middle", fontFace: "Microsoft YaHei", fontSize: 11 } },
      { text: "大模型应用", options: { fill: { color: "F3E8FF" }, color: VIVO_ACCENT, bold: true, align: "center", fontFace: "Microsoft YaHei", fontSize: 11 } },
      { text: "有关参赛团队是否对大模型进行微调或使用自建大模型的详细说明，以及通过API调用实现产品功能的技术路径。", options: { fill: { color: "F3E8FF" }, color: DARK_TEXT, fontFace: "Microsoft YaHei", fontSize: 11 } }
    ]
  ];

  slide.addTable(tableData, {
    x: 0.5, y: 1.7, w: 9,
    colW: [1.5, 1.3, 6.2],
    border: { pt: 0.5, color: LIGHT_GRAY },
    rowH: 0.38,
    fontFace: "Microsoft YaHei"
  });
}

// ============================================================
// Slide 13: 致谢页
// ============================================================
{
  let slide = pres.addSlide();
  slide.background = { color: VIVO_DARK };

  // 装饰线
  slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.1, fill: { color: VIVO_PURPLE }, line: { color: VIVO_PURPLE } });
  slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.525, w: 10, h: 0.1, fill: { color: VIVO_PURPLE }, line: { color: VIVO_PURPLE } });

  // 中心文字
  slide.addText("感谢聆听", { x: 0, y: 1.8, w: 10, h: 0.9, fontSize: 52, bold: true, color: WHITE, align: "center", fontFace: "Microsoft YaHei" });
  slide.addShape(pres.shapes.RECTANGLE, { x: 4, y: 2.7, w: 2, h: 0.05, fill: { color: VIVO_PURPLE }, line: { color: VIVO_PURPLE } });
  slide.addText("THANK YOU", { x: 0, y: 2.85, w: 10, h: 0.5, fontSize: 20, color: VIVO_PURPLE, align: "center", fontFace: "Arial", charSpacing: 6 });

  slide.addText("欢迎提问与交流", { x: 0, y: 3.6, w: 10, h: 0.5, fontSize: 18, color: GRAY_TEXT, align: "center", fontFace: "Microsoft YaHei" });
  slide.addText("2026年中国高校计算机大赛 - AIGC创新赛 · 工友通", { x: 0, y: 4.2, w: 10, h: 0.4, fontSize: 13, color: GRAY_TEXT, align: "center", fontFace: "Microsoft YaHei" });
}

// ============================================================
// 保存文件
// ============================================================
const outputPath = path.join("C:\\Users\\30742\\Desktop", "vivoAIGC赛事.pptx");
pres.writeFile({ fileName: outputPath })
  .then(() => {
    console.log("PPT 创建成功！保存路径：" + outputPath);
    console.log("共 " + pres.slides.length + " 页");
  })
  .catch(err => {
    console.error("创建失败：", err);
    process.exit(1);
  });
