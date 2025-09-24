<template>
  <div class="pomodoro-page">
    <div class="main-layout">
      <!-- 左侧导航 -->
      <div class="left-sidebar">
        <div class="nav-buttons">
          <router-link to="/" class="btn btn-primary">📝 笔记</router-link>
          <router-link to="/todos" class="btn btn-secondary">✅ 待办</router-link>
          <router-link to="/projects" class="btn btn-secondary">📊 项目</router-link>
          <router-link to="/chat" class="btn btn-secondary">🤖 AI对话</router-link>
          <router-link to="/pomodoro" class="btn btn-primary">🍅 番茄钟</router-link>
          <router-link to="/settings" class="btn btn-secondary">⚙️ 设置</router-link>
        </div>
      </div>

      <!-- 中间内容区域 -->
      <div class="center-content">
        <div class="pomodoro-container">
          <h1>🍅 番茄钟</h1>
          
          <!-- 计时器显示 -->
          <div class="timer-display">
            <div class="timer-circle" :class="{ 'active': isRunning, 'break': isBreakTime }">
              <div class="timer-text">
                <div class="time">{{ formatTime(currentTime) }}</div>
                <div class="session-type">{{ sessionTypeText }}</div>
              </div>
            </div>
          </div>

          <!-- 任务输入 -->
          <div class="task-input" v-if="!isRunning">
            <input 
              v-model="currentTask" 
              type="text" 
              placeholder="输入当前任务名称..."
              class="task-name-input"
              @keyup.enter="startTimer"
            >
          </div>

          <!-- 当前任务显示 -->
          <div class="current-task" v-if="isRunning && currentTask">
            <h3>当前任务: {{ currentTask }}</h3>
          </div>

          <!-- 控制按钮 -->
          <div class="timer-controls">
            <button 
              v-if="!isRunning" 
              @click="startTimer" 
              class="btn btn-primary timer-btn"
              :disabled="!currentTask.trim()"
            >
              开始
            </button>
            <button 
              v-if="isRunning" 
              @click="pauseTimer" 
              class="btn btn-secondary timer-btn"
            >
              {{ isPaused ? '继续' : '暂停' }}
            </button>
            <button 
              v-if="isRunning" 
              @click="stopTimer" 
              class="btn btn-danger timer-btn"
            >
              停止
            </button>
          </div>

          <!-- 设置区域 -->
          <div class="timer-settings" v-if="!isRunning">
            <div class="setting-item">
              <label>工作时长 (分钟):</label>
              <input v-model.number="workDuration" type="number" min="1" max="60" class="duration-input">
            </div>
            <div class="setting-item">
              <label>短休息 (分钟):</label>
              <input v-model.number="shortBreakDuration" type="number" min="1" max="30" class="duration-input">
            </div>
            <div class="setting-item">
              <label>长休息 (分钟):</label>
              <input v-model.number="longBreakDuration" type="number" min="1" max="60" class="duration-input">
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧统计 -->
      <div class="right-sidebar">
        <div class="stats-container">
          <h3>📊 今日统计</h3>
          <div class="stat-item">
            <span class="stat-label">完成番茄:</span>
            <span class="stat-value">{{ todayStats.completed }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">专注时间:</span>
            <span class="stat-value">{{ formatDuration(todayStats.focusTime) }}</span>
          </div>
          
          <h3>📈 历史记录</h3>
          <div class="session-history">
            <div 
              v-for="session in recentSessions" 
              :key="session.id"
              class="session-item"
              :class="{ 'completed': session.completed }"
            >
              <div class="session-task">{{ session.task_name }}</div>
              <div class="session-time">{{ formatSessionTime(session.start_time) }}</div>
              <div class="session-duration">{{ session.duration }}分钟</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PomodoroPage',
  data() {
    return {
      // 计时器状态
      isRunning: false,
      isPaused: false,
      currentTime: 0, // 秒
      timer: null,
      
      // 会话设置
      workDuration: 25, // 分钟
      shortBreakDuration: 5,
      longBreakDuration: 15,
      
      // 当前会话
      currentTask: '',
      sessionType: 'work', // 'work', 'short_break', 'long_break'
      sessionCount: 0,
      currentSessionId: null,
      
      // 统计数据
      todayStats: {
        completed: 0,
        focusTime: 0
      },
      recentSessions: []
    }
  },
  computed: {
    isBreakTime() {
      return this.sessionType !== 'work'
    },
    sessionTypeText() {
      switch(this.sessionType) {
        case 'work': return '专注时间'
        case 'short_break': return '短休息'
        case 'long_break': return '长休息'
        default: return '专注时间'
      }
    }
  },
  mounted() {
    this.loadStats()
    this.loadRecentSessions()
  },
  beforeUnmount() {
    if (this.timer) {
      clearInterval(this.timer)
    }
  },
  methods: {
    startTimer() {
      if (!this.currentTask.trim() && this.sessionType === 'work') {
        alert('请输入任务名称')
        return
      }
      
      this.isRunning = true
      this.isPaused = false
      
      // 设置初始时间
      if (this.currentTime === 0) {
        switch(this.sessionType) {
          case 'work':
            this.currentTime = this.workDuration * 60
            break
          case 'short_break':
            this.currentTime = this.shortBreakDuration * 60
            break
          case 'long_break':
            this.currentTime = this.longBreakDuration * 60
            break
        }
      }
      
      // 创建会话记录
      this.createSession()
      
      // 开始计时
      this.timer = setInterval(() => {
        if (!this.isPaused) {
          this.currentTime--
          if (this.currentTime <= 0) {
            this.completeSession()
          }
        }
      }, 1000)
    },
    
    pauseTimer() {
      this.isPaused = !this.isPaused
    },
    
    stopTimer() {
      this.isRunning = false
      this.isPaused = false
      clearInterval(this.timer)
      this.timer = null
      this.currentTime = 0
      
      // 如果有当前会话，标记为未完成
      if (this.currentSessionId) {
        this.deleteSession(this.currentSessionId)
        this.currentSessionId = null
      }
    },
    
    completeSession() {
      this.isRunning = false
      this.isPaused = false
      clearInterval(this.timer)
      this.timer = null
      
      // 完成当前会话
      if (this.currentSessionId) {
        this.finishSession(this.currentSessionId)
      }
      
      // 播放提示音（如果浏览器支持）
      this.playNotificationSound()
      
      // 显示完成提示
      if (this.sessionType === 'work') {
        this.sessionCount++
        alert(`🎉 专注时间完成！已完成 ${this.sessionCount} 个番茄钟`)
        
        // 决定下一个会话类型
        if (this.sessionCount % 4 === 0) {
          this.sessionType = 'long_break'
          this.currentTask = ''
        } else {
          this.sessionType = 'short_break'
          this.currentTask = ''
        }
      } else {
        alert('😊 休息时间结束！准备开始下一个专注时间')
        this.sessionType = 'work'
      }
      
      this.currentTime = 0
      this.currentSessionId = null
      
      // 刷新统计数据
      this.loadStats()
      this.loadRecentSessions()
    },
    
    async createSession() {
      try {
        const response = await fetch('http://127.0.0.1:5000/api/pomodoro/sessions', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            task_name: this.currentTask || this.sessionTypeText,
            duration: this.sessionType === 'work' ? this.workDuration : 
                     this.sessionType === 'short_break' ? this.shortBreakDuration : this.longBreakDuration,
            session_type: this.sessionType
          })
        })
        
        if (response.ok) {
          const data = await response.json()
          this.currentSessionId = data.session.id
        }
      } catch (error) {
        console.error('创建会话失败:', error)
      }
    },
    
    async finishSession(sessionId) {
      try {
        await fetch(`http://127.0.0.1:5000/api/pomodoro/sessions/${sessionId}/complete`, {
          method: 'PUT'
        })
      } catch (error) {
        console.error('完成会话失败:', error)
      }
    },
    
    async deleteSession(sessionId) {
      try {
        await fetch(`http://127.0.0.1:5000/api/pomodoro/sessions/${sessionId}`, {
          method: 'DELETE'
        })
      } catch (error) {
        console.error('删除会话失败:', error)
      }
    },
    
    async loadStats() {
      try {
        const response = await fetch('http://127.0.0.1:5000/api/pomodoro/stats')
        if (response.ok) {
          const data = await response.json()
          this.todayStats = data.today
        }
      } catch (error) {
        console.error('加载统计数据失败:', error)
      }
    },
    
    async loadRecentSessions() {
      try {
        const response = await fetch('http://127.0.0.1:5000/api/pomodoro/sessions')
        if (response.ok) {
          const data = await response.json()
          this.recentSessions = data.sessions.slice(0, 10) // 显示最近10个
        }
      } catch (error) {
        console.error('加载历史记录失败:', error)
      }
    },
    
    formatTime(seconds) {
      const mins = Math.floor(seconds / 60)
      const secs = seconds % 60
      return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    },
    
    formatDuration(minutes) {
      const hours = Math.floor(minutes / 60)
      const mins = minutes % 60
      if (hours > 0) {
        return `${hours}小时${mins}分钟`
      }
      return `${mins}分钟`
    },
    
    formatSessionTime(timestamp) {
      const date = new Date(timestamp)
      return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    },
    
    playNotificationSound() {
      // 简单的提示音实现
      try {
        const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLZiTYIG2m98OScTgwOUarm7blmGgU7k9n1unEiBC13yO/eizEIHWq+8+OWT')
        audio.play().catch(() => {})
      } catch (error) {
        // 忽略音频播放错误
      }
    }
  }
}
</script>

