<template>
  <div class="project-page">
    <div class="main-layout">
      <!-- 左侧导航 -->
      <div class="left-sidebar">
        <div class="nav-buttons">
          <router-link to="/" class="btn btn-secondary">📝 笔记</router-link>
          <router-link to="/todos" class="btn btn-secondary">✅ 待办</router-link>
          <router-link to="/chat" class="btn btn-secondary">🤖 AI对话</router-link>
          <router-link to="/pomodoro" class="btn btn-secondary">🍅 番茄钟</router-link>
          <router-link to="/projects" class="btn btn-primary">📊 项目</router-link>
          <router-link to="/settings" class="btn btn-secondary">⚙️ 设置</router-link>
        </div>
      </div>

      <!-- 中间内容区域 -->
      <div class="center-content">
        <div class="project-container glass-panel">
          <div class="project-header">
            <h1>任务 (Tasks)</h1>
            <div class="project-actions">
              <button class="btn btn-primary" @click="openTaskForm(null)">+ 新建任务</button>
              <div class="dropdown">
                <button class="btn btn-secondary dropdown-toggle" @click="toggleFilterDropdown">
                  过滤 <i class="fas fa-chevron-down"></i>
                </button>
                <div class="dropdown-menu" v-if="showFilterDropdown">
                  <div class="dropdown-item">
                    <label>优先级</label>
                    <div class="filter-options">
                      <label><input type="checkbox" v-model="filters.priority.high"> 高</label>
                      <label><input type="checkbox" v-model="filters.priority.medium"> 中</label>
                      <label><input type="checkbox" v-model="filters.priority.low"> 低</label>
                    </div>
                  </div>
                  <div class="dropdown-item">
                    <label>标签</label>
                    <div class="filter-options">
                      <div v-for="tag in availableTags" :key="tag.id">
                        <label>
                          <input type="checkbox" v-model="filters.tags[tag.id]"> 
                          <span class="tag" :style="{backgroundColor: tag.color}">{{ tag.name }}</span>
                        </label>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div class="dropdown">
                <button class="btn btn-secondary dropdown-toggle" @click="toggleSortDropdown">
                  排序 <i class="fas fa-chevron-down"></i>
                </button>
                <div class="dropdown-menu" v-if="showSortDropdown">
                  <div class="dropdown-item" @click="setSortBy('dueDate')">截止日期</div>
                  <div class="dropdown-item" @click="setSortBy('createdAt')">创建时间</div>
                  <div class="dropdown-item" @click="setSortBy('priority')">优先级</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 任务列表 -->
          <div class="tasks-table">
            <table>
              <thead>
                <tr>
                  <th class="checkbox-col"></th>
                  <th class="title-col">任务标题</th>
                  <th class="assignee-col">负责人</th>
                  <th class="tags-col">标签</th>
                  <th class="due-date-col">截止日期</th>
                  <th class="priority-col">优先级</th>
                  <th class="actions-col"></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="task in filteredTasks" :key="task.id" :class="{ 'completed': task.status === 'DONE' }">
                  <td>
                    <input type="checkbox" :checked="task.status === 'DONE'" @change="toggleTaskStatus(task)">
                  </td>
                  <td class="title-col">
                    {{ task.title }}
                    <i class="fas fa-file-alt note-icon" v-if="task.linkedNotes && task.linkedNotes.length > 0"></i>
                  </td>
                  <td class="assignee-col">
                    <div class="avatar">{{ getInitials(task.assignee) }}</div>
                  </td>
                  <td class="tags-col">
                    <span 
                      v-for="tag in task.tags" 
                      :key="tag.id" 
                      class="tag" 
                      :style="{backgroundColor: tag.color}"
                    >
                      {{ tag.name }}
                    </span>
                  </td>
                  <td class="due-date-col" :class="getDueDateClass(task.dueDate)">
                    {{ formatDate(task.dueDate) }}
                  </td>
                  <td class="priority-col">
                    <span class="priority-indicator" :class="'priority-' + task.priority.toLowerCase()">
                      {{ getPriorityIcon(task.priority) }}
                    </span>
                  </td>
                  <td class="actions-col">
                    <div class="dropdown">
                      <button class="btn-icon" @click="toggleActionDropdown(task.id)">
                        <i class="fas fa-ellipsis-v"></i>
                      </button>
                      <div class="dropdown-menu" v-if="actionDropdownId === task.id">
                        <div class="dropdown-item" @click="openTaskForm(task)">编辑</div>
                        <div class="dropdown-item" @click="confirmDeleteTask(task)">删除</div>
                      </div>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
            <div class="empty-state" v-if="filteredTasks.length === 0">
              <div class="empty-icon">📋</div>
              <h3>暂无任务</h3>
              <p>点击"新建任务"按钮创建您的第一个任务</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 任务表单侧边栏 -->
    <div class="task-form-sidebar" :class="{ 'open': showTaskForm }">
      <div class="task-form glass-panel">
        <div class="form-header">
          <h2>{{ isEditMode ? '编辑任务' : '新建任务' }}</h2>
          <button class="btn-icon" @click="closeTaskForm">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="form-content">
          <div class="form-group">
            <label for="taskTitle">任务标题</label>
            <input type="text" id="taskTitle" v-model="currentTask.title" placeholder="输入任务标题...">
          </div>
          <div class="form-group">
            <label for="taskDescription">描述</label>
            <textarea id="taskDescription" v-model="currentTask.description" placeholder="详细描述任务..."></textarea>
          </div>
          <div class="form-group">
            <label for="taskAssignee">负责人</label>
            <select id="taskAssignee" v-model="currentTask.assigneeId">
              <option v-for="user in users" :key="user.id" :value="user.id">{{ user.name }}</option>
            </select>
          </div>
          <div class="form-group">
            <label for="taskDueDate">截止日期</label>
            <input type="date" id="taskDueDate" v-model="currentTask.dueDate">
          </div>
          <div class="form-group">
            <label for="taskPriority">优先级</label>
            <select id="taskPriority" v-model="currentTask.priority">
              <option value="HIGH">高</option>
              <option value="MEDIUM">中</option>
              <option value="LOW">低</option>
            </select>
          </div>
          <div class="form-group">
            <label>标签</label>
            <div class="tags-input">
              <div class="selected-tags">
                <span 
                  v-for="tag in selectedTags" 
                  :key="tag.id" 
                  class="tag" 
                  :style="{backgroundColor: tag.color}"
                >
                  {{ tag.name }}
                  <button class="tag-remove" @click="removeTag(tag)">×</button>
                </span>
              </div>
              <div class="tags-dropdown">
                <input 
                  type="text" 
                  v-model="tagInput" 
                  @focus="showTagsDropdown = true" 
                  placeholder="添加标签..."
                >
                <div class="dropdown-menu" v-if="showTagsDropdown">
                  <div 
                    v-for="tag in filteredAvailableTags" 
                    :key="tag.id" 
                    class="dropdown-item"
                    @click="addTag(tag)"
                  >
                    <span class="tag" :style="{backgroundColor: tag.color}">{{ tag.name }}</span>
                  </div>
                  <div class="dropdown-item new-tag" v-if="tagInput && !tagExists(tagInput)" @click="createNewTag">
                    创建标签 "{{ tagInput }}"
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 关联笔记区 -->
          <div class="form-section">
            <h3>关联的笔记</h3>
            <div class="linked-notes">
              <div v-for="note in currentTask.linkedNotes" :key="note.id" class="linked-note">
                <span>{{ note.title }}</span>
                <button class="btn-icon" @click="unlinkNote(note)">
                  <i class="fas fa-times"></i>
                </button>
              </div>
              <button class="btn btn-secondary" @click="openLinkNoteDialog">
                + 关联笔记
              </button>
            </div>
          </div>

          <!-- AI 助理区 -->
          <div class="form-section">
            <h3>AI 助理</h3>
            <button class="btn btn-ai" @click="breakdownTask" :disabled="!currentTask.title">
              <i class="fas fa-robot"></i> 分解任务
            </button>
            <div class="ai-loading" v-if="aiLoading">
              <div class="spinner"></div>
              <span>AI 正在分析您的任务...</span>
            </div>
          </div>

          <div class="form-actions">
            <button class="btn btn-secondary" @click="closeTaskForm">取消</button>
            <button class="btn btn-primary" @click="saveTask">保存</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 关联笔记对话框 -->
    <div class="modal" v-if="showLinkNoteDialog">
      <div class="modal-content glass-panel">
        <div class="modal-header">
          <h3>关联笔记</h3>
          <button class="btn-icon" @click="closeLinkNoteDialog">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="search-box">
            <input type="text" v-model="noteSearchQuery" placeholder="搜索笔记...">
          </div>
          <div class="notes-list">
            <div 
              v-for="note in filteredNotes" 
              :key="note.id" 
              class="note-item"
              @click="toggleNoteSelection(note)"
              :class="{ 'selected': isNoteSelected(note) }"
            >
              <div class="note-title">{{ note.title }}</div>
              <div class="note-preview">{{ getNoteSummary(note) }}</div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeLinkNoteDialog">取消</button>
          <button class="btn btn-primary" @click="confirmLinkNotes">确认关联</button>
        </div>
      </div>
    </div>

    <!-- 删除确认对话框 -->
    <div class="modal" v-if="showDeleteConfirm">
      <div class="modal-content glass-panel">
        <div class="modal-header">
          <h3>确认删除</h3>
          <button class="btn-icon" @click="cancelDelete">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <p>确定要删除任务 "{{ taskToDelete?.title }}" 吗？此操作无法撤销。</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="cancelDelete">取消</button>
          <button class="btn btn-danger" @click="deleteTask">删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'

