<template>
  <div class="todo-page">
    <!-- 顶部导航 -->
    <div class="top-nav">
      <h1 class="page-title">📝 <span class="gradient-text">AI智能项目管理</span></h1>
      <div class="nav-buttons">
        <router-link to="/" class="nav-btn">
          <span class="icon">📔</span>
          笔记
        </router-link>
        <router-link to="/chat" class="nav-btn">
          <span class="icon">🤖</span>
          AI对话
        </router-link>
        <router-link to="/projects" class="nav-btn">
          <span class="icon">📊</span>
          项目
        </router-link>
        <router-link to="/pomodoro" class="nav-btn">
          <span class="icon">🍅</span>
          番茄钟
        </router-link>
        <router-link to="/settings" class="nav-btn">
          <span class="icon">⚙️</span>
          设置
        </router-link>
      </div>
    </div>

    <div class="todo-container">
      <!-- 左侧：添加新任务 -->
      <div class="add-todo-section">
        <div class="glass-panel ai-panel">
          <div class="panel-header">
            <div class="ai-icon">✨</div>
            <h3>AI智能任务创建</h3>
          </div>
          <form @submit.prevent="addTodo" class="add-form">
            <div class="input-wrapper">
              <input
                v-model="newTodo.title"
                type="text"
                placeholder="任务标题..."
                class="input-field"
                required
              />
              <div class="ai-suggestion" v-if="newTodo.title.length > 3">
                <div class="suggestion-chip">添加截止日期 📅</div>
                <div class="suggestion-chip">设为高优先级 🔴</div>
                <div class="suggestion-chip">分解为子任务 📋</div>
              </div>
            </div>
            <textarea
              v-model="newTodo.description"
              placeholder="任务描述（可选）..."
              class="textarea-field"
              rows="3"
            ></textarea>
            <div class="form-row">
              <select v-model="newTodo.priority" class="select-field">
                <option value="low">🟢 低优先级</option>
                <option value="medium">🟡 中优先级</option>
                <option value="high">🔴 高优先级</option>
              </select>
              <input
                v-model="newTodo.due_date"
                type="date"
                class="date-field"
              />
            </div>
            <button type="submit" class="add-btn">
              <span class="btn-icon">➕</span>
              <span class="btn-text">添加任务</span>
              <span class="btn-effect"></span>
            </button>
          </form>
        </div>

        <!-- 统计信息 -->
        <div class="glass-panel stats-panel ai-panel">
          <div class="panel-header">
            <div class="ai-icon">📊</div>
            <h3>智能数据分析</h3>
          </div>
          <div class="stats">
            <div class="stat-item">
              <div class="stat-circle">
                <span class="stat-number">{{ totalTodos }}</span>
              </div>
              <span class="stat-label">总任务</span>
            </div>
            <div class="stat-item">
              <div class="stat-circle completed">
                <span class="stat-number">{{ completedTodos }}</span>
              </div>
              <span class="stat-label">已完成</span>
            </div>
            <div class="stat-item">
              <div class="stat-circle pending">
                <span class="stat-number">{{ pendingTodos }}</span>
              </div>
              <span class="stat-label">待完成</span>
            </div>
          </div>
          <div class="progress-container">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
            </div>
            <p class="progress-text">完成进度: {{ progressPercentage }}%</p>
          </div>
          
          <div class="ai-insights" v-if="totalTodos > 0">
            <div class="insight-header">
              <div class="ai-icon small">💡</div>
              <h4>AI洞察</h4>
            </div>
            <div class="insight-content">
              <p v-if="completedTodos === 0">您尚未完成任何任务，建议从优先级最高的任务开始。</p>
              <p v-else-if="progressPercentage < 30">您的进度较慢，建议专注于完成几个重要任务。</p>
              <p v-else-if="progressPercentage < 70">保持良好节奏，您已经完成了一半以上的任务！</p>
              <p v-else>太棒了！您即将完成所有任务，继续保持！</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：任务列表 -->
      <div class="todo-list-section">
        <div class="glass-panel ai-panel">
          <div class="panel-header">
            <div class="ai-icon">📋</div>
            <h3>智能任务列表</h3>
            <div class="filter-buttons">
              <button
                @click="filterStatus = 'all'"
                :class="{ active: filterStatus === 'all' }"
                class="filter-btn"
              >
                全部
              </button>
              <button
                @click="filterStatus = 'pending'"
                :class="{ active: filterStatus === 'pending' }"
                class="filter-btn"
              >
                待完成
              </button>
              <button
                @click="filterStatus = 'completed'"
                :class="{ active: filterStatus === 'completed' }"
                class="filter-btn"
              >
                已完成
              </button>
            </div>
          </div>

          <div class="todo-list" v-if="filteredTodos.length > 0">
            <div
              v-for="todo in filteredTodos"
              :key="todo.id"
              :class="['todo-item', { completed: todo.completed, editing: editingId === todo.id }]"
            >
              <div class="todo-content" v-if="editingId !== todo.id">
                <div class="todo-main">
                  <div class="checkbox-wrapper">
                    <input
                      type="checkbox"
                      :checked="todo.completed"
                      @change="toggleTodo(todo.id)"
                      class="todo-checkbox"
                    />
                    <span class="checkmark"></span>
                  </div>
                  <div class="todo-info">
                    <h4 class="todo-title" :class="{ completed: todo.completed }">
                      {{ todo.title }}
                    </h4>
                    <p class="todo-description" v-if="todo.description">
                      {{ todo.description }}
                    </p>
                    <div class="todo-meta">
                      <span class="priority" :class="todo.priority">
                        {{ getPriorityIcon(todo.priority) }} {{ getPriorityText(todo.priority) }}
                      </span>
                      <span class="due-date" v-if="todo.due_date">
                        📅 {{ formatDate(todo.due_date) }}
                      </span>
                    </div>
                  </div>
                </div>
                <div class="todo-actions">
                  <button @click="startEdit(todo)" class="action-btn edit-btn">
                    ✏️
                  </button>
                  <button @click="deleteTodo(todo.id)" class="action-btn delete-btn">
                    🗑️
                  </button>
                </div>
              </div>

              <!-- 编辑模式 -->
              <div class="edit-form" v-else>
                <input
                  v-model="editForm.title"
                  type="text"
                  class="input-field"
                  @keyup.enter="saveEdit"
                  @keyup.esc="cancelEdit"
                />
                <textarea
                  v-model="editForm.description"
                  class="textarea-field"
                  rows="2"
                ></textarea>
                <div class="form-row">
                  <select v-model="editForm.priority" class="select-field">
                    <option value="low">🟢 低优先级</option>
                    <option value="medium">🟡 中优先级</option>
                    <option value="high">🔴 高优先级</option>
                  </select>
                  <input
                    v-model="editForm.due_date"
                    type="date"
                    class="date-field"
                  />
                </div>
                <div class="edit-actions">
                  <button @click="saveEdit" class="save-btn">
                    <span class="btn-icon">💾</span>
                    <span class="btn-text">保存</span>
                    <span class="btn-effect"></span>
                  </button>
                  <button @click="cancelEdit" class="cancel-btn">
                    <span class="btn-icon">❌</span>
                    <span class="btn-text">取消</span>
                    <span class="btn-effect"></span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div class="empty-state" v-else>
            <div class="empty-icon">🤖</div>
            <p>{{ getEmptyMessage() }}</p>
            <button v-if="filterStatus === 'all'" @click="createNewTodo" class="add-btn empty-btn">
              <span class="btn-icon">➕</span>
              <span class="btn-text">创建第一个任务</span>
              <span class="btn-effect"></span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'TodoPage',
  data() {
    return {
      todos: [],
      newTodo: {
        title: '',
        description: '',
        priority: 'medium',
        due_date: ''
      },
      editingId: null,
      editForm: {},
      filterStatus: 'all'
    }
  },
  computed: {
    filteredTodos() {
      if (this.filterStatus === 'all') {
        return this.todos
      } else if (this.filterStatus === 'pending') {
        return this.todos.filter(todo => !todo.completed)
      } else {
        return this.todos.filter(todo => todo.completed)
      }
    },
    totalTodos() {
      return this.todos.length
    },
    completedTodos() {
      return this.todos.filter(todo => todo.completed).length
    },
    pendingTodos() {
      return this.todos.filter(todo => !todo.completed).length
    },
    progressPercentage() {
      if (this.totalTodos === 0) return 0
      return Math.round((this.completedTodos / this.totalTodos) * 100)
    }
  },
  mounted() {
    this.loadTodos()
  },
  methods: {
    async loadTodos() {
      try {
        const response = await axios.get('/api/todos')
        this.todos = response.data
      } catch (error) {
        console.error('加载待办事项失败:', error)
      }
    },
    async addTodo() {
      if (!this.newTodo.title.trim()) return
      
      try {
        await axios.post('/api/todos', this.newTodo)
        this.newTodo = {
          title: '',
          description: '',
          priority: 'medium',
          due_date: ''
        }
        this.loadTodos()
      } catch (error) {
        console.error('添加待办事项失败:', error)
      }
    },
    async toggleTodo(id) {
      try {
        await axios.post(`/api/todos/${id}/toggle`)
        this.loadTodos()
      } catch (error) {
        console.error('切换任务状态失败:', error)
      }
    },
    async deleteTodo(id) {
      if (confirm('确定要删除这个任务吗？')) {
        try {
          await axios.delete(`/api/todos/${id}`)
          this.loadTodos()
        } catch (error) {
          console.error('删除待办事项失败:', error)
        }
      }
    },
    startEdit(todo) {
      this.editingId = todo.id
      this.editForm = { ...todo }
    },
    async saveEdit() {
      try {
        await axios.put(`/api/todos/${this.editingId}`, this.editForm)
        this.editingId = null
        this.editForm = {}
        this.loadTodos()
      } catch (error) {
        console.error('更新待办事项失败:', error)
      }
    },
    cancelEdit() {
      this.editingId = null
      this.editForm = {}
    },
    getPriorityIcon(priority) {
      const icons = {
        low: '🟢',
        medium: '🟡',
        high: '🔴'
      }
      return icons[priority] || '🟡'
    },
    getPriorityText(priority) {
      const texts = {
        low: '低',
        medium: '中',
        high: '高'
      }
      return texts[priority] || '中'
    },
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN')
    },
    getEmptyMessage() {
      if (this.filterStatus === 'pending') {
        return '🎉 太棒了！没有待完成的任务'
      } else if (this.filterStatus === 'completed') {
        return '还没有完成的任务'
      } else {
        return '还没有任务，点击左侧添加第一个任务吧！'
      }
    },
    createNewTodo() {
      // 聚焦到添加任务的输入框
      this.$nextTick(() => {
        const inputField = document.querySelector('.add-form .input-field')
        if (inputField) inputField.focus()
      })
    }
  }
}
</script>

