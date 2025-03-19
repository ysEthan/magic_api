# Build stage
FROM python:3.12.5-slim as builder

# 设置工作目录
WORKDIR /app

# 安装最小必需的依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    pkg-config \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 替换为国内源
RUN mkdir -p ~/.pip \
    && echo "[global]" > ~/.pip/pip.conf \
    && echo "index-url=https://mirrors.aliyun.com/pypi/simple" >> ~/.pip/pip.conf \
    && echo "trusted-host=mirrors.aliyun.com" >> ~/.pip/pip.conf

RUN python -m pip install --upgrade pip

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制源代码和配置文件
COPY . .
COPY .env.example /app/.env.example

# 创建启动脚本
COPY <<'EOF' /docker-entrypoint.sh
#!/bin/sh
set -e

# 如果没有 .env 文件，使用 .env.example
if [ ! -f /app/.env ]; then
    echo "No .env file found, using .env.example as default"
    cp /app/.env.example /app/.env
fi

# 设置基本环境变量
export PYTHONUNBUFFERED=1
export DJANGO_SETTINGS_MODULE=mysite.settings

# 加载环境变量
while IFS='=' read -r key value; do
    # 忽略注释和空行
    if [[ ! $key =~ ^#.*$ ]] && [[ -n $key ]]; then
        # 移除可能的引号和空格
        value=$(echo "$value" | tr -d '"' | tr -d "'")
        export "$key=$value"
    fi
done < /app/.env

# 确保关键环境变量已设置
if [ -z "$SECRET_KEY" ]; then
    echo "ERROR: SECRET_KEY is not set!"
    exit 1
fi

# 执行数据库迁移
python manage.py migrate

# 启动 Django 服务
exec python manage.py runserver 0.0.0.0:8002
EOF

RUN chmod +x /docker-entrypoint.sh

# 暴露容器端口
EXPOSE 8002

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8002/api/health || exit 1

# 启动命令
CMD ["/docker-entrypoint.sh"]