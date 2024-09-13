<template>
    <div class="improve-prompt-chat">
      <div class="conversation-container">
        <div v-if="conversationHistory.length === 0" class="empty-chat-message">
            <i class="el-icon-chat-dot-square"></i>
            <span>Say Hi 👋</span>
        </div>
        <el-scrollbar class="conversation-messages" ref="chatScrollbar">
          <div v-for="(message, index) in conversationHistory" :key="index" class="conversation-message" :class="message.role">
            <div class="message">
              <div v-html="formattedMessage(message.content)"></div>
              <div class="timestamp" v-if="message.timestamp">
                {{ new Date(message.timestamp).toLocaleString() }}
              </div>
            </div>
          </div>
          <div class="chat-message assistant" v-if="isRequestInProgress">
            <div class="message assistant">
              <div class="typing-indicator">
                <div class="dot-pulse"></div>
              </div>
            </div>
          </div>
        </el-scrollbar>
        <div class="input-container">
          <el-input
            type="textarea"
            placeholder="Type a message to improve your prompt"
            v-model="message"
            @keyup="handleKeyup"
            class="chat-input-textbox" 
            autosize
          ></el-input>
          <!-- <el-button @click="sendMessage" type="primary" :loading="isRequestInProgress">Send</el-button> -->
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        message: '',
        conversationHistory: [],
        isRequestInProgress: false,
        userEmail: '',
      };
    },
    mounted() {
      this.userEmail = localStorage.getItem('email');
      if (!this.userEmail) {
        this.$router.push({ name: 'LoginPage' });
      }
      this.fetchConversation();
    },
    methods: {
      fetchConversation() {
        const apiUrl = this.baseUrlForApiCall + 'get_conversation';
        const self = this;
        axios.get(apiUrl, {
          params: {
            userEmail: this.userEmail,
            token: localStorage.getItem('token'),
            advisorPersonalityName: 'improve-prompt',
          },
        })
        .then((response) => {
          this.conversationHistory = response.data.conversation;
          setTimeout(() => {
            self.scrollToBottom();
          }, 1000);
        })
        .catch((error) => {
          console.error('Error fetching conversation:', error);
        });
      },
      formattedMessage(message) {
        return message.replace(/\n/g, "<br>");
      },
      handleKeyup(event) {
        if (event.key === "Enter" && !event.shiftKey) {
          this.sendMessage();
          event.preventDefault();
        }
      },
      sendMessage() {
        if (this.message.trim() === '') {
          return;
        }
  
        const message = this.message;
        this.message = '';
        this.isRequestInProgress = true;
        this.conversationHistory.push({
          content: message,
          role: 'user',
          timestamp: new Date().toISOString()
        });
  
        this.scrollToBottom();
  
        const apiUrl = this.baseUrlForApiCall + 'chat_incoming_message';
        axios.post(apiUrl, {
          message: message,
          userEmail: this.userEmail,
          token: localStorage.getItem('token'),
          advisorPersonalityName: 'improve-prompt',
        })
        .then((response) => {
          this.isRequestInProgress = false;
          this.conversationHistory.push({
            content: response.data.response,
            role: 'assistant',
            timestamp: new Date().toISOString()
          });
          this.scrollToBottom();
        })
        .catch((error) => {
          console.error('Error sending message:', error);
          this.isRequestInProgress = false;
        });
      },
      scrollToBottom() {
        this.$nextTick(() => {
          const chatScrollbar = this.$refs.chatScrollbar;
          if (chatScrollbar) {
            const scrollHeight = chatScrollbar.$el.scrollHeight * 99999;
            chatScrollbar.setScrollTop(scrollHeight);
          }
        });
      },
    },
  };
  </script>
  
  <style>
  .improve-prompt-chat {
    height: 500px;
    display: flex;
    flex-direction: column;
  }
  .improve-prompt-chat .conversation-container {
    height: 100%;
    display: flex;
    flex-direction: column;
  }
  .improve-prompt-chat .conversation-messages {
    flex: 1;
    overflow-y: auto;
    padding: 10px;
  }
  .improve-prompt-chat .conversation-message {
    margin-bottom: 10px;
  }
  .improve-prompt-chat .message {
    padding: 10px;
    border-radius: 5px;
    max-width: 80%;
  }
  .improve-prompt-chat .user .message {
    background-color: #e6f7ff;
    margin-left: auto;
  }
  .improve-prompt-chat .assistant .message {
    background-color: #f0f0f0;
  }
  .improve-prompt-chat .timestamp {
    font-size: 0.8em;
    color: #888;
    margin-top: 5px;
    text-align: right;
  }
  .improve-prompt-chat {
    font-size: 0.8rem;
}
.improve-prompt-chat .input-container {
    display: flex;
    padding: 10px;
  }
  .improve-prompt-chat .chat-input-textbox {
    flex: 1;
    margin-right: 10px;
  }
  .improve-prompt-chat .typing-indicator {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 20px;
  }
  
  .improve-prompt-chat .dot-pulse {
    position: relative;
    left: -9999px;
    width: 10px;
    height: 10px;
    border-radius: 5px;
    background-color: #9880ff;
    color: #9880ff;
    box-shadow: 9999px 0 0 -5px;
    animation: dot-pulse 1.5s infinite linear;
    animation-delay: 0.25s;
  }
  
  .improve-prompt-chat .dot-pulse::before, .dot-pulse::after {
    content: '';
    display: inline-block;
    position: absolute;
    top: 0;
    width: 10px;
    height: 10px;
    border-radius: 5px;
    background-color: #9880ff;
    color: #9880ff;
  }
  
  .improve-prompt-chat .dot-pulse::before {
    box-shadow: 9984px 0 0 -5px;
    animation: dot-pulse-before 1.5s infinite linear;
    animation-delay: 0s;
  }
  
  .improve-prompt-chat .dot-pulse::after {
    box-shadow: 10014px 0 0 -5px;
    animation: dot-pulse-after 1.5s infinite linear;
    animation-delay: 0.5s;
  }
  
  @keyframes dot-pulse-before {
    0% { box-shadow: 9984px 0 0 -5px; }
    30% { box-shadow: 9984px 0 0 2px; }
    60%, 100% { box-shadow: 9984px 0 0 -5px; }
  }
  
  @keyframes dot-pulse {
    0% { box-shadow: 9999px 0 0 -5px; }
    30% { box-shadow: 9999px 0 0 2px; }
    60%, 100% { box-shadow: 9999px 0 0 -5px; }
  }
  
  @keyframes dot-pulse-after {
    0% { box-shadow: 10014px 0 0 -5px; }
    30% { box-shadow: 10014px 0 0 2px; }
    60%, 100% { box-shadow: 10014px 0 0 -5px; }
  }
  .improve-prompt-chat .el-textarea.chat-input-textbox textarea.el-textarea__inner {
    padding-left: 11px;
}

.empty-chat-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
  font-size: 2rem;
}

.empty-chat-message i {
  font-size: 3rem;
  margin-bottom: 10px;
}
  </style>