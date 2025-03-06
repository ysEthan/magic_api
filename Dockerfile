# Build stage
FROM python:3.12.5-slim as builder

# 设置工作目录
WORKDIR /app


# 替换为国内源
RUN mkdir -p ~/.pip \
    && echo "[global]" > ~/.pip/pip.conf \
    && echo "index-url=https://mirrors.aliyun.com/pypi/simple" >> ~/.pip/pip.conf \
    && echo "trusted-host=mirrors.aliyun.com" >> ~/.pip/pip.conf

RUN python -m pip install --upgrade pip

# 将当前目录下的 requirements.txt 文件复制到容器内的工作目录
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 将当前目录下的项目代码复制到容器内的工作目录
COPY . .

# 设置环境变量
ENV DJANGO_SETTINGS_MODULE=mysite.settings \
    PYTHONUNBUFFERED=1

# 暴露容器内的端口
EXPOSE 8002

# 运行 Django 命令来启动服务器
CMD ["python", "manage.py", "runserver", "0.0.0.0:8002"]