# 部署指南

## 环境要求

### 软件要求
- Docker 20.10+
- Docker Compose 2.0+
- Node.js 18+ (本地开发)
- Python 3.9+ (本地开发)
- Poetry (Python包管理)
- pnpm (Node.js包管理)

### 硬件要求
- 内存: 最低2GB，推荐4GB+
- 存储: 最低10GB可用空间
- 网络: 稳定的互联网连接

### 外部依赖
- PostgreSQL 13+ 数据库
- Dify平台访问权限
- SSL证书（生产环境）

## 快速部署

### 1. 克隆项目
```bash
git clone https://github.com/magatamaclub/rag_ui.git
cd rag_ui_ant_design
```

### 2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库和应用参数
vim .env
```

### 3. 启动服务
```bash
# 本地开发模式
./start-dev.sh

# 或者使用Docker
docker-compose up --build
```

## Docker部署

### 使用Docker Compose（推荐）

#### 完整的docker-compose.yml配置
```yaml
version: '3.8'

services:
  # PostgreSQL数据库
  db:
    image: postgres:13-alpine
    container_name: rag-postgres
    environment:
      POSTGRES_DB: ${DB_NAME:-rag_ui_db}
      POSTGRES_USER: ${DB_USER:-rag_user}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-secure_password}
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-db.sql:/docker-entrypoint-initdb.d/init-db.sql
    ports:
      - "${DB_PORT:-5432}:5432"
    networks:
      - rag-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-rag_user}"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis缓存（可选）
  redis:
    image: redis:7-alpine
    container_name: rag-redis
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - rag-network
    restart: unless-stopped

  # FastAPI后端
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: rag-backend
    environment:
      - DB_HOST=db
      - DB_PORT=5432
      - DB_NAME=${DB_NAME:-rag_ui_db}
      - DB_USER=${DB_USER:-rag_user}
      - DB_PASSWORD=${DB_PASSWORD:-secure_password}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - REDIS_URL=redis://redis:6379
    ports:
      - "${BACKEND_PORT:-8000}:8000"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    networks:
      - rag-network
    restart: unless-stopped
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # React前端
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        - API_URL=${API_URL:-http://localhost:8000}
    container_name: rag-frontend
    ports:
      - "${FRONTEND_PORT:-80}:80"
    depends_on:
      backend:
        condition: service_healthy
    networks:
      - rag-network
    restart: unless-stopped

  # Nginx反向代理
  nginx:
    image: nginx:alpine
    container_name: rag-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - frontend
      - backend
    networks:
      - rag-network
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:

networks:
  rag-network:
    driver: bridge
```

#### 启动完整环境
```bash
# 构建并启动所有服务
docker-compose up --build -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
```

### 单独部署各服务

#### 部署数据库
```bash
docker run -d \
  --name rag-postgres \
  --network rag-network \
  -e POSTGRES_DB=rag_ui_db \
  -e POSTGRES_USER=rag_user \
  -e POSTGRES_PASSWORD=secure_password \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:13-alpine
```

#### 部署后端
```bash
cd backend
docker build -t rag-backend .
docker run -d \
  --name rag-backend \
  --network rag-network \
  -e DB_HOST=rag-postgres \
  -e DB_PORT=5432 \
  -e DB_NAME=rag_ui_db \
  -e DB_USER=rag_user \
  -e DB_PASSWORD=secure_password \
  -p 8000:8000 \
  -v $(pwd)/uploads:/app/uploads \
  rag-backend
```

#### 部署前端
```bash
cd frontend
docker build -t rag-frontend .
docker run -d \
  --name rag-frontend \
  --network rag-network \
  -p 80:80 \
  rag-frontend
```

## 生产环境配置

### 环境变量配置
```env
# 生产环境数据库
DB_HOST=your-db-host.com
DB_PORT=5432
DB_NAME=rag_production
DB_USER=rag_user
DB_PASSWORD=very_secure_password_here

# 应用配置
APP_HOST=0.0.0.0
APP_PORT=8000
APP_DEBUG=false
APP_ENV=production

# JWT配置
JWT_SECRET_KEY=your-very-secure-secret-key-minimum-32-characters
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# Dify配置
DEFAULT_DIFY_API_URL=https://api.dify.ai/v1
DEFAULT_DIFY_API_KEY=your-dify-api-key

# 安全配置
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com

# 上传配置
MAX_FILE_SIZE=10485760  # 10MB
UPLOAD_PATH=/app/uploads
```

### Nginx反向代理配置
```nginx
# /etc/nginx/nginx.conf
upstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:80;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # 重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL配置
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # 安全头
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
    
    # 前端静态文件
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # API接口
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 支持长连接和流式响应
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_buffering off;
        proxy_cache off;
    }
    
    # WebSocket支持
    location /ws/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # 文件上传限制
    client_max_body_size 10M;
    
    # 压缩配置
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
}
```

### SSL证书配置
```bash
# 使用Let's Encrypt获取免费SSL证书
# 安装certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 自动续期
sudo crontab -e
# 添加行: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 监控和维护

