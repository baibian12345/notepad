from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 数据库初始化
def init_db():
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    
    # 创建笔记表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建设置表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL
        )
    ''')
    
    # 创建待办事项表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            completed BOOLEAN DEFAULT FALSE,
            priority TEXT DEFAULT 'medium',
            due_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建AI对话会话表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建AI对话消息表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES chat_sessions (id)
        )
    ''')
    
    # 创建番茄钟记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pomodoro_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_name TEXT NOT NULL,
            duration INTEGER NOT NULL,
            completed BOOLEAN DEFAULT FALSE,
            session_type TEXT DEFAULT 'work',
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# 笔记相关API
@app.route('/api/notes', methods=['GET'])
def get_notes():
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM notes ORDER BY updated_at DESC')
    notes = cursor.fetchall()
    conn.close()
    
    notes_list = []
    for note in notes:
        notes_list.append({
            'id': note[0],
            'title': note[1],
            'content': note[2],
            'created_at': note[3],
            'updated_at': note[4]
        })
    
    return jsonify(notes_list)

@app.route('/api/notes', methods=['POST'])
def create_note():
    data = request.get_json()
    title = data.get('title', '未命名笔记')
    content = data.get('content', '')
    
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO notes (title, content) VALUES (?, ?)',
        (title, content)
    )
    note_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({'id': note_id, 'message': '笔记创建成功'}), 201

@app.route('/api/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM notes WHERE id = ?', (note_id,))
    note = cursor.fetchone()
    conn.close()
    
    if note:
        return jsonify({
            'id': note[0],
            'title': note[1],
            'content': note[2],
            'created_at': note[3],
            'updated_at': note[4]
        })
    else:
        return jsonify({'error': '笔记不存在'}), 404

@app.route('/api/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE notes SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        (title, content, note_id)
    )
    conn.commit()
    conn.close()
    
    return jsonify({'message': '笔记更新成功'})

@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': '笔记删除成功'})

# 设置相关API
@app.route('/api/settings', methods=['GET'])
def get_settings():
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM settings')
    settings = cursor.fetchall()
    conn.close()
    
    settings_dict = {}
    for setting in settings:
        settings_dict[setting[1]] = setting[2]
    
    return jsonify(settings_dict)

@app.route('/api/settings', methods=['POST'])
def save_setting():
    data = request.get_json()
    key = data.get('key')
    value = data.get('value')
    
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)',
        (key, value)
    )
    conn.commit()
    conn.close()
    
    return jsonify({'message': '设置保存成功'})

# AI功能相关API
@app.route('/api/ai/summarize', methods=['POST'])
def summarize_note():
    data = request.get_json()
    content = data.get('content', '')
    
    # 这里需要集成AI API，暂时返回模拟数据
    summary = f"这是对以下内容的总结：{content[:100]}..."
    
    return jsonify({'summary': summary})

@app.route('/api/ai/question', methods=['POST'])
def ask_question():
    data = request.get_json()
    question = data.get('question', '')
    context = data.get('context', '')
    
    # 这里需要集成AI API，暂时返回模拟数据
    answer = f"基于提供的内容，关于'{question}'的回答是：这是一个模拟回答。"
    
    return jsonify({'answer': answer})

# 待办事项相关API
@app.route('/api/todos', methods=['GET'])
def get_todos():
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM todos ORDER BY created_at DESC')
    todos = cursor.fetchall()
    conn.close()
    
    todos_list = []
    for todo in todos:
        todos_list.append({
            'id': todo[0],
            'title': todo[1],
            'description': todo[2],
            'completed': bool(todo[3]),
            'priority': todo[4],
            'due_date': todo[5],
            'created_at': todo[6],
            'updated_at': todo[7]
        })
    
    return jsonify(todos_list)

@app.route('/api/todos', methods=['POST'])
def create_todo():
    data = request.get_json()
    title = data.get('title', '未命名任务')
    description = data.get('description', '')
    priority = data.get('priority', 'medium')
    due_date = data.get('due_date')
    
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO todos (title, description, priority, due_date) VALUES (?, ?, ?, ?)',
        (title, description, priority, due_date)
    )
    todo_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({'id': todo_id, 'message': '待办事项创建成功'}), 201

