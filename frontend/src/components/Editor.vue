<template>
  <div class="editor glass-panel">
    <div class="editor-header">
      <input 
        v-model="currentNote.title"
        @input="saveNote"
        class="input title-input"
        placeholder="笔记标题"
      />
      <div class="editor-actions">
        <button @click="saveNote" class="btn btn-primary">
          保存
        </button>
      </div>
    </div>
    
    <div class="editor-content">
      <textarea 
        v-model="currentNote.content"
        @input="saveNote"
        class="textarea content-textarea"
        placeholder="开始写下你的想法..."
      ></textarea>
    </div>
    
    <div v-if="!currentNote.id" class="empty-editor">
      <div class="empty-message">
        <h3>选择一个笔记开始编辑</h3>
        <p>或者创建一个新的笔记</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Editor',
  props: {
    note: {
      type: Object,
      default: () => ({ id: null, title: '', content: '' })
    }
  },
  emits: ['note-updated'],
  data() {
    return {
      currentNote: { ...this.note },
      saveTimeout: null
    }
  },
  watch: {
    note: {
      handler(newNote) {
        this.currentNote = { ...newNote }
      },
      deep: true,
      immediate: true
    }
  },
  methods: {
    saveNote() {
      if (!this.currentNote.id) return
      
      // 防抖保存，避免频繁请求
      if (this.saveTimeout) {
        clearTimeout(this.saveTimeout)
      }
      
      this.saveTimeout = setTimeout(async () => {
        try {
          await axios.put(`/api/notes/${this.currentNote.id}`, {
            title: this.currentNote.title,
            content: this.currentNote.content
          })
          this.$emit('note-updated', this.currentNote)
        } catch (error) {
          console.error('保存笔记失败:', error)
        }
      }, 1000) // 1秒后保存
    }
  }
}
</script>

<style scoped>
.editor {
  height: 100%;
  padding: 20px;
  display: flex;
  flex-direction: column;
  position: relative;
}

.editor-header {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  align-items: center;
}

.title-input {
  flex: 1;
  font-size: 18px;
  font-weight: 600;
}

.editor-actions {
  display: flex;
  gap: 10px;
}

.editor-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.content-textarea {
  flex: 1;
  resize: none;
  font-size: 14px;
  line-height: 1.6;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.empty-editor {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(5px);
  border-radius: 12px;
}

.empty-message {
  text-align: center;
  color: rgba(255, 255, 255, 0.8);
}

.empty-message h3 {
  font-size: 20px;
  margin-bottom: 10px;
  font-weight: 600;
}

.empty-message p {
  font-size: 14px;
  opacity: 0.8;
}
</style>