<style scoped>
/* 动画关键帧 */
@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
  100% { transform: translateY(0px); }
}

@keyframes glow {
  0% { box-shadow: 0 0 5px rgba(123, 97, 255, 0.3); }
  50% { box-shadow: 0 0 20px rgba(123, 97, 255, 0.6); }
  100% { box-shadow: 0 0 5px rgba(123, 97, 255, 0.3); }
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

@keyframes typing {
  from { width: 0 }
  to { width: 100% }
}

.todo-page {
  min-height: 100vh;
  padding: 20px;
  background-color: #1e293b; /* 深蓝灰色背景 */
  color: #e2e8f0;
  position: relative;
  overflow: hidden;
}

/* AI 风格装饰元素 */
.todo-page::before,
.todo-page::after {
  content: '';
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  z-index: -1;
  opacity: 0.15;
}

.todo-page::before {
  width: 500px;
  height: 500px;
  background: linear-gradient(135deg, #7c3aed, #3b82f6);
  top: -100px;
  left: -100px;
  animation: float 15s infinite ease-in-out;
}

.todo-page::after {
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, #ec4899, #8b5cf6);
  bottom: -100px;
  right: -100px;
  animation: float 20s infinite ease-in-out reverse;
}

.top-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 0 10px;
  position: relative;
  z-index: 1;
}

.page-title {
  font-size: 2.5rem;
  font-weight: bold;
  margin: 0;
  position: relative;
  z-index: 1;
}

.gradient-text {
  background: linear-gradient(135deg, #7c3aed, #3b82f6, #ec4899);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  animation: shimmer 8s infinite linear;
  background-size: 200% 100%;
}

.nav-buttons {
  display: flex;
  gap: 15px;
}

.nav-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 25px;
  color: #e2e8f0;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  position: relative;
  overflow: hidden;
}

.nav-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: all 0.5s ease;
}

