<template>
  <div class="chat-page">
    <!-- 顶部导航 -->
    <div class="top-nav">
      <div class="nav-content">
        <h1 class="app-title">🤖 AI对话助手</h1>
        <div class="nav-buttons">
          <router-link to="/" class="btn btn-secondary">📝 笔记</router-link>
          <router-link to="/todos" class="btn btn-secondary">✅ 待办</router-link>
          <router-link to="/projects" class="btn btn-secondary">📊 项目</router-link>
          <router-link to="/settings" class="btn btn-secondary">⚙️ 设置</router-link>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-layout">
      <!-- 会话列表面板 -->
      <div class="session-list-panel glass-panel">
        <div class="panel-header">
          <h3>💬 对话会话</h3>
          <button @click="createNewSession" class="btn btn-primary">新建对话</button>
        </div>
        
        <div class="session-list">
          <div 
            v-for="session in sessions" 
            :key="session.id"
            :class="['session-item', { active: currentSessionId === session.id }]"
            @click="selectSession(session.id)"
          >
            <div class="session-info">
              <div class="session-title">{{ session.title }}</div>
              <div class="session-time">{{ formatTime(session.updated_at || session.created_at) }}</div>
            </div>
            <button 
              @click.stop="confirmDeleteSession(session)" 
              class="btn btn-danger session-delete"
              title="删除会话"
            >
              🗑️
            </button>
          </div>
        </div>
      </div>

      <!-- 聊天面板 -->
      <div class="chat-panel glass-panel">
        <div v-if="!currentSessionId" class="no-session">
          <div class="welcome-message">
            <h2>🌟 欢迎使用AI对话助手</h2>
            <p>选择一个会话开始对话，或创建新的会话</p>
          </div>
        </div>
        
        <div v-else class="chat-container">
          <!-- 消息列表 -->
          <div class="messages-container" ref="messagesContainer">
            <div 
              v-for="(message, index) in currentMessages" 
              :key="index"
              :class="['message', message.role]"
            >
              <div class="message-avatar">
                {{ message.role === 'user' ? '👤' : '🤖' }}
              </div>
              <div class="message-content">
                <div class="message-text" v-html="formatMessageContent(message.content)"></div>
                <div class="message-time">{{ formatTime(message.timestamp) }}</div>
              </div>
            </div>
            
            <!-- 流式响应中的消息 -->
            <div v-if="streamingMessage" class="message assistant">
              <div class="message-avatar">🤖</div>
              <div class="message-content">
                <div class="message-text" v-html="formatMessageContent(streamingMessage)"></div>
                <div class="message-time">{{ formatTime(Date.now()) }}</div>
              </div>
            </div>
          </div>

          <!-- 输入区域 -->
          <div class="input-area">
            <div class="input-container">
              <textarea 
                v-model="newMessage"
                @keydown.enter.prevent="sendMessage"
                placeholder="输入您的消息..."
                class="message-input"
                rows="3"
                :disabled="isStreaming"
              ></textarea>
              <button 
                v-if="!isStreaming"
                @click="sendMessage" 
                :disabled="!newMessage.trim()"
                class="btn btn-primary send-btn"
              >
                发送
              </button>
              <button 
                v-else
                @click="stopStreaming" 
                class="btn btn-danger send-btn"
              >
                停止生成
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 删除确认对话框 -->
    <div v-if="deleteConfirm.show" class="modal-overlay" @click="cancelDelete">
      <div class="modal-container" @click.stop>
        <div class="modal-header">
          <h3>确认删除</h3>
        </div>
        <div class="modal-body">
          <p>确定要删除会话「{{ deleteConfirm.session?.title || '无标题' }}」吗？</p>
          <p class="warning-text">此操作不可撤销！</p>
        </div>
        <div class="modal-footer">
          <button @click="cancelDelete" class="btn btn-secondary">取消</button>
          <button @click="deleteSession" class="btn btn-danger">删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { v4 as uuidv4 } from 'uuid';