export default {
  name: 'ProjectPage',
  setup() {
    // 状态变量
    const tasks = ref([])
    const users = ref([{ id: 1, name: '我自己' }])
    const availableTags = ref([
      { id: 1, name: '开发', color: '#4CAF50' },
      { id: 2, name: '设计', color: '#2196F3' },
      { id: 3, name: '文档', color: '#FF9800' },
      { id: 4, name: '会议', color: '#9C27B0' },
      { id: 5, name: '紧急', color: '#F44336' }
    ])
    const notes = ref([])
    
    // UI 状态
    const showFilterDropdown = ref(false)
    const showSortDropdown = ref(false)
    const showTaskForm = ref(false)
    const showTagsDropdown = ref(false)
    const showLinkNoteDialog = ref(false)
    const showDeleteConfirm = ref(false)
    const actionDropdownId = ref(null)
    const aiLoading = ref(false)
    
    // 表单状态
    const isEditMode = ref(false)
    const currentTask = reactive({
      id: null,
      title: '',
      description: '',
      status: 'TODO',
      priority: 'MEDIUM',
      dueDate: '',
      assigneeId: 1,
      tags: [],
      linkedNotes: []
    })
    const tagInput = ref('')
    const noteSearchQuery = ref('')
    const selectedNoteIds = ref([])
    const taskToDelete = ref(null)
    
    // 过滤和排序
    const filters = reactive({
      priority: {
        high: true,
        medium: true,
        low: true
      },
      tags: {}
    })
    const sortBy = ref('dueDate')
    
    // 初始化
    onMounted(() => {
      loadTasks()
      loadNotes()
      // 初始化标签过滤器
      availableTags.value.forEach(tag => {
        filters.tags[tag.id] = true
      })
    })
    
    // 计算属性
    const filteredTasks = computed(() => {
      return tasks.value
        .filter(task => {
          // 优先级过滤
          if (task.priority === 'HIGH' && !filters.priority.high) return false
          if (task.priority === 'MEDIUM' && !filters.priority.medium) return false
          if (task.priority === 'LOW' && !filters.priority.low) return false
          
          // 标签过滤
          if (task.tags && task.tags.length > 0) {
            const hasMatchingTag = task.tags.some(tag => filters.tags[tag.id])
            if (!hasMatchingTag) return false
          }
          
          return true
        })
        .sort((a, b) => {
          if (sortBy.value === 'dueDate') {
            return new Date(a.dueDate) - new Date(b.dueDate)
          } else if (sortBy.value === 'createdAt') {
            return new Date(a.createdAt) - new Date(b.createdAt)
          } else if (sortBy.value === 'priority') {
            const priorityOrder = { 'HIGH': 0, 'MEDIUM': 1, 'LOW': 2 }
            return priorityOrder[a.priority] - priorityOrder[b.priority]
          }
          return 0
        })
    })
    
    const filteredAvailableTags = computed(() => {
      if (!tagInput.value) return availableTags.value
      return availableTags.value.filter(tag => 
        tag.name.toLowerCase().includes(tagInput.value.toLowerCase())
      )
    })
    
    const selectedTags = computed(() => {
      return currentTask.tags || []
    })
    
    const filteredNotes = computed(() => {
      if (!noteSearchQuery.value) return notes.value
      return notes.value.filter(note => 
        note.title.toLowerCase().includes(noteSearchQuery.value.toLowerCase())
      )
    })
    
    // 方法
    function loadTasks() {
      // 模拟从API加载任务
      const savedTasks = localStorage.getItem('tasks')
      if (savedTasks) {
        tasks.value = JSON.parse(savedTasks)
      } else {
        // 示例数据
        tasks.value = [
          {
            id: 1,
            title: '完成项目管理页面设计',
            description: '设计并实现项目管理页面的UI和功能',
            status: 'TODO',
            priority: 'HIGH',
            dueDate: '2023-12-31',
            assigneeId: 1,
            createdAt: '2023-12-15',
            tags: [{ id: 1, name: '开发', color: '#4CAF50' }, { id: 2, name: '设计', color: '#2196F3' }],
            linkedNotes: [{ id: 1, title: '项目管理页面需求' }]
          },
          {
            id: 2,
            title: '编写API文档',
            description: '为项目管理API编写详细文档',
            status: 'TODO',
            priority: 'MEDIUM',
            dueDate: '2024-01-15',
            assigneeId: 1,
            createdAt: '2023-12-20',
            tags: [{ id: 3, name: '文档', color: '#FF9800' }],
            linkedNotes: []
          },
          {
            id: 3,
            title: '项目进度会议',
            description: '与团队讨论项目进度和下一步计划',
            status: 'DONE',
            priority: 'LOW',
            dueDate: '2023-12-10',
            assigneeId: 1,
            createdAt: '2023-12-05',
            tags: [{ id: 4, name: '会议', color: '#9C27B0' }],
            linkedNotes: []
          }
        ]
        saveTasks()
      }
    }
    
    function loadNotes() {
      // 模拟从API加载笔记
      const savedNotes = localStorage.getItem('notes')
      if (savedNotes) {
        notes.value = JSON.parse(savedNotes)
      } else {
        // 示例数据
        notes.value = [
          { id: 1, title: '项目管理页面需求', content: '项目管理页面需要包含任务列表、过滤和排序功能...' },
          { id: 2, title: '会议记录：项目启动', content: '讨论了项目目标、时间线和责任分工...' },
          { id: 3, title: 'API设计文档', content: '项目管理API包括以下端点：GET /api/tasks...' }
        ]
      }
    }
    
    function saveTasks() {
      localStorage.setItem('tasks', JSON.stringify(tasks.value))
    }
    
    function toggleFilterDropdown() {
      showFilterDropdown.value = !showFilterDropdown.value
      if (showFilterDropdown.value) showSortDropdown.value = false
    }
    
    function toggleSortDropdown() {
      showSortDropdown.value = !showSortDropdown.value
      if (showSortDropdown.value) showFilterDropdown.value = false
    }
    
    function setSortBy(value) {
      sortBy.value = value
      showSortDropdown.value = false
    }
    
    function toggleActionDropdown(taskId) {
      if (actionDropdownId.value === taskId) {
        actionDropdownId.value = null
      } else {
        actionDropdownId.value = taskId
      }
    }
    
    function openTaskForm(task) {
      if (task) {
        // 编辑模式
        isEditMode.value = true
        Object.assign(currentTask, JSON.parse(JSON.stringify(task)))
      } else {
        // 创建模式
        isEditMode.value = false
        Object.assign(currentTask, {
          id: null,
          title: '',
          description: '',
          status: 'TODO',
          priority: 'MEDIUM',
          dueDate: formatDateForInput(new Date()),
          assigneeId: 1,
          tags: [],
          linkedNotes: []
        })
      }
      showTaskForm.value = true
    }
    
    function closeTaskForm() {
      showTaskForm.value = false
    }
    
    function saveTask() {
      if (!currentTask.title.trim()) {
        alert('任务标题不能为空')
        return
      }
      
      const taskToSave = JSON.parse(JSON.stringify(currentTask))
      
      if (!isEditMode.value) {
        // 创建新任务
        taskToSave.id = Date.now()
        taskToSave.createdAt = new Date().toISOString()
        tasks.value.push(taskToSave)
      } else {
        // 更新现有任务
        const index = tasks.value.findIndex(t => t.id === taskToSave.id)
        if (index !== -1) {
          tasks.value[index] = taskToSave
        }
      }
      
      saveTasks()
      closeTaskForm()
    }
    
    function toggleTaskStatus(task) {
      const taskToUpdate = tasks.value.find(t => t.id === task.id)
      if (taskToUpdate) {
        taskToUpdate.status = taskToUpdate.status === 'DONE' ? 'TODO' : 'DONE'
        saveTasks()
      }
    }
    
    function confirmDeleteTask(task) {
      taskToDelete.value = task
      showDeleteConfirm.value = true
    }
    
    function deleteTask() {
      if (taskToDelete.value) {
        const index = tasks.value.findIndex(t => t.id === taskToDelete.value.id)
        if (index !== -1) {
          tasks.value.splice(index, 1)
          saveTasks()
        }
      }
      showDeleteConfirm.value = false
      taskToDelete.value = null
    }
    
    function cancelDelete() {
      showDeleteConfirm.value = false
      taskToDelete.value = null
    }
    
    function addTag(tag) {
      if (!currentTask.tags) currentTask.tags = []
      if (!currentTask.tags.some(t => t.id === tag.id)) {
        currentTask.tags.push(tag)
      }
      tagInput.value = ''
      showTagsDropdown.value = false
    }
    
    function removeTag(tag) {
      const index = currentTask.tags.findIndex(t => t.id === tag.id)
      if (index !== -1) {
        currentTask.tags.splice(index, 1)
      }
    }
    
    function tagExists(name) {
      return availableTags.value.some(tag => 
        tag.name.toLowerCase() === name.toLowerCase()
      )
    }
    
    function createNewTag() {
      if (!tagInput.value.trim()) return
      
      const newTag = {
        id: Date.now(),
        name: tagInput.value.trim(),
        color: getRandomColor()
      }
      
      availableTags.value.push(newTag)
      filters.tags[newTag.id] = true
      addTag(newTag)
    }
    
    function getRandomColor() {
      const colors = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336', '#009688', '#673AB7', '#FFC107']
      return colors[Math.floor(Math.random() * colors.length)]
    }
    
    function openLinkNoteDialog() {
      selectedNoteIds.value = currentTask.linkedNotes.map(note => note.id)
      showLinkNoteDialog.value = true
    }
    
    function closeLinkNoteDialog() {
      showLinkNoteDialog.value = false
      noteSearchQuery.value = ''
    }
    
    function toggleNoteSelection(note) {
      const index = selectedNoteIds.value.indexOf(note.id)
      if (index === -1) {
        selectedNoteIds.value.push(note.id)
      } else {
        selectedNoteIds.value.splice(index, 1)
      }
    }
    
    function isNoteSelected(note) {
      return selectedNoteIds.value.includes(note.id)
    }
    
    function confirmLinkNotes() {
      // 更新当前任务的关联笔记
      currentTask.linkedNotes = notes.value
        .filter(note => selectedNoteIds.value.includes(note.id))
        .map(note => ({ id: note.id, title: note.title }))
      
      closeLinkNoteDialog()
    }
    
    function unlinkNote(note) {
      const index = currentTask.linkedNotes.findIndex(n => n.id === note.id)
      if (index !== -1) {
        currentTask.linkedNotes.splice(index, 1)
      }
    }
    
    function breakdownTask() {
      if (!currentTask.title) return
      
      aiLoading.value = true
      
      // 模拟AI处理
      setTimeout(() => {
        const taskBreakdown = `## 任务分解

### 步骤
- [ ] 分析需求
- [ ] 设计解决方案
- [ ] 实现核心功能
- [ ] 测试和调试
- [ ] 文档和部署

### 资源需求
- 开发环境设置
- 相关文档参考
- 测试数据准备`
        
        if (currentTask.description) {
          currentTask.description += '\n\n' + taskBreakdown
        } else {
          currentTask.description = taskBreakdown
        }
        
        aiLoading.value = false
      }, 1500)
    }
    
    // 辅助函数
    function formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN')
    }
    
    function formatDateForInput(date) {
      return date.toISOString().split('T')[0]
    }
    
    function getInitials(name) {
      if (!name) return ''
      return name.split(' ').map(n => n[0]).join('').toUpperCase()
    }
    
    function getDueDateClass(dateString) {
      if (!dateString) return ''
      
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      
      const dueDate = new Date(dateString)
      dueDate.setHours(0, 0, 0, 0)
      
      const diffTime = dueDate - today
      const diffDays = diffTime / (1000 * 60 * 60 * 24)
      
      if (diffDays < 0) return 'overdue'
      if (diffDays <= 2) return 'due-soon'
      return ''
    }
    
    function getPriorityIcon(priority) {
      switch (priority) {
        case 'HIGH': return '🔥'
        case 'MEDIUM': return '▲'
        case 'LOW': return '▼'
        default: return ''
      }
    }
    
    function getNoteSummary(note) {
      if (!note.content) return ''
      return note.content.length > 60 ? note.content.substring(0, 60) + '...' : note.content
    }
    
    return {
      tasks,
      users,
      availableTags,
      notes,
      showFilterDropdown,
      showSortDropdown,
      showTaskForm,
      showTagsDropdown,
      showLinkNoteDialog,
      showDeleteConfirm,
      actionDropdownId,
      aiLoading,
      isEditMode,
      currentTask,
      tagInput,
      noteSearchQuery,
      selectedNoteIds,
      taskToDelete,
      filters,
      sortBy,
      filteredTasks,
      filteredAvailableTags,
      selectedTags,
      filteredNotes,
      toggleFilterDropdown,
      toggleSortDropdown,
      setSortBy,
      toggleActionDropdown,
      openTaskForm,
      closeTaskForm,
      saveTask,
      toggleTaskStatus,
      confirmDeleteTask,
      deleteTask,
      cancelDelete,
      addTag,
      removeTag,
      tagExists,
      createNewTag,
      openLinkNoteDialog,
      closeLinkNoteDialog,
      toggleNoteSelection,
      isNoteSelected,
      confirmLinkNotes,
      unlinkNote,
      breakdownTask,
      formatDate,
      getInitials,
      getDueDateClass,
      getPriorityIcon,
      getNoteSummary
    }
  }
}
</script>

