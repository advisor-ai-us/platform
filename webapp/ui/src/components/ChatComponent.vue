<template>
  <div class="chat-container" :class="{ minimized: isMinimized, bigger: isChatWindowBigger }">
    <div class="chat-header">
      <span>Chat</span>

      <div class="chat-header-buttons">
        <el-button class="close-button" link @click="toggleChatSizeBigger" v-if="!isChatWindowBigger">
          <i class="fa fa-window-restore"></i>
        </el-button>
        <el-button class="close-button" link @click="toggleChatSizeBigger" v-if="isChatWindowBigger">
          <i class="fa fa-window-maximize"></i>
        </el-button>

        <el-button v-if="isMinimized" class="toggle-button" link @click="toggleChat">
          <i class="fa fa-window-maximize"></i>
        </el-button>
        <el-button v-else class="toggle-button" link @click="toggleChat">
          <i class="fa fa-window-minimize"></i>
        </el-button>
      </div>
    </div>
    <div class="chat-content" v-if="!isMinimized">
      <el-scrollbar class="chat-messages">
        <div class="chat-message" v-for="(message, index) in conversationHistory" :key="index" :class="message.role">
          <div class="message" :class="message.role">
            <el-popover placement="left" width="500" trigger="click" v-if="message.role === 'assistant'">
              <template #reference>
                  <el-button type="info" link :icon="Setting" style="float: right;"></el-button>
              </template>
              <el-row class="prompt-details">
                <el-collapse v-model="activePromptName" accordion>
                  <el-collapse-item title="System Prompt" name="1">
                    <p v-html="getPromptValue(message.prompt_details, 'system')"></p>
                  </el-collapse-item>
                  <el-collapse-item title="User" name="2">
                    <p v-html="getPromptValue(message.prompt_details, 'user')"></p>
                  </el-collapse-item>
                  <el-collapse-item title="Response from LLM" name="3">
                    <p v-html="getPromptValue(message.prompt_details, 'response')"></p>
                  </el-collapse-item>
                </el-collapse>
              </el-row>
            </el-popover>

            <div v-html="formattedMessage(message.content)"></div>
          </div>
        </div>
        <div class="chat-message assistant" v-if="isRequsetInProgress">
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
          placeholder="Type a message"
          v-model="message"
          @keyup="handleKeyup"
          class="chat-input-textbox"
        ></el-input>
        <el-button @mousedown="startVoiceInput" @mouseup="stopVoiceInput" link class="microphone-button" :class="activeClass" :style="{ bottom: recognizing ? '15px' : '26px' }">
          <i class="fa fa-microphone"></i>
          <span v-if="recognizing" class="timer">
            {{ formattedTime }}
            <img src="/audio-wave-n.gif" alt="" style="height: 30px;vertical-align: middle;">
          </span>
        </el-button>
        
      </div>
    </div>
  </div>
</template>