.nav-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.nav-btn:hover::before {
  left: 100%;
}

.todo-container {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 30px;
  max-width: 1400px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

/* AI 面板样式 */
.glass-panel {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 25px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  margin-bottom: 20px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.ai-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #7c3aed, #3b82f6, #ec4899, #7c3aed);
  background-size: 300% 100%;
  animation: shimmer 6s infinite linear;
}

.panel-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  gap: 10px;
}

.ai-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #7c3aed, #3b82f6);
  border-radius: 50%;
  font-size: 18px;
  box-shadow: 0 0 15px rgba(124, 58, 237, 0.5);
  animation: pulse 3s infinite ease-in-out;
}

.ai-icon.small {
  width: 24px;
  height: 24px;
  font-size: 14px;
}

.glass-panel h3 {
  margin: 0;
  color: #e2e8f0;
  font-size: 1.3rem;
  font-weight: 600;
}

.add-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.input-wrapper {
  position: relative;
}

.ai-suggestion {
  display: flex;
  gap: 8px;
  margin-top: 8px;
  flex-wrap: wrap;
}

.suggestion-chip {
  background: rgba(124, 58, 237, 0.2);
  border: 1px solid rgba(124, 58, 237, 0.3);
  border-radius: 20px;
  padding: 4px 12px;
  font-size: 0.8rem;
  color: #c4b5fd;
  cursor: pointer;
  transition: all 0.3s ease;
}

