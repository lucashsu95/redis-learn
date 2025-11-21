# ☁️ 雲端部署指南

本文檔將介紹如何將隨機匿名聊天室部署到各種雲端平台。

## 📋 目錄

- [部署前準備](#部署前準備)
- [Render 部署（推薦）](#render-部署推薦)
- [Heroku 部署](#heroku-部署)
- [Railway 部署](#railway-部署)
- [Google Cloud Run 部署](#google-cloud-run-部署)
- [AWS Elastic Beanstalk 部署](#aws-elastic-beanstalk-部署)
- [自架 VPS 部署](#自架-vps-部署)

---

## 🎯 部署前準備

### 1. 確保本地運行正常

```bash
# 測試本地環境
python app.py
```

### 2. 準備 Redis 資料庫

由於你已經使用 Redis Cloud，無需額外設定。確保 `.env` 中的連線資訊正確：

```env
REDIS_HOST=redis-11981.c256.us-east-1-2.ec2.cloud.redislabs.com
REDIS_PORT=11981
REDIS_USERNAME=default
REDIS_PASSWORD=cuPy9eDoB6PeMQ6tzRP6hHyBJSZ6ZZsn
```

### 3. 檢查必要檔案

確保以下檔案存在且正確：

- ✅ `requirements.txt` - Python 依賴
- ✅ `app.py` - 主程式
- ✅ `.env` 或環境變數設定
- ✅ `templates/index.html` - 前端頁面

---

## 🚀 Render 部署（推薦）

Render 提供免費方案，支援 WebSocket，部署簡單。

### 步驟 1：準備部署檔案

創建 `render.yaml`：

```yaml
services:
  - type: web
    name: chat-app
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python app.py
    envVars:
      - key: REDIS_HOST
        value: redis-11981.c256.us-east-1-2.ec2.cloud.redislabs.com
      - key: REDIS_PORT
        value: 11981
      - key: REDIS_USERNAME
        value: default
      - key: REDIS_PASSWORD
        sync: false
      - key: FLASK_SECRET_KEY
        generateValue: true
      - key: FLASK_PORT
        value: 10000
      - key: FLASK_DEBUG
        value: False
```

### 步驟 2：修改 app.py 監聽設定

在 `app.py` 最後修改為：

```python
if __name__ == '__main__':
    port = int(os.getenv('PORT', os.getenv('FLASK_PORT', 5000)))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    socketio.run(app, host='0.0.0.0', port=port, debug=debug)
```

### 步驟 3：部署到 Render

1. 前往 [Render 官網](https://render.com/)
2. 註冊/登入帳號
3. 點擊「New +」→「Web Service」
4. 連接你的 GitHub 倉庫
5. 選擇 `chat` 資料夾（或整個倉庫）
6. 設定環境變數：
   - `REDIS_HOST`
   - `REDIS_PORT`
   - `REDIS_USERNAME`
   - `REDIS_PASSWORD`
   - `FLASK_SECRET_KEY`
7. 點擊「Create Web Service」

### 步驟 4：訪問應用

部署完成後，Render 會提供一個 URL，例如：
```
https://your-app-name.onrender.com
```

---

## 🟣 Heroku 部署

### 步驟 1：安裝 Heroku CLI

```bash
# Windows (使用 Chocolatey)
choco install heroku-cli

# macOS
brew tap heroku/brew && brew install heroku

# 或下載安裝程式
# https://devcenter.heroku.com/articles/heroku-cli
```

### 步驟 2：創建 Procfile

在專案根目錄創建 `Procfile`（無副檔名）：

```
web: python app.py
```

### 步驟 3：創建 runtime.txt

指定 Python 版本：

```
python-3.11.0
```

### 步驟 4：修改 app.py

確保監聽 `0.0.0.0` 和使用 `PORT` 環境變數：

```python
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
```

### 步驟 5：部署

```bash
# 登入 Heroku
heroku login

# 創建應用
heroku create your-chat-app-name

# 設定環境變數
heroku config:set REDIS_HOST=redis-11981.c256.us-east-1-2.ec2.cloud.redislabs.com
heroku config:set REDIS_PORT=11981
heroku config:set REDIS_USERNAME=default
heroku config:set REDIS_PASSWORD=cuPy9eDoB6PeMQ6tzRP6hHyBJSZ6ZZsn
heroku config:set FLASK_SECRET_KEY=your-secret-key
heroku config:set FLASK_DEBUG=False

# 推送代碼
git add .
git commit -m "Prepare for Heroku deployment"
git push heroku main

# 開啟應用
heroku open
```

---

## 🚂 Railway 部署

Railway 提供簡單的部署流程和免費額度。

### 步驟 1：準備專案

確保 `app.py` 使用環境變數：

```python
if __name__ == '__main__':
    port = int(os.getenv('PORT', os.getenv('FLASK_PORT', 5000)))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
```

### 步驟 2：部署到 Railway

1. 前往 [Railway.app](https://railway.app/)
2. 使用 GitHub 登入
3. 點擊「New Project」
4. 選擇「Deploy from GitHub repo」
5. 選擇你的倉庫
6. Railway 會自動偵測 Python 專案

### 步驟 3：設定環境變數

在 Railway 控制台：
1. 點擊你的服務
2. 進入「Variables」分頁
3. 添加環境變數：
   ```
   REDIS_HOST=redis-11981.c256.us-east-1-2.ec2.cloud.redislabs.com
   REDIS_PORT=11981
   REDIS_USERNAME=default
   REDIS_PASSWORD=cuPy9eDoB6PeMQ6tzRP6hHyBJSZ6ZZsn
   FLASK_SECRET_KEY=your-secret-key
   FLASK_DEBUG=False
   ```

### 步驟 4：訪問應用

Railway 會自動生成一個 URL。

---

## 🐳 Google Cloud Run 部署

使用 Docker 容器化部署。

### 步驟 1：創建 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080
ENV FLASK_DEBUG=False

CMD ["python", "app.py"]
```

### 步驟 2：創建 .dockerignore

```
.env
.git
.gitignore
__pycache__
*.pyc
*.pyo
*.pyd
.Python
venv/
```

### 步驟 3：修改 app.py

```python
if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
```

### 步驟 4：部署到 Cloud Run

```bash
# 安裝 Google Cloud SDK
# https://cloud.google.com/sdk/docs/install

# 登入 Google Cloud
gcloud auth login

# 設定專案
gcloud config set project YOUR_PROJECT_ID

# 構建並部署
gcloud run deploy chat-app \
  --source . \
  --platform managed \
  --region asia-east1 \
  --allow-unauthenticated \
  --set-env-vars REDIS_HOST=redis-11981.c256.us-east-1-2.ec2.cloud.redislabs.com,REDIS_PORT=11981,REDIS_USERNAME=default,REDIS_PASSWORD=cuPy9eDoB6PeMQ6tzRP6hHyBJSZ6ZZsn,FLASK_SECRET_KEY=your-secret-key,FLASK_DEBUG=False
```

---

## ☁️ AWS Elastic Beanstalk 部署

### 步驟 1：安裝 EB CLI

```bash
pip install awsebcli
```

### 步驟 2：初始化 EB

```bash
eb init -p python-3.11 chat-app --region ap-northeast-1
```

### 步驟 3：創建環境變數設定

創建 `.ebextensions/environment.config`：

```yaml
option_settings:
  aws:elasticbeanstalk:application:environment:
    REDIS_HOST: redis-11981.c256.us-east-1-2.ec2.cloud.redislabs.com
    REDIS_PORT: 11981
    REDIS_USERNAME: default
    REDIS_PASSWORD: cuPy9eDoB6PeMQ6tzRP6hHyBJSZ6ZZsn
    FLASK_SECRET_KEY: your-secret-key
    FLASK_DEBUG: False
```

### 步驟 4：部署

```bash
# 創建環境並部署
eb create chat-app-env

# 開啟應用
eb open
```

---

## 🖥️ 自架 VPS 部署

適用於 DigitalOcean、Linode、AWS EC2 等。

### 步驟 1：連接到伺服器

```bash
ssh user@your-server-ip
```

### 步驟 2：安裝必要軟體

```bash
# 更新系統
sudo apt update && sudo apt upgrade -y

# 安裝 Python 和 pip
sudo apt install python3 python3-pip python3-venv -y

# 安裝 Nginx
sudo apt install nginx -y
```

### 步驟 3：上傳專案

```bash
# 在本地機器上
scp -r chat/ user@your-server-ip:/home/user/
```

或使用 Git：

```bash
# 在伺服器上
git clone https://github.com/yourusername/redis-learn.git
cd redis-learn/chat
```

### 步驟 4：設定虛擬環境

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 步驟 5：創建 .env 檔案

```bash
nano .env
```

填入環境變數：

```env
REDIS_HOST=redis-11981.c256.us-east-1-2.ec2.cloud.redislabs.com
REDIS_PORT=11981
REDIS_USERNAME=default
REDIS_PASSWORD=cuPy9eDoB6PeMQ6tzRP6hHyBJSZ6ZZsn
FLASK_SECRET_KEY=your-secret-key
FLASK_PORT=5000
FLASK_DEBUG=False
```

### 步驟 6：使用 Gunicorn + Nginx

安裝 Gunicorn：

```bash
pip install gunicorn eventlet
```

創建 systemd 服務檔案：

```bash
sudo nano /etc/systemd/system/chat.service
```

內容：

```ini
[Unit]
Description=Chat App
After=network.target

[Service]
User=user
WorkingDirectory=/home/user/chat
Environment="PATH=/home/user/chat/venv/bin"
ExecStart=/home/user/chat/venv/bin/gunicorn -k eventlet -w 1 -b 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target
```

啟動服務：

```bash
sudo systemctl start chat
sudo systemctl enable chat
sudo systemctl status chat
```

### 步驟 7：設定 Nginx

```bash
sudo nano /etc/nginx/sites-available/chat
```

內容：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

啟用網站：

```bash
sudo ln -s /etc/nginx/sites-available/chat /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 步驟 8：設定 SSL（可選）

使用 Let's Encrypt：

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## 🔒 安全建議

### 1. 使用強密碼

確保 `FLASK_SECRET_KEY` 使用強隨機字串：

```python
import secrets
print(secrets.token_hex(32))
```

### 2. 啟用 HTTPS

所有生產環境都應使用 HTTPS，尤其是 WebSocket 連線。

### 3. 限制 CORS

修改 `app.py`：

```python
socketio = SocketIO(app, cors_allowed_origins=['https://your-domain.com'])
```

### 4. 環境變數保護

- 不要將 `.env` 提交到 Git
- 使用平台提供的環境變數管理功能
- 定期更換密碼和密鑰

### 5. Redis 安全

- 使用強密碼
- 啟用 SSL/TLS 連線
- 限制 IP 白名單

---

## 📊 效能優化

### 1. 使用生產級 WSGI 伺服器

不要使用 Flask 內建的開發伺服器。建議使用：
- Gunicorn + Eventlet
- uWSGI

### 2. 啟用 WebSocket 壓縮

```python
socketio = SocketIO(
    app, 
    cors_allowed_origins='*',
    compression_threshold=1024
)
```

### 3. Redis 連線池

```python
r = redis.Redis(
    host=os.getenv('REDIS_HOST'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True,
    username=os.getenv('REDIS_USERNAME', 'default'),
    password=os.getenv('REDIS_PASSWORD'),
    max_connections=50  # 設定連線池大小
)
```

### 4. 監控與日誌

使用服務如：
- Sentry（錯誤追蹤）
- LogDNA（日誌管理）
- New Relic（效能監控）

---

## 🐛 常見問題排查

### WebSocket 連線失敗

**問題：** 瀏覽器無法建立 WebSocket 連線

**解決：**
1. 確保使用 `host='0.0.0.0'`
2. 檢查防火牆設定
3. 確認平台支援 WebSocket
4. 使用 HTTPS（某些平台要求）

### Redis 連線超時

**問題：** `Redis 連線失敗: Timeout`

**解決：**
1. 檢查 Redis 服務狀態
2. 確認網路連線
3. 檢查防火牆規則
4. 增加超時時間：
   ```python
   r = redis.Redis(
       ...,
       socket_connect_timeout=5,
       socket_timeout=5
   )
   ```

### 應用崩潰重啟

**問題：** 應用頻繁重啟

**解決：**
1. 檢查日誌找出錯誤
2. 確保記憶體足夠
3. 檢查 Worker 數量設定
4. 使用 `try-except` 捕獲異常

---

## 📈 擴展建議

### 橫向擴展

使用 Redis Pub/Sub 支援多個伺服器實例：

```python
# 使用 Redis 作為訊息隊列
socketio = SocketIO(app, message_queue='redis://...')
```

### 負載平衡

使用 Nginx 或雲端負載平衡器分散流量。

### CDN 加速

將靜態資源（CSS、JS）上傳到 CDN。

---

## 📚 相關資源

- [Flask-SocketIO 文檔](https://flask-socketio.readthedocs.io/)
- [Eventlet 文檔](https://eventlet.net/)
- [Redis 官方文檔](https://redis.io/docs/)
- [Nginx 設定指南](https://nginx.org/en/docs/)

---

## ✅ 部署檢查清單

- [ ] 本地測試通過
- [ ] 環境變數設定正確
- [ ] Redis 連線正常
- [ ] 修改 `host='0.0.0.0'`
- [ ] 使用 `PORT` 環境變數
- [ ] 關閉 DEBUG 模式
- [ ] 設定強密鑰
- [ ] 啟用 HTTPS
- [ ] 限制 CORS
- [ ] 測試 WebSocket 連線
- [ ] 設定監控和日誌
- [ ] 備份環境變數

---

## 🎉 完成

恭喜！你已成功將聊天室部署到雲端。如有問題，請參考各平台的官方文檔或在 GitHub 提 Issue。
