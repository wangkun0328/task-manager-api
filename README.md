# Task Manager API

[![CI](https://github.com/wangkun0328/task-manager-api/actions/workflows/ci.yml/badge.svg)](https://github.com/wangkun0328/task-manager-api/actions/workflows/ci.yml)

## 项目简介

一个基于 Python + FastAPI 构建的 RESTful 任务管理服务，支持任务的增删改查（CRUD）。项目展示了完整的 DevOps 工程能力，包括 Docker 容器化、Kubernetes 部署和 GitHub Actions CI/CD 自动化。

## 技术栈

- **语言**: Python 3.11+
- **框架**: FastAPI (异步 ASGI)
- **服务器**: Uvicorn
- **测试**: pytest + httpx
- **代码检查**: Ruff
- **容器化**: Docker (多阶段构建)
- **编排**: Kubernetes (Minikube 本地部署)
- **CI/CD**: GitHub Actions
- **安全扫描**: Trivy

## 本地开发环境搭建

### 前置条件

- Python 3.11+
- pip

### 安装依赖

```bash
# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 运行服务

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
```

### 访问 API 文档

服务启动后访问 http://localhost:8080/docs 查看 Swagger UI 交互式文档。

## API 接口

| 方法 | 路径 | 功能 | 状态码 |
|------|------|------|--------|
| GET | /health | 健康检查 | 200 |
| GET | /tasks | 获取所有任务 | 200 |
| GET | /tasks/{id} | 获取单个任务 | 200 / 404 |
| POST | /tasks | 创建任务 | 201 / 400 |
| PUT | /tasks/{id} | 更新任务 | 200 / 404 |
| DELETE | /tasks/{id} | 删除任务 | 204 / 404 |

### 任务数据模型

```json
{
  "id": "uuid-string",
  "title": "任务标题",
  "description": "任务描述",
  "status": "todo | in_progress | done",
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-01-01T00:00:00Z"
}
```

## Docker 构建和运行

### 构建镜像

```bash
docker build -t task-manager-api .
```

### 运行容器

```bash
docker run -p 8080:8080 task-manager-api
```

### 使用 docker-compose（可选）

```bash
docker compose up -d
```

### 验证

```bash
curl http://localhost:8080/health
```

## Minikube 部署

### 启动 Minikube

```bash
minikube start \
    --driver=docker \
    --cpus=4 \
    --memory=4096m \
    --cni=flannel \
    --disk-size=10g \
    --image-mirror-country='cn' \
    --image-repository='registry.cn-hangzhou.aliyuncs.com/google_containers'
```

### 启用 Ingress 插件

```bash
minikube addons enable ingress
```

### 部署到 Kubernetes

```bash
kubectl apply -f k8s/
```

### 验证部署

```bash
# 检查 Pod 状态
kubectl get pods -n task-manager

# 查看所有资源
kubectl get all -n task-manager

# 通过 Ingress 访问
curl -H "Host: task-manager.local" http://$(minikube ip)/health
curl -H "Host: task-manager.local" http://$(minikube ip)/tasks
```

详见 [k8s/README.md](k8s/README.md) 获取详细部署说明及常见问题排查。

## 运行测试

```bash
# 安装测试依赖
pip install -r requirements.txt

# 运行测试
pytest src/tests/ -v --cov=src/ --cov-fail-under=60
```

## CI/CD 流水线

项目使用 GitHub Actions 实现自动化 CI/CD，包含以下阶段：

1. **Lint**: Ruff 代码风格检查
2. **Test**: 运行单元测试（覆盖率 >60%）
3. **Build**: 构建 Docker 镜像并推送到 GHCR
4. **Security Scan**: Trivy 镜像漏洞扫描

触发条件：Push 到 main 分支 或 PR 到 main 分支。
