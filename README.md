# Personal Web

目前暂定是记录学习目标与工作量的个人网页全栈项目。
技术栈：Vue 3 + FastAPI + SQLite，部署于 Render。

## 当前进度

- [x] FastAPI 最小接口跑通
- [x] 依赖清单 requirements.txt
- [ ] 数据库设计（W2）
- [ ] 核心接口（W3）
- [ ] 前端页面（W4）
- [ ] 公网部署（W5）

## 本地运行

环境要求：Python 3.8+

```bash
# 1. 克隆仓库
git clone https://github.com/aocoffee6-afk/AcoSpace.git
cd AcoSpace

# 2. 安装依赖
python -m pip install -r requirements.txt

# 3. 启动服务
python -m uvicorn main:app --reload

# 4. 浏览器访问
# http://127.0.0.1:8000        返回 {"message":"ok"}
# http://127.0.0.1:8000/docs   接口文档