### 健康检查
```bash
# 检查所有服务状态
docker-compose ps

# 查看服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f nginx

# 检查API健康状态
curl -f http://localhost:8000/health

# 检查前端状态
curl -f http://localhost/
```

### 日志管理
```bash
# 配置日志轮转
cat > /etc/logrotate.d/rag-ui << EOF
/var/log/rag-ui/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    postrotate
        docker-compose restart nginx
    endscript
}
EOF
```

### 备份数据库
```bash
# 创建备份脚本
cat > backup-db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/rag_ui_backup_$TIMESTAMP.sql"

mkdir -p $BACKUP_DIR

docker exec rag-postgres pg_dump -U rag_user rag_ui_db > $BACKUP_FILE

# 压缩备份文件
gzip $BACKUP_FILE

# 删除7天前的备份
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "Database backup completed: $BACKUP_FILE.gz"
EOF

chmod +x backup-db.sh

# 设置定时备份
crontab -e
# 添加行: 0 2 * * * /path/to/backup-db.sh
```

### 恢复数据库
```bash
# 恢复备份
gunzip -c backup_file.sql.gz | docker exec -i rag-postgres psql -U rag_user rag_ui_db
```

### 更新部署
```bash
# 拉取最新代码
git pull origin main

# 重新构建和部署
docker-compose down
docker-compose up --build -d

# 验证部署
docker-compose ps
curl -f http://localhost:8000/health
```

### 性能监控
```bash
# 安装监控工具
docker run -d \
  --name rag-monitoring \
  -p 3000:3000 \
  -v grafana-storage:/var/lib/grafana \
  grafana/grafana

# 系统资源监控
docker stats

# 数据库连接监控
docker exec rag-postgres psql -U rag_user -d rag_ui_db -c "SELECT count(*) FROM pg_stat_activity;"
```

## 故障排除

### 常见问题

1. **容器启动失败**
   ```bash
   # 检查端口占用
   netstat -tulpn | grep :8000
   sudo lsof -i :8000
   
   # 检查日志
   docker-compose logs backend
   
   # 检查磁盘空间
   df -h
   ```

2. **数据库连接失败**
   ```bash
   # 验证数据库容器状态
   docker exec rag-postgres pg_isready -U rag_user
   
   # 检查网络连接
   docker network ls
   docker network inspect rag_network
   
   # 测试连接
   docker exec rag-postgres psql -U rag_user -d rag_ui_db -c "SELECT 1;"
   ```

3. **前端无法访问后端**
   ```bash
   # 检查代理配置
   curl -v http://localhost/api/health
   
   # 验证CORS设置
   curl -H "Origin: http://localhost" -v http://localhost:8000/api/health
   
   # 检查防火墙
   sudo ufw status
   ```

4. **SSL证书问题**
   ```bash
   # 检查证书有效期
   sudo certbot certificates
   
   # 测试证书
   openssl s_client -connect your-domain.com:443 -servername your-domain.com
   
   # 强制续期
   sudo certbot renew --force-renewal
   ```

### 调试命令
```bash
# 进入容器调试
docker exec -it rag-backend bash
docker exec -it rag-frontend sh
docker exec -it rag-postgres psql -U rag_user rag_ui_db

# 查看容器资源使用
docker stats --no-stream

# 查看网络配置
docker network inspect rag_network

# 检查挂载卷
docker volume ls
docker volume inspect rag_ui_ant_design_postgres_data
```

### 紧急恢复
```bash
# 快速重启所有服务
docker-compose restart

# 仅重启特定服务
docker-compose restart backend

# 完全重建
docker-compose down -v  # 注意：会删除数据！
docker-compose up --build
```

---

*部署指南版本: v1.0 | 最后更新: 2025-07-27*
