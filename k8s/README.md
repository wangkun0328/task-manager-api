# Kubernetes 部署指南

## 前置条件

- Minikube 已安装并运行 (`minikube start`)
- kubectl 已配置指向 Minikube 集群

## 部署步骤

### 1. 构建 Docker 镜像

在部署之前，需要构建 Docker 镜像。如果要在 Minikube 中使用本地镜像：

```bash
# 设置 Docker 环境变量指向 Minikube 的 Docker daemon
eval $(minikube docker-env)

# 构建镜像（将 <username> 替换为你的 GitHub 用户名）
docker build -t ghcr.io/<username>/task-manager-api:latest .
```

如果不想使用本地镜像，可以跳过此步骤。Deployment 中的 `imagePullPolicy: IfNotPresent` 会优先使用本地镜像。

### 2. 应用 Kubernetes 资源清单

按顺序应用所有资源：

```bash
# 创建命名空间
kubectl apply -f k8s/namespace.yaml

# 应用其他资源（顺序不重要，kubectl 会自动处理依赖）
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml

# 或者一次性应用所有资源
kubectl apply -f k8s/
```

### 3. 验证部署

```bash
# 检查 Pod 状态（应该看到 2 个 Running 状态的 Pod）
kubectl get pods -n task-manager

# 查看所有资源
kubectl get all -n task-manager

# 检查 Deployment 状态
kubectl get deployment -n task-manager

# 查看 Pod 日志
kubectl logs -n task-manager -l app.kubernetes.io/name=task-manager-api
```

### 4. 启用 Ingress 并访问

```bash
# 启用 Minikube Ingress 插件
minikube addons enable ingress

# 通过 Ingress 访问（使用 Minikube IP）
MINIKUBE_IP=$(minikube ip)
curl -H "Host: task-manager.local" http://$MINIKUBE_IP/health
curl -H "Host: task-manager.local" http://$MINIKUBE_IP/tasks
```

### 5. 清理

```bash
kubectl delete -f k8s/
```

## 资源说明

| 资源 | 文件 | 说明 |
|------|------|------|
| Namespace | namespace.yaml | 独立命名空间 `task-manager` |
| ConfigMap | configmap.yaml | 非敏感配置（日志级别） |
| Deployment | deployment.yaml | 2 个副本，资源限制，健康探针 |
| Service | service.yaml | ClusterIP，端口 8080 |
| Ingress | ingress.yaml | 域名 `task-manager.local` |