.suggestion-chip:hover {
  background: rgba(124, 58, 237, 0.3);
  transform: translateY(-2px);
}

.input-field, .textarea-field, .select-field, .date-field {
  padding: 14px 16px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.5);
  color: #e2e8f0;
  font-size: 14px;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  width: 100%;
}

.input-field:focus, .textarea-field:focus, .select-field:focus, .date-field:focus {
  outline: none;
  border-color: #7c3aed;
  background: rgba(15, 23, 42, 0.7);
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.2);
}

.textarea-field {
  resize: vertical;
  min-height: 80px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.add-btn, .save-btn, .cancel-btn {
  padding: 14px 20px;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  position: relative;
  overflow: hidden;
}

.btn-icon {
  font-size: 1.2rem;
  position: relative;
  z-index: 2;
}

.btn-text {
  position: relative;
  z-index: 2;
}

.btn-effect {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: all 0.5s ease;
}

.add-btn, .save-btn {
  background: linear-gradient(135deg, #7c3aed, #3b82f6);
  color: white;
}

.add-btn:hover, .save-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(124, 58, 237, 0.3);
}

.add-btn:hover .btn-effect, .save-btn:hover .btn-effect {
  left: 100%;
}

.cancel-btn {
  background: rgba(255, 255, 255, 0.1);
  color: #e2e8f0;
}

.cancel-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
}

.stats-panel {
  margin-top: 20px;
}

.stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
  padding: 15px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.stat-circle {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(124, 58, 237, 0.2), rgba(59, 130, 246, 0.2));
  border: 2px solid rgba(124, 58, 237, 0.3);
  position: relative;
  overflow: hidden;
}

.stat-circle::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  animation: shimmer 3s infinite linear;
}

.stat-circle.completed {
  background: linear-gradient(135deg, rgba(46, 204, 113, 0.2), rgba(39, 174, 96, 0.2));
  border-color: rgba(46, 204, 113, 0.3);
}

.stat-circle.pending {
  background: linear-gradient(135deg, rgba(236, 72, 153, 0.2), rgba(225, 29, 72, 0.2));
  border-color: rgba(236, 72, 153, 0.3);
}

.stat-number {
  font-size: 1.8rem;
  font-weight: bold;
  color: #e2e8f0;
  position: relative;
  z-index: 1;
}

.stat-label {
  font-size: 0.9rem;
  color: #94a3b8;
}

.progress-container {
  margin-bottom: 20px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 10px;
  position: relative;
}

.progress-bar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  animation: shimmer 2s infinite linear;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #7c3aed, #3b82f6);
  transition: width 0.5s ease;
  position: relative;
  z-index: 1;
}

.progress-text {
  text-align: center;
  color: #94a3b8;
  font-size: 0.9rem;
  margin: 0;
}

.ai-insights {
  background: rgba(15, 23, 42, 0.3);
  border-radius: 12px;
  padding: 15px;
  margin-top: 20px;
  border-left: 3px solid #7c3aed;
}

.insight-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.insight-header h4 {
  margin: 0;
  font-size: 1rem;
  color: #e2e8f0;
}

