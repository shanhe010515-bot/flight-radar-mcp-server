FROM python:3.12-slim-bookworm

WORKDIR /app

# 先复制依赖文件
COPY requirements.txt pyproject.toml ./

# 安装 Python 依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制 MCP Server
COPY server.py ./

# Python 日志直接输出
ENV PYTHONUNBUFFERED=1

# Smithery 部署端口
ENV PORT=8081

EXPOSE 8081

# 启动 FastMCP Server
CMD ["python", "server.py"]