# 阶段一: 构建Vue前端
FROM node:18-alpine as frontend-builder

# 设置工作目录
WORKDIR /app/frontend

# 复制前端项目文件
COPY frontend/package*.json ./

# 安装依赖
RUN npm ci

# 复制前端源代码
COPY frontend/ ./

# 构建前端应用
RUN npm run build

# 阶段二: 构建Python后端
FROM python:3.10-slim as backend-builder

# 设置工作目录
WORKDIR /app

# 安装系统依赖和构建依赖
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    ca-certificates \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt /app/

# 安装 Python 依赖
RUN pip install --no-cache-dir --user -r requirements.txt

# 阶段三: 运行阶段
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制Python依赖
COPY --from=backend-builder /root/.local /root/.local

# 确保脚本路径在PATH中
ENV PATH=/root/.local/bin:$PATH

# 设置环境变量
ENV PYTHONPATH=/app

# 复制应用代码
COPY . /app/

# 从前端构建阶段复制生成的静态文件到后端的前端目录
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# 暴露端口
EXPOSE 8888

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8888/api/config || exit 1

# 启动命令
CMD ["python", "web_server.py"]