.insight-content p {
  margin: 0;
  font-size: 0.9rem;
  color: #94a3b8;
  line-height: 1.5;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.filter-buttons {
  display: flex;
  gap: 10px;
}

.filter-btn {
  padding: 8px 16px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  background: rgba(15, 23, 42, 0.3);
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.filter-btn.active, .filter-btn:hover {
  background: rgba(124, 58, 237, 0.2);
  border-color: #7c3aed;
  color: #c4b5fd;
}

.todo-list {
  max-height: 600px;
  overflow-y: auto;
  padding-right: 5px;
}

.todo-list::-webkit-scrollbar {
  width: 6px;
}

.todo-list::-webkit-scrollbar-track {
  background: rgba(15, 23, 42, 0.3);
  border-radius: 3px;
}

.todo-list::-webkit-scrollbar-thumb {
  background: rgba(124, 58, 237, 0.5);
  border-radius: 3px;
}

.todo-item {
  background: rgba(15, 23, 42, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 15px;
  padding: 20px;
  margin-bottom: 15px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.todo-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 3px;
  height: 100%;
  background: linear-gradient(to bottom, #7c3aed, #3b82f6);
  opacity: 0.7;
}

.todo-item:hover {
  background: rgba(15, 23, 42, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.todo-item.completed {
  opacity: 0.7;
}

.todo-item.completed::before {
  background: linear-gradient(to bottom, #10b981, #059669);
}

.todo-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.todo-main {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  flex: 1;
}

.checkbox-wrapper {
  position: relative;
  width: 24px;
  height: 24px;
}

.todo-checkbox {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

.checkmark {
  position: absolute;
  top: 0;
  left: 0;
  height: 24px;
  width: 24px;
  background: rgba(15, 23, 42, 0.5);
  border: 2px solid rgba(124, 58, 237, 0.5);
  border-radius: 6px;
  transition: all 0.3s ease;
}

.todo-checkbox:checked ~ .checkmark {
  background: linear-gradient(135deg, #7c3aed, #3b82f6);
  border-color: transparent;
}

.checkmark:after {
  content: "";
  position: absolute;
  display: none;
  left: 8px;
  top: 4px;
  width: 5px;
  height: 10px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.todo-checkbox:checked ~ .checkmark:after {
  display: block;
}

.todo-info {
  flex: 1;
}

.todo-title {
  margin: 0 0 8px 0;
  color: #e2e8f0;
  font-size: 1.1rem;
  font-weight: 600;
  transition: all 0.3s ease;
}

.todo-title.completed {
  text-decoration: line-through;
  color: #94a3b8;
}

.todo-description {
  margin: 0 0 10px 0;
  color: #94a3b8;
  font-size: 0.95rem;
  line-height: 1.4;
}

.todo-meta {
  display: flex;
  gap: 15px;
  font-size: 0.85rem;
  flex-wrap: wrap;
}

.priority {
  padding: 4px 10px;
  border-radius: 12px;
  font-weight: 500;
}

.priority.low {
  background: rgba(16, 185, 129, 0.2);
  color: #34d399;
}

.priority.medium {
  background: rgba(245, 158, 11, 0.2);
  color: #fbbf24;
}

.priority.high {
  background: rgba(239, 68, 68, 0.2);
  color: #f87171;
}

.due-date {
  color: #94a3b8;
}

.todo-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

.edit-btn {
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
}

.edit-btn:hover {
  background: rgba(59, 130, 246, 0.3);
  transform: translateY(-2px);
}

.delete-btn {
  background: rgba(239, 68, 68, 0.2);
  color: #f87171;
}

.delete-btn:hover {
  background: rgba(239, 68, 68, 0.3);
  transform: translateY(-2px);
}

.edit-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.edit-actions {
  display: flex;
  gap: 10px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #94a3b8;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 10px;
  animation: float 3s infinite ease-in-out;
}

.empty-state p {
  font-size: 1.1rem;
  margin: 0;
}

.empty-btn {
  width: auto;
  margin-top: 10px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .todo-container {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .top-nav {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }
  
  .nav-buttons {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .stats {
    grid-template-columns: 1fr;
  }
  
  .list-header {
    flex-direction: column;
    gap: 15px;
  }
  
  .filter-buttons {
    justify-content: center;
  }
}
</style>