<template>
  <div class="note-list glass-panel">
    <div class="note-list-header">
      <h2>我的笔记</h2>
      <button @click="createNewNote" class="btn btn-primary">
        + 新建笔记
      </button>
    </div>
    
    <div class="note-list-content">
      <div 
        v-for="note in notes" 
        :key="note.id"
        @click="selectNote(note)"
        :class="['note-item', { active: selectedNoteId === note.id }]"
      >
        <div class="note-title">{{ note.title || '未命名笔记' }}</div>
        <div class="note-preview">{{ getPreview(note.content) }}</div>
        <div class="note-date">{{ formatDate(note.updated_at) }}</div>
        <button 
          @click.stop="deleteNote(note.id)"
          class="btn btn-danger note-delete"
        >
          删除
        </button>
      </div>
      
      <div v-if="notes.length === 0" class="empty-state">
        <p>还没有笔记，点击上方按钮创建第一个笔记吧！</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'NoteList',
  props: {
    selectedNoteId: {
      type: Number,
      default: null
    }
  },
  emits: ['note-selected', 'note-created', 'note-deleted'],
  data() {
    return {
      notes: []
    }
  },
  async mounted() {
    await this.loadNotes()
  },
  methods: {
    async loadNotes() {
      try {
        const response = await axios.get('/api/notes')
        this.notes = response.data
      } catch (error) {
        console.error('加载笔记失败:', error)
      }
    },
    
    async createNewNote() {
      try {
        const response = await axios.post('/api/notes', {
          title: '新建笔记',
          content: ''
        })
        await this.loadNotes()
        this.$emit('note-created', response.data.id)
      } catch (error) {
        console.error('创建笔记失败:', error)
      }
    },
    
    selectNote(note) {
      this.$emit('note-selected', note)
    },
    
    async deleteNote(noteId) {
      if (confirm('确定要删除这个笔记吗？')) {
        try {
          await axios.delete(`/api/notes/${noteId}`)
          await this.loadNotes()
          this.$emit('note-deleted', noteId)
        } catch (error) {
          console.error('删除笔记失败:', error)
        }
      }
    },
    
    getPreview(content) {
      return content.length > 50 ? content.substring(0, 50) + '...' : content
    },
    
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  }
}
</script>

<style scoped>
.note-list {
  height: 100%;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.note-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.note-list-header h2 {
  color: white;
  font-size: 18px;
  font-weight: 600;
}

.note-list-content {
  flex: 1;
  overflow-y: auto;
}

.note-item {
  padding: 15px;
  margin-bottom: 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
}

.note-item:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

.note-item.active {
  background: rgba(74, 144, 226, 0.3);
  border-color: rgba(74, 144, 226, 0.5);
}

.note-title {
  color: white;
  font-weight: 600;
  margin-bottom: 5px;
  font-size: 14px;
}

.note-preview {
  color: rgba(255, 255, 255, 0.8);
  font-size: 12px;
  line-height: 1.4;
  margin-bottom: 8px;
}

.note-date {
  color: rgba(255, 255, 255, 0.6);
  font-size: 11px;
}

.note-delete {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 4px 8px;
  font-size: 11px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.note-item:hover .note-delete {
  opacity: 1;
}

.empty-state {
  text-align: center;
  color: rgba(255, 255, 255, 0.7);
  padding: 40px 20px;
  font-size: 14px;
}
</style>