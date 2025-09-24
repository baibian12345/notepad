<template>
  <div class="settings-page">
    <div class="settings-container">
      <div class="settings-panel glass-panel">
        <div class="settings-header">
          <h1>应用设置</h1>
          <div class="nav-buttons">
            <router-link to="/" class="btn btn-secondary">
              📔 笔记
            </router-link>
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
          </div>
        </div>
        
        <div class="settings-content">
          <!-- AI API 设置 -->
          <div class="setting-section">
            <h3>AI 功能设置</h3>
            <div class="setting-item">
              <label for="apiKey">API Key:</label>
              <input 
                id="apiKey"
                v-model="settings.apiKey"
                type="password"
                class="input"
                placeholder="请输入您的AI API Key"
              />
              <small class="setting-help">
                用于AI总结和问答功能，支持OpenAI、Claude等API
              </small>
            </div>
            
            <div class="setting-item">
              <label for="apiUrl">API 地址:</label>
              <input 
                id="apiUrl"
                v-model="settings.apiUrl"
                type="url"
                class="input"
                placeholder="https://api.openai.com/v1"
              />
              <small class="setting-help">
                API服务地址，留空使用默认地址
              </small>
            </div>
            
            <div class="setting-item">
              <label for="model">AI 模型:</label>
              <select id="model" v-model="settings.model" class="input">
                <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                <option value="gpt-4">GPT-4</option>
                <option value="claude-3-sonnet">Claude 3 Sonnet</option>
                <option value="claude-3-haiku">Claude 3 Haiku</option>
              </select>
              <small class="setting-help">
                选择要使用的AI模型
              </small>
            </div>
          </div>
          
          <!-- 界面设置 -->
          <div class="setting-section">
            <h3>界面设置</h3>
            <div class="setting-item">
              <label for="fontSize">字体大小:</label>
              <select id="fontSize" v-model="settings.fontSize" class="input">
                <option value="small">小</option>
                <option value="medium">中</option>
                <option value="large">大</option>
              </select>
            </div>
            
            <div class="setting-item">
              <label>
                <input 
                  type="checkbox" 
                  v-model="settings.autoSave"
                  class="checkbox"
                />
                自动保存
              </label>
              <small class="setting-help">
                编辑时自动保存笔记内容
              </small>
            </div>
            
            <div class="setting-item">
              <label>
                <input 
                  type="checkbox" 
                  v-model="settings.showPreview"
                  class="checkbox"
                />
                显示预览
              </label>
              <small class="setting-help">
                在笔记列表中显示内容预览
              </small>
            </div>
          </div>
          
          <!-- 数据管理 -->
          <div class="setting-section">
            <h3>数据管理</h3>
            <div class="setting-actions">
              <button @click="exportData" class="btn btn-primary">
                导出数据
              </button>
              <button @click="importData" class="btn btn-primary">
                导入数据
              </button>
              <button @click="clearData" class="btn btn-danger">
                清空所有数据
              </button>
            </div>
            <input 
              ref="fileInput"
              type="file"
              accept=".json"
              @change="handleFileImport"
              style="display: none;"
            />
          </div>
        </div>
        
        <div class="settings-footer">
          <button @click="saveSettings" class="btn btn-primary">
            保存设置
          </button>
          <button @click="resetSettings" class="btn">
            重置为默认
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'SettingsPage',
  data() {
    return {
      settings: {
        apiKey: '',
        apiUrl: '',
        model: 'gpt-3.5-turbo',
        fontSize: 'medium',
        autoSave: true,
        showPreview: true
      }
    }
  },
  async mounted() {
    await this.loadSettings()
  },
  methods: {
    async loadSettings() {
      try {
        const response = await axios.get('/api/settings')
        this.settings = { ...this.settings, ...response.data }
      } catch (error) {
        console.error('加载设置失败:', error)
      }
    },
    
    async saveSettings() {
      try {
        for (const [key, value] of Object.entries(this.settings)) {
          await axios.post('/api/settings', { key, value })
        }
        alert('设置保存成功！')
      } catch (error) {
        console.error('保存设置失败:', error)
        alert('保存设置失败，请重试')
      }
    },
    
    resetSettings() {
      if (confirm('确定要重置所有设置为默认值吗？')) {
        this.settings = {
          apiKey: '',
          apiUrl: '',
          model: 'gpt-3.5-turbo',
          fontSize: 'medium',
          autoSave: true,
          showPreview: true
        }
      }
    },
    
    async exportData() {
      try {
        const response = await axios.get('/api/notes')
        const data = {
          notes: response.data,
          settings: this.settings,
          exportTime: new Date().toISOString()
        }
        
        const blob = new Blob([JSON.stringify(data, null, 2)], {
          type: 'application/json'
        })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `labubu-notes-${new Date().toISOString().split('T')[0]}.json`
        a.click()
        URL.revokeObjectURL(url)
      } catch (error) {
        console.error('导出数据失败:', error)
        alert('导出数据失败，请重试')
      }
    },
    
    importData() {
      this.$refs.fileInput.click()
    },
    
    async handleFileImport(event) {
      const file = event.target.files[0]
      if (!file) return
      
      try {
        const text = await file.text()
        const data = JSON.parse(text)
        
        if (confirm('导入数据将覆盖现有数据，确定继续吗？')) {
          // 这里需要实现导入逻辑
          console.log('导入的数据:', data)
          alert('数据导入功能正在开发中')
        }
      } catch (error) {
        console.error('导入数据失败:', error)
        alert('导入数据失败，请检查文件格式')
      }
    },
    
    async clearData() {
      if (confirm('确定要清空所有笔记数据吗？此操作不可恢复！')) {
        if (confirm('请再次确认：真的要删除所有数据吗？')) {
          try {
            // 这里需要实现清空数据的API
            alert('清空数据功能正在开发中')
          } catch (error) {
            console.error('清空数据失败:', error)
            alert('清空数据失败，请重试')
          }
        }
      }
    }
  }
}
</script>

<style scoped>
.settings-page {
  height: 100vh;
  padding: 40px 20px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.settings-container {
  width: 100%;
  max-width: 800px;
}

.settings-panel {
  padding: 30px;
}

.settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.settings-header h1 {
  color: white;
  font-size: 28px;
  font-weight: 700;
  margin: 0;
}

.settings-content {
  margin-bottom: 30px;
}

.setting-section {
  margin-bottom: 30px;
}

.setting-section h3 {
  color: white;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.setting-item {
  margin-bottom: 20px;
}

.setting-item label {
  display: block;
  color: white;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
}

.setting-item label input[type="checkbox"] {
  margin-right: 8px;
}

.setting-help {
  display: block;
  color: rgba(255, 255, 255, 0.6);
  font-size: 12px;
  margin-top: 5px;
  line-height: 1.4;
}

.checkbox {
  width: auto !important;
  margin-right: 8px;
}

.setting-actions {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.settings-footer {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

/* 响应式设计 */
@media (max-width: 600px) {
  .settings-page {
    padding: 20px 10px;
  }
  
  .settings-panel {
    padding: 20px;
  }
  
  .settings-header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
  
  .nav-buttons {
    display: flex;
    gap: 10px;
  }
  
  .nav-buttons .btn {
    font-size: 0.9rem;
    padding: 8px 16px;
  }
  
  .setting-actions {
    flex-direction: column;
  }
  
  .settings-footer {
    flex-direction: column;
  }
}
</style>