@app.route('/api/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM todos WHERE id = ?', (todo_id,))
    todo = cursor.fetchone()
    conn.close()
    
    if todo:
        return jsonify({
            'id': todo[0],
            'title': todo[1],
            'description': todo[2],
            'completed': bool(todo[3]),
            'priority': todo[4],
            'due_date': todo[5],
            'created_at': todo[6],
            'updated_at': todo[7]
        })
    else:
        return jsonify({'error': '待办事项不存在'}), 404

@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    completed = data.get('completed')
    priority = data.get('priority')
    due_date = data.get('due_date')
    
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE todos SET title = ?, description = ?, completed = ?, priority = ?, due_date = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        (title, description, completed, priority, due_date, todo_id)
    )
    conn.commit()
    conn.close()
    
    return jsonify({'message': '待办事项更新成功'})

@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': '待办事项删除成功'})

@app.route('/api/todos/<int:todo_id>/toggle', methods=['POST'])
def toggle_todo(todo_id):
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    cursor.execute('SELECT completed FROM todos WHERE id = ?', (todo_id,))
    result = cursor.fetchone()
    
    if result:
        new_status = not bool(result[0])
        cursor.execute(
            'UPDATE todos SET completed = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (new_status, todo_id)
        )
        conn.commit()
        conn.close()
        return jsonify({'completed': new_status, 'message': '状态更新成功'})
    else:
        conn.close()
        return jsonify({'error': '待办事项不存在'}), 404

# AI对话会话管理
@app.route('/api/chat/sessions', methods=['GET'])
def get_chat_sessions():
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM chat_sessions ORDER BY updated_at DESC')
    sessions = cursor.fetchall()
    conn.close()
    
    session_list = []
    for session in sessions:
        session_list.append({
            'id': session[0],
            'title': session[1],
            'created_at': session[2],
            'updated_at': session[3]
        })
    
    return jsonify(session_list)

@app.route('/api/chat/sessions', methods=['POST'])
def create_chat_session():
    data = request.get_json()
    title = data.get('title', '新对话')
    
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO chat_sessions (title) VALUES (?)',
        (title,)
    )
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({'id': session_id, 'title': title, 'message': '对话会话创建成功'})

@app.route('/api/chat/sessions/<int:session_id>', methods=['DELETE'])
def delete_chat_session(session_id):
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    # 删除会话相关的所有消息
    cursor.execute('DELETE FROM chat_messages WHERE session_id = ?', (session_id,))
    # 删除会话
    cursor.execute('DELETE FROM chat_sessions WHERE id = ?', (session_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': '对话会话删除成功'})

# AI对话消息管理
@app.route('/api/chat/sessions/<int:session_id>/messages', methods=['GET'])
def get_chat_messages(session_id):
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM chat_messages WHERE session_id = ? ORDER BY created_at ASC',
        (session_id,)
    )
    messages = cursor.fetchall()
    conn.close()
    
    message_list = []
    for message in messages:
        message_list.append({
            'id': message[0],
            'session_id': message[1],
            'role': message[2],
            'content': message[3],
            'created_at': message[4]
        })
    
    return jsonify(message_list)

@app.route('/api/chat/sessions/<int:session_id>/messages', methods=['POST'])
def send_chat_message(session_id):
    data = request.get_json()
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({'error': '消息内容不能为空'}), 400
    
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    
    # 保存用户消息
    cursor.execute(
        'INSERT INTO chat_messages (session_id, role, content) VALUES (?, ?, ?)',
        (session_id, 'user', user_message)
    )
    
    # 模拟AI回复（实际项目中这里会调用真实的AI API）
    ai_response = f"这是对您消息 '{user_message}' 的AI回复。在实际应用中，这里会调用真实的AI服务。"
    
    # 保存AI回复
    cursor.execute(
        'INSERT INTO chat_messages (session_id, role, content) VALUES (?, ?, ?)',
        (session_id, 'assistant', ai_response)
    )
    
    # 更新会话的最后更新时间
    cursor.execute(
        'UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        (session_id,)
    )
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'user_message': user_message,
        'ai_response': ai_response,
        'message': '消息发送成功'
    })

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)