<style scoped>
.pomodoro-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.main-layout {
  display: flex;
  min-height: 100vh;
}

.left-sidebar {
  width: 200px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-right: 1px solid rgba(255, 255, 255, 0.2);
}

.center-content {
  flex: 1;
  padding: 40px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.right-sidebar {
  width: 300px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-left: 1px solid rgba(255, 255, 255, 0.2);
}

.pomodoro-container {
  text-align: center;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  max-width: 500px;
  width: 100%;
}

.pomodoro-container h1 {
  color: white;
  margin-bottom: 30px;
  font-size: 2.5em;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.timer-display {
  margin: 40px 0;
}

.timer-circle {
  width: 250px;
  height: 250px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  border: 8px solid rgba(255, 255, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  transition: all 0.3s ease;
}

.timer-circle.active {
  border-color: #ff6b6b;
  box-shadow: 0 0 30px rgba(255, 107, 107, 0.5);
  animation: pulse 2s infinite;
}

.timer-circle.break {
  border-color: #4ecdc4;
  box-shadow: 0 0 30px rgba(78, 205, 196, 0.5);
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

.timer-text {
  text-align: center;
  color: white;
}

.time {
  font-size: 3em;
  font-weight: bold;
  margin-bottom: 10px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.session-type {
  font-size: 1.2em;
  opacity: 0.8;
}

.task-input {
  margin: 20px 0;
}

.task-name-input {
  width: 100%;
  max-width: 300px;
  padding: 12px 16px;
  border: none;
  border-radius: 25px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  font-size: 16px;
  text-align: center;
  backdrop-filter: blur(10px);
}

.task-name-input::placeholder {
  color: rgba(255, 255, 255, 0.7);
}

.current-task {
  margin: 20px 0;
  color: white;
}

.current-task h3 {
  font-size: 1.3em;
  margin: 0;
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  display: inline-block;
}

.timer-controls {
  margin: 30px 0;
}

.timer-btn {
  margin: 0 10px;
  padding: 12px 30px;
  font-size: 18px;
  border-radius: 25px;
  min-width: 100px;
}

.timer-settings {
  margin-top: 30px;
  text-align: left;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 15px 0;
  color: white;
}

.setting-item label {
  font-size: 14px;
}

.duration-input {
  width: 60px;
  padding: 5px 8px;
  border: none;
  border-radius: 5px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  text-align: center;
}

.stats-container {
  color: white;
}

.stats-container h3 {
  margin-bottom: 20px;
  font-size: 1.3em;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.stat-item {
  display: flex;
  justify-content: space-between;
  margin: 15px 0;
  padding: 10px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}

.stat-label {
  opacity: 0.8;
}

.stat-value {
  font-weight: bold;
  color: #ffd93d;
}

.session-history {
  max-height: 400px;
  overflow-y: auto;
}

.session-item {
  padding: 12px;
  margin: 8px 0;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  border-left: 4px solid #ff6b6b;
}

.session-item.completed {
  border-left-color: #4ecdc4;
}

.session-task {
  font-weight: bold;
  margin-bottom: 5px;
}

.session-time {
  font-size: 0.9em;
  opacity: 0.7;
}

.session-duration {
  font-size: 0.9em;
  color: #ffd93d;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .main-layout {
    flex-direction: column;
  }
  
  .left-sidebar,
  .right-sidebar {
    width: 100%;
  }
  
  .center-content {
    padding: 20px;
  }
}

@media (max-width: 768px) {
  .timer-circle {
    width: 200px;
    height: 200px;
  }
  
  .time {
    font-size: 2.5em;
  }
  
  .pomodoro-container {
    padding: 20px;
  }
}
</style>