<style scoped>
.project-page {
  height: 100vh;
  overflow: hidden;
  position: relative;
}

.main-layout {
  display: flex;
  height: 100vh;
}

.left-sidebar {
  width: 200px;
  padding: 20px;
  background-color: rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
  display: flex;
  flex-direction: column;
  border-right: 1px solid rgba(255, 255, 255, 0.1);
}

.nav-buttons {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.center-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.project-container {
  padding: 20px;
  border-radius: 10px;
  background-color: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.project-header h1 {
  margin: 0;
  font-size: 24px;
  color: white;
}

.project-actions {
  display: flex;
  gap: 10px;
}

.dropdown {
  position: relative;
}

.dropdown-toggle {
  display: flex;
  align-items: center;
  gap: 5px;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  z-index: 10;
  min-width: 200px;
  padding: 10px;
  margin-top: 5px;
  background-color: rgba(30, 30, 30, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 5px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.dropdown-item {
  padding: 8px 10px;
  cursor: pointer;
  border-radius: 4px;
  color: white;
}

.dropdown-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.filter-options {
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin-top: 5px;
}

.tasks-table {
  width: 100%;
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background-color: rgba(0, 0, 0, 0.2);
}

th, td {
  padding: 12px 15px;
  text-align: left;
  color: white;
}

th {
  font-weight: 500;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

tr {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

tr.completed {
  opacity: 0.6;
}

tr.completed .title-col {
  text-decoration: line-through;
}

.checkbox-col {
  width: 40px;
}

.title-col {
  min-width: 200px;
}

.assignee-col {
  width: 80px;
}

.tags-col {
  min-width: 150px;
}

.due-date-col {
  width: 100px;
}

.priority-col {
  width: 80px;
}

.actions-col {
  width: 50px;
}

.avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background-color: #2196F3;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 500;
}

.tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  color: white;
  margin-right: 5px;
  margin-bottom: 5px;
}

.note-icon {
  margin-left: 5px;
  color: rgba(255, 255, 255, 0.7);
}

.priority-indicator {
  font-size: 16px;
}

.priority-high {
  color: #F44336;
}

.priority-medium {
  color: #FF9800;
}

.priority-low {
  color: #9E9E9E;
}

.overdue {
  color: #F44336;
}

.due-soon {
  color: #FF9800;
}

.btn-icon {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  padding: 5px;
  border-radius: 4px;
}

.btn-icon:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 50px 0;
  color: rgba(255, 255, 255, 0.7);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.task-form-sidebar {
  position: fixed;
  top: 0;
  right: -500px;
  width: 450px;
  height: 100vh;
  transition: right 0.3s ease;
  z-index: 100;
}

.task-form-sidebar.open {
  right: 0;
}

.task-form {
  height: 100%;
  padding: 20px;
  background-color: rgba(30, 30, 30, 0.95);
  backdrop-filter: blur(10px);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.form-header h2 {
  margin: 0;
  color: white;
}

.form-content {
  flex: 1;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 10px;
  background-color: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  color: white;
}

.form-group textarea {
  min-height: 100px;
  resize: vertical;
}

.tags-input {
  background-color: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  padding: 5px;
}

.selected-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-bottom: 5px;
}

.tag-remove {
  background: none;
  border: none;
  color: white;
  margin-left: 5px;
  cursor: pointer;
  font-size: 14px;
}

.tags-dropdown input {
  background: none;
  border: none;
  color: white;
  width: 100%;
  padding: 5px;
}

.tags-dropdown input:focus {
  outline: none;
}

.new-tag {
  color: #4CAF50;
}

.form-section {
  margin-top: 30px;
  margin-bottom: 20px;
}

.form-section h3 {
  font-size: 16px;
  color: white;
  margin-bottom: 15px;
}

.linked-notes {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.linked-note {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}

.btn-ai {
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: #7E57C2;
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-ai:hover {
  background-color: #673AB7;
}

.btn-ai:disabled {
  background-color: rgba(126, 87, 194, 0.5);
  cursor: not-allowed;
}

.ai-loading {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 10px;
  color: rgba(255, 255, 255, 0.7);
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #7E57C2;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  width: 500px;
  max-width: 90%;
  max-height: 80vh;
  background-color: rgba(30, 30, 30, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-header h3 {
  margin: 0;
  color: white;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 15px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.search-box {
  margin-bottom: 15px;
}

.search-box input {
  width: 100%;
  padding: 10px;
  background-color: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  color: white;
}

.notes-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 300px;
  overflow-y: auto;
}

.note-item {
  padding: 10px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.note-item:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

.note-item.selected {
  background-color: rgba(33, 150, 243, 0.2);
  border: 1px solid rgba(33, 150, 243, 0.5);
}

.note-title {
  font-weight: 500;
  margin-bottom: 5px;
  color: white;
}

.note-preview {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

.btn {
  padding: 8px 16px;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
  border: none;
}

.btn-primary {
  background-color: #2196F3;
  color: white;
}

.btn-primary:hover {
  background-color: #1E88E5;
}

.btn-secondary {
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
}

.btn-secondary:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.btn-danger {
  background-color: #F44336;
  color: white;
}

.btn-danger:hover {
  background-color: #E53935;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-layout {
    flex-direction: column;
  }
  
  .left-sidebar {
    width: 100%;
    height: auto;
    padding: 10px;
  }
  
  .nav-buttons {
    flex-direction: row;
    overflow-x: auto;
    padding-bottom: 10px;
  }
  
  .project-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .project-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .task-form-sidebar {
    width: 100%;
    right: -100%;
  }
}
</style>