export default {
  name: 'AIChatPage',
  data() {
    return {
      sessions: [],
      currentSessionId: null,
      newMessage: '',
      isStreaming: false,
      streamingMessage: '',
      abortController: null,
      deleteConfirm: {
        show: false,
        session: null
      }
    }
  },
  computed: {
    currentMessages() {
      if (!this.currentSessionId) return [];
      const session = this.sessions.find(s => s.id === this.currentSessionId);
      return session ? session.messages : [];
    }
  },
  mounted() {
    this.loadSessionsFromLocalStorage();
    
    // 如果有会话，自动选择第一个
    if (this.sessions.length > 0 && !this.currentSessionId) {
      this.selectSession(this.sessions[0].id);
    }
  },
  methods: {
    loadSessionsFromLocalStorage() {
      const savedSessions = localStorage.getItem('chat-sessions');
      if (savedSessions) {
        try {
          this.sessions = JSON.parse(savedSessions);
        } catch (error) {
          console.error('解析本地存储的会话数据失败:', error);
          this.sessions = [];
        }
      }
    },
    
    saveSessionsToLocalStorage() {
      localStorage.setItem('chat-sessions', JSON.stringify(this.sessions));
    },
    
    createNewSession() {
      const newSession = {
        id: uuidv4(),
        title: `对话 ${new Date().toLocaleString('zh-CN', {month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'})}`,
        created_at: Date.now(),
        updated_at: Date.now(),
        messages: []
      };
      
      this.sessions.unshift(newSession);
      this.saveSessionsToLocalStorage();
      this.selectSession(newSession.id);
    },
    
    selectSession(sessionId) {
      this.currentSessionId = sessionId;
      this.$nextTick(() => {
        this.scrollToBottom();
      });
    },
    
    async sendMessage() {
      if (!this.newMessage.trim() || this.isStreaming) return;
      
      const userMessage = this.newMessage.trim();
      this.newMessage = '';
      
      // 找到当前会话
      const sessionIndex = this.sessions.findIndex(s => s.id === this.currentSessionId);
      if (sessionIndex === -1) return;
      
      // 添加用户消息
      const userMessageObj = {
        role: 'user',
        content: userMessage,
        timestamp: Date.now()
      };
      
      this.sessions[sessionIndex].messages.push(userMessageObj);
      this.sessions[sessionIndex].updated_at = Date.now();
      this.saveSessionsToLocalStorage();
      
      this.$nextTick(() => {
        this.scrollToBottom();
      });
      
      // 开始流式响应
      this.isStreaming = true;
      this.streamingMessage = '';
      this.abortController = new AbortController();
      
      try {
        // 模拟AI响应（实际项目中这里会调用真实的AI API）
        await this.simulateStreamingResponse(userMessage);
        
        // 响应完成后，保存AI消息
        const aiMessageObj = {
          role: 'assistant',
          content: this.streamingMessage,
          timestamp: Date.now()
        };
        
        this.sessions[sessionIndex].messages.push(aiMessageObj);
        this.sessions[sessionIndex].updated_at = Date.now();
        this.saveSessionsToLocalStorage();
        
      } catch (error) {
        if (error.name !== 'AbortError') {
          console.error('AI响应出错:', error);
        }
      } finally {
        this.isStreaming = false;
        this.streamingMessage = '';
        this.abortController = null;
      }
    },
    
    async simulateStreamingResponse(userMessage) {
      // 这是一个模拟流式响应的函数
      // 在实际项目中，这里应该调用后端API，获取流式响应
      
      const responses = [
        "我正在思考您的问题...",
        "根据您的提问 '",
        userMessage,
        "'，我的回答是：\n\n",
        "这是一个模拟的AI响应，在实际项目中，这里会返回真实的AI回答。\n\n",
        "您可以通过调用OpenRouter API或其他AI服务来获取真实的回答。\n\n",
        "```javascript\n// 这是一个代码示例\nfunction hello() {\n  console.log('Hello, world!');\n}\n```\n\n",
        "希望这个示例能帮助您理解流式响应的效果。"
      ];
      
      for (const part of responses) {
        if (this.abortController && this.abortController.signal.aborted) {
          throw new DOMException('Stream was aborted', 'AbortError');
        }
        
        this.streamingMessage += part;
        this.$nextTick(() => {
          this.scrollToBottom();
        });
        
        // 模拟网络延迟
        await new Promise(resolve => setTimeout(resolve, 300 + Math.random() * 700));
      }
    },
    
    stopStreaming() {
      if (this.abortController) {
        this.abortController.abort();
      }
    },
    
    confirmDeleteSession(session) {
      this.deleteConfirm = {
        show: true,
        session: session
      };
    },
    
    deleteSession() {
      if (!this.deleteConfirm.session) return;
      
      const sessionId = this.deleteConfirm.session.id;
      const sessionIndex = this.sessions.findIndex(s => s.id === sessionId);
      
      if (sessionIndex !== -1) {
        this.sessions.splice(sessionIndex, 1);
        this.saveSessionsToLocalStorage();
        
        if (this.currentSessionId === sessionId) {
          this.currentSessionId = this.sessions.length > 0 ? this.sessions[0].id : null;
        }
      }
      
      this.cancelDelete();
    },
    
    cancelDelete() {
      this.deleteConfirm = {
        show: false,
        session: null
      };
    },
    
    scrollToBottom() {
      const container = this.$refs.messagesContainer;
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    },
    
    formatTime(timestamp) {
      return new Date(timestamp).toLocaleString('zh-CN', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    
    formatMessageContent(content) {
      // 使用marked将Markdown转换为HTML，并使用DOMPurify清理HTML
      return DOMPurify.sanitize(marked(content));
    }
  }
}
</script>

<style scoped>
@keyframes moveHorizontal {
  0% {
    transform: translateX(-50%) translateY(-10%);
  }
  50% {
    transform: translateX(50%) translateY(10%);
  }
  100% {
    transform: translateX(-50%) translateY(-10%);
  }
}

@keyframes moveInCircle {
  0% {
    transform: rotate(0deg);
  }
  50% {
    transform: rotate(180deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@keyframes moveVertical {
  0% {
    transform: translateY(-50%);
  }
  50% {
    transform: translateY(50%);
  }
  100% {
    transform: translateY(-50%);
  }
}

@keyframes floatCats {
  0% {
    transform: translateY(0) rotate(0deg);
    opacity: 0.8;
  }
  50% {
    transform: translateY(-15px) rotate(5deg);
    opacity: 1;
  }
  100% {
    transform: translateY(0) rotate(0deg);
    opacity: 0.8;
  }
}

.chat-page {
  height: 100vh;
  background-color: #1a1c23;
  position: relative;
  overflow: hidden;
}

.chat-page::before {
  content: '';
  position: absolute;
  width: 100%;
  height: 100%;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100' viewBox='0 0 100 100'%3E%3Cpath d='M50 30c-5.5 0-10 4.5-10 10s4.5 10 10 10 10-4.5 10-10-4.5-10-10-10zm0 18c-4.4 0-8-3.6-8-8s3.6-8 8-8 8 3.6 8 8-3.6 8-8 8zm0-44c-5.5 0-10 4.5-10 10s4.5 10 10 10 10-4.5 10-10-4.5-10-10-10zm0 18c-4.4 0-8-3.6-8-8s3.6-8 8-8 8 3.6 8 8-3.6 8-8 8zm0 26c-5.5 0-10 4.5-10 10s4.5 10 10 10 10-4.5 10-10-4.5-10-10-10zm0 18c-4.4 0-8-3.6-8-8s3.6-8 8-8 8 3.6 8 8-3.6 8-8 8z' fill='%23ffffff' fill-opacity='0.03'/%3E%3C/svg%3E");
  opacity: 0.5;
}

.main-layout::before {
  content: '';
  position: absolute;
  width: 300px;
  height: 300px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Cpath d='M30,50 C30,40 35,30 50,30 C65,30 70,40 70,50 C70,60 65,70 50,70 C35,70 30,60 30,50 Z M40,45 C40,42 42,40 45,40 C48,40 50,42 50,45 C50,48 48,50 45,50 C42,50 40,48 40,45 Z M50,55 C50,52 52,50 55,50 C58,50 60,52 60,55 C60,58 58,60 55,60 C52,60 50,58 50,55 Z' fill='%23ff9580' fill-opacity='0.2'/%3E%3C/svg%3E");
  top: 10%;
  left: 5%;
  animation: floatCats 8s ease-in-out infinite;
  z-index: 0;
}

.main-layout::after {
  content: '';
  position: absolute;
  width: 250px;
  height: 250px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Cpath d='M30,50 C30,40 35,30 50,30 C65,30 70,40 70,50 C70,60 65,70 50,70 C35,70 30,60 30,50 Z M40,45 C40,42 42,40 45,40 C48,40 50,42 50,45 C50,48 48,50 45,50 C42,50 40,48 40,45 Z M50,55 C50,52 52,50 55,50 C58,50 60,52 60,55 C60,58 58,60 55,60 C52,60 50,58 50,55 Z' fill='%2380b3ff' fill-opacity='0.2'/%3E%3C/svg%3E");
  bottom: 10%;
  right: 5%;
  animation: floatCats 10s ease-in-out infinite;
  z-index: 0;
}

.top-nav {
  position: relative;
  z-index: 10;
  padding: 1rem;
  display: flex;
  justify-content: center;
}

.nav-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  max-width: 1200px;
}

.app-title {
  font-size: 1.5rem;
  color: #fff;
  margin: 0;
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
}

.nav-buttons {
  display: flex;
  gap: 0.5rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-primary {
  background-color: #7c3aed;
  color: #fff;
}

.btn-primary:hover {
  background-color: #6d28d9;
}

.btn-secondary {
  background-color: rgba(255, 255, 255, 0.1);
  color: #fff;
  text-decoration: none;
}

.btn-secondary:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.btn-danger {
  background-color: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.btn-danger:hover {
  background-color: rgba(239, 68, 68, 0.3);
}

.main-layout {
  display: flex;
  gap: 1rem;
  padding: 0 1rem 1rem;
  height: calc(100vh - 80px);
  position: relative;
  z-index: 1;
}

.glass-panel {
  background-color: rgba(30, 41, 59, 0.7);
  backdrop-filter: blur(10px);
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 左侧面板样式 */
.left-panel {
  width: 300px;
  flex-shrink: 0;
}

.panel-tabs {
  display: flex;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.tab-btn {
  flex: 1;
  padding: 1rem;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.tab-btn.active {
  color: #fff;
  border-bottom: 2px solid #7c3aed;
}

.tab-btn:hover:not(.active) {
  color: #fff;
  background-color: rgba(255, 255, 255, 0.05);
}

.panel-header {
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.panel-header h3 {
  margin: 0;
  color: #fff;
  font-size: 1rem;
}

/* 会话列表样式 */
.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.session-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem;
  border-radius: 0.5rem;
  margin-bottom: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  background-color: rgba(255, 255, 255, 0.05);
}

.session-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.session-item.active {
  background-color: rgba(124, 58, 237, 0.2);
  border-left: 3px solid #7c3aed;
}

.session-info {
  flex: 1;
  overflow: hidden;
}

.session-title {
  color: #fff;
  font-weight: 500;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-time {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.75rem;
}

.session-delete {
  padding: 0.25rem;
  font-size: 0.875rem;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.session-item:hover .session-delete {
  opacity: 1;
}

/* 项目管理面板样式 */
.project-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.add-task-form {
  padding: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.task-input {
  width: 100%;
  padding: 0.75rem;
  background-color: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 0.5rem;
  color: #fff;
  margin-bottom: 0.5rem;
}

.task-form-row {
  display: flex;
  gap: 0.5rem;
}

.task-priority-select {
  flex: 1;
  padding: 0.5rem;
  background-color: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 0.5rem;
  color: #fff;
}

.add-task-btn {
  padding: 0.5rem 1rem;
}

.task-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.empty-tasks {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: rgba(255, 255, 255, 0.5);
}

.task-item {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  border-radius: 0.5rem;
  margin-bottom: 0.5rem;
  background-color: rgba(255, 255, 255, 0.05);
  transition: all 0.2s ease;
}

.task-item.completed {
  opacity: 0.6;
}

.task-item.completed .task-title {
  text-decoration: line-through;
  color: rgba(255, 255, 255, 0.5);
}

.task-checkbox {
  margin-right: 0.75rem;
}

.task-content {
  flex: 1;
}

.task-title {
  color: #fff;
  margin-bottom: 0.25rem;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
}

.task-priority {
  font-size: 0.875rem;
}

.task-priority.high {
  color: #ef4444;
}

.task-priority.medium {
  color: #f59e0b;
}

.task-priority.low {
  color: #10b981;
}

.task-date {
  font-size: 0.75rem;
}

.task-actions {
  opacity: 0;
  transition: opacity 0.2s ease;
}

.task-item:hover .task-actions {
  opacity: 1;
}

.task-delete-btn {
  padding: 0.25rem;
  font-size: 0.875rem;
}

/* 聊天面板样式 */
.chat-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.no-session {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}

.welcome-message {
  text-align: center;
  color: #fff;
}

.welcome-message h2 {
  margin-bottom: 1rem;
  font-size: 1.5rem;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.message {
  display: flex;
  margin-bottom: 1.5rem;
}

.message-avatar {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 1.25rem;
  margin-right: 1rem;
  flex-shrink: 0;
}

.message-content {
  flex: 1;
}

.message-text {
  padding: 1rem;
  border-radius: 0.5rem;
  color: #fff;
  margin-bottom: 0.5rem;
  line-height: 1.5;
}

.message.user .message-text {
  background-color: rgba(124, 58, 237, 0.3);
}

.message.assistant .message-text {
  background-color: rgba(255, 255, 255, 0.1);
}

.message-time {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
  text-align: right;
}

.input-area {
  padding: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.input-container {
  display: flex;
  gap: 0.5rem;
}

.message-input {
  flex: 1;
  padding: 0.75rem;
  background-color: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 0.5rem;
  color: #fff;
  resize: none;
}

.send-btn {
  align-self: flex-end;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 100;
}

.modal-container {
  background-color: #1e293b;
  border-radius: 0.5rem;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 10px 15px rgba(0, 0, 0, 0.3);
}

.modal-header {
  padding: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-header h3 {
  margin: 0;
  color: #fff;
}

.modal-body {
  padding: 1rem;
  color: #fff;
}

.warning-text {
  color: #ef4444;
  font-weight: 500;
}

.modal-footer {
  padding: 1rem;
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-layout {
    flex-direction: column;
  }
  
  .left-panel {
    width: 100%;
    height: 300px;
  }
  
  .nav-content {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .nav-buttons {
    width: 100%;
    justify-content: center;
  }
}
</style>