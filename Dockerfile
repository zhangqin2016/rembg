# 使用官方 Python 镜像作为基础镜像
FROM python:3.9-slim

# 设置工作目录为/app
WORKDIR /app

# 复制当前目录下的所有文件到容器的/app目录
COPY . /app

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露应用端口
EXPOSE 5000

# 启动 Flask 应用
CMD ["python", "app.py"]