<script setup>
import { Setting } from '@element-plus/icons-vue';
</script>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      isChatVisible: true,
      isMinimized: true,
      isChatWindowBigger: false,
      message: '',
      conversationHistory: [],
      isRequsetInProgress: false,
      userEmail: '',
      recognition: null,
      recognizing: false,
      activeClass: 'inactive',
      timer: null,
      elapsedTime: 0,
      activePromptName: '1',
    };
  },
  props: {
    systemPrompt: {
      type: String,
      required: true,
    },
    advisorPersonalityName: {
      type: String,
      required: true,
    },
    stock: {
      type: String,
      required: false,
      default: '',
    },
  },
  mounted() {
    this.userEmail = localStorage.getItem('email');
    if (!this.userEmail) {
      location.reload();
    }

    this.fetchData();

    // Initialize Speech Recognition
    if ('webkitSpeechRecognition' in window) {
      this.recognition = new webkitSpeechRecognition();
      this.recognition.continuous = false; // Set to false to stop automatically after each result
      this.recognition.interimResults = false;
      this.recognition.lang = 'en-US';

      this.recognition.onstart = () => {
        this.recognizing = true;
      };

      this.recognition.onend = () => {
        this.recognizing = false;
        this.stopTimer();

        this.sendMessage();
      };

      this.recognition.onresult = (event) => {
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            this.message += event.results[i][0].transcript;
          }
        }
      };
    } else {
      console.warn('Speech recognition not supported in this browser.');
    }
  },
  methods: {
    toggleChat() {
      this.isMinimized = !this.isMinimized;

      if (this.isMinimized) {
        this.isChatWindowBigger = false;
      }

      const self = this;
      setTimeout(() => {
        console.log('scrollToBottom');
        self.scrollToBottom();
      }, 5000);
    },
    toggleChatSizeBigger() {
      this.isMinimized = false;
      this.isChatWindowBigger = !this.isChatWindowBigger;
    },
    fetchData() {
      const apiUrl = this.baseUrlForApiCall + 'get_conversation';
      axios.get(apiUrl, {
        params: {
          userEmail: this.userEmail,
          token: localStorage.getItem('token'),
          advisorPersonalityName: this.advisorPersonalityName
        },
        headers: {
          "Authorization": null,
          'Content-Type': 'application/json'
        }
      })
      .then((response) => {
        console.log(response);
        this.conversationHistory = response.data.conversation;
        this.dashboardData = response.data.dashboard;

        // Emit event to update dashboard boxes
        const eventName = "update-dashboard-boxes";
        this.emitter.emit(eventName, this.dashboardData);
        
        this.scrollToBottom();
      })
      .catch((error) => {
        console.log(error);
      });      
    },
    formattedMessage(message) {
      const profileCompletionMatch = message.match(/\(Profile Completion: (\d+)%\)/i);
      let profileCompletion = null;
      if (profileCompletionMatch) {
        profileCompletion = profileCompletionMatch[1];
        message = message.replace(profileCompletionMatch[0], "").trim();
      }

      if (profileCompletion) {
        message = message + `<br><br><div class="profile-completion">(Profile completion: ${profileCompletion}%)</div>`;
      }
      return message.replace(/\n/g, "<br>");
    },
    handleKeyup(event) {
      if (event.key === "Enter" && !event.shiftKey) {
        // If Enter is pressed without Shift, call sendMessage
        this.sendMessage();
        event.preventDefault(); // Prevents the default behavior of the Enter key
      } else if (event.key === "Enter" && event.shiftKey) {
        // use default behavior of Enter key
      }
    },
    sendMessage() {
      if(this.message === '') {
        return;
      }

      const message = this.message;
      this.message = '';
      this.isRequsetInProgress = true;
      this.conversationHistory.push({
        content: message,
        role: 'user'
      });

      const apiUrl = this.baseUrlForApiCall + 'chat_incoming_message';
      axios.post(apiUrl, {
        message: message,
        userEmail: this.userEmail,
        systemPrompt: this.systemPrompt,
        token: localStorage.getItem('token'),
        advisorPersonalityName: this.advisorPersonalityName,
        stock: this.stock,
      },
      {
        headers: {
          "Authorization": null,
          'Content-Type': 'application/json'
        }
      })
      .then((response) => {
        this.isRequsetInProgress = false;

        this.conversationHistory.push({
          content: response.data.response,
          prompt_details: response.data.prompt_details,
          role: 'assistant'
        });

        if(this.advisorPersonalityName === 'dashboard') {
          this.dashboardData = response.data.dashboard;
          const eventName = "update-dashboard-boxes";
          this.emitter.emit(eventName, this.dashboardData);
        } 
        else if(this.advisorPersonalityName === 'portfolio-performance') {
          const graphData = response.data.graph_data;
          const recommendations = response.data.recommendations;
          const assets = response.data.assets;

          const eventName = "update-analysis-page";
          this.emitter.emit(eventName, { graphData, recommendations, assets });
        }
        else if(this.advisorPersonalityName === 'stock-picker-discussion') {
          if(response.data.reportRow) {
            const reportRow = response.data.reportRow;

            const eventName = "update-stock-report";
            this.emitter.emit(eventName, { reportRow });
          }
        }
        else if(this.advisorPersonalityName === 'mental-health-advisor') {
          if(response.data.phq9Data) {
            const phq9Data = response.data.phq9Data;
            const eventName = "update-mental-health-page";
            this.emitter.emit(eventName, { phq9Data });
          }
        }

        this.scrollToBottom();
      })
      .catch((error) => {
        console.log(error);
        this.isRequsetInProgress = false;
      });
    },
    scrollToBottom() {
      // this.$nextTick(() => {
      //   const chatMessages = this.$el.querySelector('.chat-messages');
      //   if (chatMessages) {
      //     chatMessages.scrollTop = chatMessages.scrollHeight;
      //     console.log('scrollToBottom', chatMessages.scrollHeight);
      //   }
      // });
    },
    startVoiceInput() {
      if (!this.recognizing) {
        this.activeClass = 'active';
        this.startTimer();
        this.recognition.start();
      }
    },
    stopVoiceInput() {
      if (this.recognizing) {
        this.activeClass = 'inactive';
        this.recognition.stop();
        this.stopTimer();
      }
    },
    startTimer() {
      this.elapsedTime = 0;
      this.timer = setInterval(() => {
        this.elapsedTime++;
      }, 1000);
    },
    stopTimer() {
      clearInterval(this.timer);
      this.timer = null;
    },
    getPromptValue(promptDetails, role) {
      if (!promptDetails) {
        return '';
      }
      
      try {
        promptDetails = JSON.parse(promptDetails);
        const prompt = promptDetails.find((item) => item.role === role);
        
        if (!prompt || !prompt.content) {
          return '';
        }

        return prompt.content.replace(/\n/g, "<br>");
      } catch (error) {
        return '';
      }
    }
  },
  computed: {
    formattedTime() {
      const minutes = Math.floor(this.elapsedTime / 60);
      const seconds = this.elapsedTime % 60;
      return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
    }
  }
};
</script>

<style>
.microphone-button {
  position: absolute;
  /* bottom: 15px; */
  left: 8px;
}
.el-textarea.chat-input-textbox textarea.el-textarea__inner {
  padding-left: 26px;
}
button.el-button.is-link.microphone-button.active {
  color: #ff0000;
}
.timer {
    margin-left: 5px;
    font-size: 14px;
    color: #000;
    background: #fff;
    padding: 0 8px;
}
.el-row.prompt-details {
    max-height: 90vh;
    overflow-y: auto;
}
</style>