<template>
  <div class="note-page">
    <div class="main-layout">
      <!-- 笔记列表面板 -->
      <div class="note-list-panel">
        <NoteList 
          :selectedNoteId="selectedNote?.id"
          @note-selected="onNoteSelected"
          @note-created="onNoteCreated"
          @note-deleted="onNoteDeleted"
          ref="noteList"
        />
      </div>
      
      <!-- 编辑器面板 -->
      <div class="editor-panel">
        <Editor 
          :note="selectedNote"
          @note-updated="onNoteUpdated"
        />
      </div>
      
      <!-- AI助手面板 -->
      <div class="ai-assistant-panel">
        <AIAssistant :currentNote="selectedNote" />
      </div>
    </div>
    
    <!-- 顶部导航 -->
    <div class="top-nav">
      <div class="nav-content">
        <h1 class="app-title">拉布布记事本</h1>
        <div class="nav-actions">
          <router-link to="/todos" class="btn btn-secondary">
            ✅ 待办事项
          </router-link>
          <router-link to="/projects" class="btn btn-secondary">
            📊 项目
          </router-link>
          <router-link to="/chat" class="btn btn-secondary">
            🤖 AI对话
          </router-link>
          <router-link to="/pomodoro" class="btn btn-secondary">
            🍅 番茄钟
          </router-link>
          <router-link to="/settings" class="btn btn-primary">
            ⚙️ 设置
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import NoteList from '../components/NoteList.vue'
import Editor from '../components/Editor.vue'
import AIAssistant from '../components/AIAssistant.vue'
import axios from 'axios'

export default {
  name: 'NotePage',
  components: {
    NoteList,
    Editor,
    AIAssistant
  },
  data() {
    return {
      selectedNote: {
        id: null,
        title: '',
        content: ''
      }
    }
  },
  methods: {
    onNoteSelected(note) {
      this.selectedNote = { ...note }
    },
    
    async onNoteCreated(noteId) {
      try {
        const response = await axios.get(`/api/notes/${noteId}`)
        this.selectedNote = response.data
      } catch (error) {
        console.error('加载新创建的笔记失败:', error)
      }
    },
    
    onNoteDeleted(noteId) {
      if (this.selectedNote.id === noteId) {
        this.selectedNote = {
          id: null,
          title: '',
          content: ''
        }
      }
    },
    
    onNoteUpdated(note) {
      // 更新笔记列表
      if (this.$refs.noteList) {
        this.$refs.noteList.loadNotes()
      }
    }
  }
}
</script>

<style scoped>
.note-page {
  height: 100vh;
  position: relative;
}

.main-layout {
  display: flex;
  height: calc(100vh - 80px);
  padding: 20px;
  gap: 20px;
  margin-top: 80px;
}

.note-list-panel {
  width: 300px;
  min-width: 250px;
}

.editor-panel {
  flex: 1;
  min-width: 400px;
}

.ai-assistant-panel {
  width: 350px;
  min-width: 300px;
}

.top-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 20;
  padding: 20px;
}

.nav-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 25px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.app-title {
  color: white;
  font-size: 24px;
  font-weight: 700;
  margin: 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.nav-actions {
  display: flex;
  gap: 10px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .ai-assistant-panel {
    width: 300px;
    min-width: 280px;
  }
}

@media (max-width: 1000px) {
  .main-layout {
    flex-direction: column;
    height: auto;
    min-height: calc(100vh - 80px);
  }
  
  .note-list-panel,
  .editor-panel,
  .ai-assistant-panel {
    width: 100%;
    min-width: auto;
    height: 400px;
  }
  
  .editor-panel {
    height: 500px;
  }
}
</style>