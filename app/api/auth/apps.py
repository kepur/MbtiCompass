from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
import httpx
import os

app = FastAPI()

# 挂载静态文件目录（将当前目录作为静态文件根目录）
app.mount("/static", StaticFiles(directory="."), name="static")

# 代理路由
@app.get("/proxy/{path:path}")
async def proxy(path: str):
    url = path  # 直接使用完整 URL
    print(f"Proxying request to: {url}")
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    print(f"Response status: {response.status_code}")
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Content-Type": response.headers.get("Content-Type", "application/octet-stream"),
        }
    )

# 根路径重定向到 test.html
@app.get("/")
async def serve_index():
    with open("test.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return Response(content=html_content, media_type="text/html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)