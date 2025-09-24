<template>
  <div class="ai-assistant glass-panel">
    <div class="ai-header">
      <h2>AI 助手</h2>
      <div class="ai-tabs">
        <button 
          @click="activeTab = 'summary'"
          :class="['tab-btn', { active: activeTab === 'summary' }]"
        >
          总结
        </button>
        <button 
          @click="activeTab = 'qa'"
          :class="['tab-btn', { active: activeTab === 'qa' }]"
        >
          问答
        </button>
      </div>
    </div>
    
    <!-- 总结功能 -->
    <div v-if="activeTab === 'summary'" class="ai-content">
      <div class="ai-section">
        <button 
          @click="summarizeNote"
          :disabled="!currentNote.content || isLoading"
          class="btn btn-primary full-width"
        >
          {{ isLoading ? '生成中...' : '生成总结' }}
        </button>
        
        <div v-if="summary" class="ai-result">
          <h4>总结结果：</h4>
          <div class="result-content">{{ summary }}</div>
        </div>
      </div>
    </div>
    
    <!-- 问答功能 -->
    <div v-if="activeTab === 'qa'" class="ai-content">
      <div class="ai-section">
        <div class="question-input">
          <textarea 
            v-model="question"
            class="textarea"
            placeholder="基于当前笔记内容提问..."
            rows="3"
          ></textarea>
          <button 
            @click="askQuestion"
            :disabled="!question.trim() || !currentNote.content || isLoading"
            class="btn btn-primary full-width"
          >
            {{ isLoading ? '思考中...' : '提问' }}
          </button>
        </div>
        
        <div v-if="answer" class="ai-result">
          <h4>AI 回答：</h4>
          <div class="result-content">{{ answer }}</div>
        </div>
      </div>
    </div>
    
    <!-- 历史记录 -->
    <div class="ai-history">
      <h4>历史记录</h4>
      <div class="history-list">
        <div 
          v-for="(item, index) in history" 
          :key="index"
          class="history-item"
        >
          <div class="history-type">{{ item.type === 'summary' ? '总结' : '问答' }}</div>
          <div class="history-content">{{ item.content }}</div>
          <div class="history-time">{{ formatTime(item.time) }}</div>
        </div>
        
        <div v-if="history.length === 0" class="empty-history">
          <p>暂无历史记录</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'AIAssistant',
  props: {
    currentNote: {
      type: Object,
      default: () => ({ id: null, title: '', content: '' })
    }
  },
  data() {
    return {
      activeTab: 'summary',
      isLoading: false,
      summary: '',
      question: '',
      answer: '',
      history: []
    }
  },
  methods: {
    async summarizeNote() {
      if (!this.currentNote.content) return
      
      this.isLoading = true
      try {
        const response = await axios.post('/api/ai/summarize', {
          content: this.currentNote.content
        })
        this.summary = response.data.summary
        
        // 添加到历史记录
        this.history.unshift({
          type: 'summary',
          content: this.summary,
          time: new Date()
        })
        
        // 限制历史记录数量
        if (this.history.length > 10) {
          this.history = this.history.slice(0, 10)
        }
      } catch (error) {
        console.error('生成总结失败:', error)
        alert('生成总结失败，请检查网络连接或API配置')
      } finally {
        this.isLoading = false
      }
    },
    
    async askQuestion() {
      if (!this.question.trim() || !this.currentNote.content) return
      
      this.isLoading = true
      try {
        const response = await axios.post('/api/ai/question', {
          question: this.question,
          context: this.currentNote.content
        })
        this.answer = response.data.answer
        
        // 添加到历史记录
        this.history.unshift({
          type: 'qa',
          content: `Q: ${this.question}\nA: ${this.answer}`,
          time: new Date()
        })
        
        // 限制历史记录数量
        if (this.history.length > 10) {
          this.history = this.history.slice(0, 10)
        }
        
        this.question = '' // 清空问题输入
      } catch (error) {
        console.error('提问失败:', error)
        alert('提问失败，请检查网络连接或API配置')
      } finally {
        this.isLoading = false
      }
    },
    
    formatTime(time) {
      return time.toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  },
  watch: {
    currentNote() {
      // 切换笔记时清空结果
      this.summary = ''
      this.answer = ''
      this.question = ''
    }
  }
}
</script>

<style scoped>
.ai-assistant {
  height: 100%;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.ai-header {
  margin-bottom: 20px;
}

.ai-header h2 {
  color: white;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 15px;
}

.ai-tabs {
  display: flex;
  gap: 5px;
}

.tab-btn {
  flex: 1;
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
}

.tab-btn.active {
  background: rgba(74, 144, 226, 0.8);
  color: white;
}

.ai-content {
  flex: 1;
  margin-bottom: 20px;
}

.ai-section {
  margin-bottom: 20px;
}

.full-width {
  width: 100%;
  margin-bottom: 15px;
}

.question-input {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ai-result {
  margin-top: 15px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.ai-result h4 {
  color: white;
  font-size: 14px;
  margin-bottom: 10px;
  font-weight: 600;
}

.result-content {
  color: rgba(255, 255, 255, 0.9);
  font-size: 13px;
  line-height: 1.5;
  white-space: pre-wrap;
}

.ai-history {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 15px;
}

.ai-history h4 {
  color: white;
  font-size: 14px;
  margin-bottom: 10px;
  font-weight: 600;
}

.history-list {
  max-height: 200px;
  overflow-y: auto;
}

.history-item {
  padding: 10px;
  margin-bottom: 8px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.history-type {
  color: rgba(74, 144, 226, 0.9);
  font-size: 11px;
  font-weight: 600;
  margin-bottom: 5px;
}

.history-content {
  color: rgba(255, 255, 255, 0.8);
  font-size: 12px;
  line-height: 1.4;
  margin-bottom: 5px;
  max-height: 60px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.history-time {
  color: rgba(255, 255, 255, 0.5);
  font-size: 10px;
}

.empty-history {
  text-align: center;
  color: rgba(255, 255, 255, 0.6);
  padding: 20px;
  font-size: 12px;
}
</style>