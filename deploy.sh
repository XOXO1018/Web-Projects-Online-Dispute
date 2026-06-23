#!/bin/bash
# ===================================================
# 智链解纷 一键部署脚本
# 使用方式：chmod +x deploy.sh && ./deploy.sh
# ===================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

echo "============================================="
echo "  智链解纷 V1.0 部署脚本"
echo "============================================="

# 检查依赖
command -v docker >/dev/null 2>&1 || log_error "未找到 Docker，请先安装 Docker"
command -v docker-compose >/dev/null 2>&1 || command -v docker compose >/dev/null 2>&1 || log_error "未找到 docker-compose"

# 检查 .env 文件
if [ ! -f ".env" ]; then
    log_warn ".env 文件不存在，从模板创建..."
    cp .env.example .env
    log_warn "请编辑 .env 文件修改密码和密钥后重新运行"
    exit 1
fi

# 创建必要目录
log_info "创建目录结构..."
mkdir -p uploads logs/backend logs/nginx nginx/ssl

# 生成自签名SSL证书（开发用）
if [ ! -f "nginx/ssl/cert.pem" ]; then
    log_info "生成自签名SSL证书（开发用）..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/key.pem \
        -out nginx/ssl/cert.pem \
        -subj "/C=CN/ST=Beijing/L=Beijing/O=智链解纷/CN=localhost" 2>/dev/null || log_warn "openssl 未安装，跳过SSL证书生成"
fi

# 停止旧容器
log_info "停止旧容器..."
docker-compose down 2>/dev/null || true

# 构建和启动
log_info "构建镜像..."
docker-compose build --no-cache

log_info "启动服务..."
docker-compose up -d

# 等待数据库就绪
log_info "等待数据库启动..."
sleep 15

# 初始化数据库
log_info "初始化数据库数据..."
docker-compose exec backend python migrations/seed.py || log_warn "数据初始化失败（可能已初始化）"

log_success "部署完成！"
echo ""
echo "访问地址："
echo "  前端：  http://localhost"
echo "  API文档：http://localhost/docs"
echo ""
echo "默认账号："
echo "  管理员：admin@zjfl.com / admin123"
echo "  演示企业：demo@zjfl.com / Demo@12345"
echo ""
echo "查看日志：docker-compose logs -f"
