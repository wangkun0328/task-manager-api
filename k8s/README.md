# Kubernetes 部署指南

## 前置条件

- Minikube 已安装 (`brew install minikube`)
- kubectl 已安装 (`brew install kubectl`)
- Docker Desktop 已安装并运行

## 部署步骤

### 1. 启动 Minikube 集群

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

**参数说明：**

| 参数 | 说明 |
|------|------|
| `--driver=docker` | 使用 Docker 作为虚拟化驱动 |
| `--cpus=4` | 分配 4 核 CPU |
| `--memory=4096m` | 分配 4G 内存 |
| `--cni=flannel` | 使用 flannel 作为网络插件（替代默认 kindnet，更稳定） |
| `--disk-size=10g` | 磁盘大小 10G |
| `--image-mirror-country='cn'` | 使用国内镜像源 |
| `--image-repository=...` | 阿里云镜像仓库，避免 Docker Hub 网络问题 |

### 2. 启用 Ingress 插件

```bash
minikube addons enable ingress

# 等待 Ingress controller 就绪
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s
```

### 3. 构建 Docker 镜像（可选）

如果想在 Minikube 中使用本地构建的镜像：

```bash
# 设置 Docker 环境变量指向 Minikube 的 Docker daemon
eval $(minikube docker-env)

# 构建镜像
docker build -t task-manager/task-manager-api:latest .
```

Deployment 中的 `imagePullPolicy: IfNotPresent` 会优先使用本地镜像。如果使用了私有仓库，Deployment 会自动从仓库拉取。

### 4. 应用 Kubernetes 资源清单

```bash
# 创建命名空间
kubectl apply -f k8s/namespace.yaml

# 应用其他资源
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml

# 或者一次性应用所有资源
kubectl apply -f k8s/
```

### 5. 验证部署

```bash
# 检查 Pod 状态
kubectl get pods -n task-manager

# 查看所有资源
kubectl get all -n task-manager

# 检查 Deployment 状态
kubectl get deployment -n task-manager

# 查看 Pod 日志
kubectl logs -n task-manager -l app.kubernetes.io/name=task-manager-api
```

### 6. 通过 Ingress 访问

```bash
# 通过 Ingress 访问（使用 Minikube IP）
MINIKUBE_IP=$(minikube ip)
curl -H "Host: task-manager.local" http://$MINIKUBE_IP/health
curl -H "Host: task-manager.local" http://$MINIKUBE_IP/tasks
```

### 6.1 通过 port-forward 访问（无需 Ingress 插件）

```bash
# 在后台转发端口到本地
kubectl port-forward -n task-manager svc/task-manager-api 8080:8080 &

# 在另一个终端访问
curl http://localhost:8080/health
curl http://localhost:8080/tasks

# 停止端口转发
kill %1
```

### 7. 清理

```bash
kubectl delete -f k8s/
```

## 常见问题

### Pod 无法调度 (FailedScheduling)

```bash
# 查看节点 taint
kubectl describe node minikube | grep -i taint

# 如果存在 not-ready taint，等待节点 Ready 后会自动消失
kubectl wait --for=condition=Ready node/minikube --timeout=120s
```

### 查看 Pod 异常退出日志

```bash
# 查看当前日志
kubectl logs <pod-name> -n task-manager

# 查看上一次崩溃的日志
kubectl logs <pod-name> -n task-manager --previous
```

### Ingress 创建失败 (webhook connection refused)

说明 Ingress controller 还没就绪，等它 Ready 后再应用：

```bash
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s

kubectl apply -f k8s/ingress.yaml
```

## 资源说明

| 资源 | 文件 | 说明 |
|------|------|------|
| Namespace | namespace.yaml | 独立命名空间 `task-manager` |
| ConfigMap | configmap.yaml | 非敏感配置（日志级别） |
| Deployment | deployment.yaml | 1 个副本，资源限制，健康探针 |
| Service | service.yaml | ClusterIP，端口 8080 |
| Ingress | ingress.yaml | 域名 `task-manager.local` |
