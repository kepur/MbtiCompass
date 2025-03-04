import uvicorn
import socket
import psutil
import platform
from fastapi import FastAPI
from app import create_app
from app.core.logger import log_event

app = create_app()


def get_server_info():
    """ 获取服务器信息 """
    host_name = socket.gethostname()
    ip_address = socket.gethostbyname(host_name)

    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()

    return {
        "host_name": host_name,
        "ip_address": ip_address,
        "cpu_usage": f"{cpu_usage}%",
        "memory_total": f"{memory.total / (1024 * 1024):.2f} MB",
        "memory_used": f"{memory.used / (1024 * 1024):.2f} MB",
        "memory_available": f"{memory.available / (1024 * 1024):.2f} MB",
        "platform": platform.system(),
        "platform_version": platform.version(),
        "python_version": platform.python_version()
    }


@app.get("/health/liveness")
def liveness_probe():
    """ Kubernetes 存活探针 """
    return {
        "status": "alive",
        "server": get_server_info(),
        "module": "FastAPI Service"
    }


@app.get("/health/readiness")
def readiness_probe():
    """ Kubernetes 就绪探针 """
    return {
        "status": "ready",
        "server": get_server_info(),
        "module": "FastAPI Service"
    }


if __name__ == "__main__":
    log_event("fastapi", "🚀 FastAPI 启动中...", "info")
    uvicorn.run("runserver:app", host="127.0.0.1", port=19999, reload=True)
