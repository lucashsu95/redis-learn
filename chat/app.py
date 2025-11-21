from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
import redis
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'secret!')
# 初始化 SocketIO
socketio = SocketIO(app, cors_allowed_origins='*')

# 初始化 Redis
try:
    r = redis.Redis(
        host=os.getenv('REDIS_HOST'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        decode_responses=True,
        username=os.getenv('REDIS_USERNAME', 'default'),
        password=os.getenv('REDIS_PASSWORD'),
    )
    r.ping()
    print("Redis 連線成功")
except Exception as e:
    print(f"Redis 連線失敗: {e}")

# 常數定義
WAIT_KEY = "wait"

# --- Redis 操作函數 ---

def get_wait_first_key():
    """取得隊伍第一筆資料 (LPop)"""
    return r.lpop(WAIT_KEY)

def add_to_wait_list(user_id):
    """將 ID 加入隊伍尾端 (LPush)"""
    r.lpush(WAIT_KEY, user_id)

def create_chat(id1, id2):
    """建立聊天室 (互相綁定)"""
    r.set(id1, id2)
    r.set(id2, id1)

def remove_chat(id1, id2):
    """移除聊天室"""
    r.delete(id1)
    if id2:
        r.delete(id2)

def get_chat_partner(user_id):
    """查詢對話對象"""
    return r.get(user_id)

# --- WebSocket 事件處理 ---

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    """
    當使用者連線時觸發
    request.sid 是 Flask-SocketIO 自動生成的唯一 Session ID
    """
    user_id = request.sid
    print(f"User connected: {user_id}")

    # 查詢等待列表
    partner_id = get_wait_first_key()

    if partner_id and partner_id != user_id:
        # 有人在等，進行配對
        print(f"配對成功: {user_id} <-> {partner_id}")
        create_chat(user_id, partner_id)
        
        # 通知雙方 (SocketIO 可以直接指定 ID 發送，不需要像 Go 那樣廣播過濾)
        emit('sys_message', {'content': '對方已經加入聊天室'}, to=user_id)
        emit('sys_message', {'content': '對方已經加入聊天室'}, to=partner_id)
    else:
        # 沒人，加入等待列表
        print(f"加入等待: {user_id}")
        add_to_wait_list(user_id)

@socketio.on('message')
def handle_message(data):
    """
    處理使用者傳送的訊息
    """
    user_id = request.sid
    msg_content = data.get('content')
    
    # 查詢聊天對象
    partner_id = get_chat_partner(user_id)
    
    if partner_id:
        # 發送給對方
        emit('chat_message', {'name': 'Stranger', 'content': msg_content}, to=partner_id)
        # 發送給自己 (回顯)
        emit('chat_message', {'name': 'You', 'content': msg_content}, to=user_id)

@socketio.on('next_chat')
def handle_next_chat():
    """
    處理「下一位」功能
    """
    user_id = request.sid
    print(f"User requesting next chat: {user_id}")
    
    partner_id = get_chat_partner(user_id)
    
    # 移除配對關係
    remove_chat(user_id, partner_id)
    
    # 通知對方
    if partner_id:
        socketio.emit('sys_message', {'content': '對方已經離開聊天室'}, to=partner_id)
    
    # 通知自己正在尋找新配對
    emit('sys_message', {'content': '正在尋找新的配對...'})
    
    # 嘗試尋找新配對
    new_partner_id = get_wait_first_key()
    
    if new_partner_id and new_partner_id != user_id:
        # 找到新配對
        print(f"配對成功: {user_id} <-> {new_partner_id}")
        create_chat(user_id, new_partner_id)
        
        emit('sys_message', {'content': '對方已經加入聊天室'}, to=user_id)
        socketio.emit('sys_message', {'content': '對方已經加入聊天室'}, to=new_partner_id)
    else:
        # 沒人，加入等待列表
        print(f"加入等待: {user_id}")
        add_to_wait_list(user_id)

@socketio.on('disconnect')
def handle_disconnect():
    """
    當使用者斷線時觸發
    """
    user_id = request.sid
    print(f"User disconnected: {user_id}")
    
    partner_id = get_chat_partner(user_id)
    
    # 移除配對關係
    remove_chat(user_id, partner_id)
    
    # 如果原本有配對對象，通知對方
    if partner_id:
        socketio.emit('sys_message', {'content': '對方已經離開聊天室'}, to=partner_id)

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    socketio.run(app, port=port, debug=debug)
