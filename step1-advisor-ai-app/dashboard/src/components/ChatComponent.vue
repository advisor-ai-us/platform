<template>
  <div class="chat-container" :class="{ minimized: isMinimized }">
    <div class="chat-header" @click="toggleChat">
      <span>Chat</span>
      <el-button v-if="isMinimized" class="toggle-button" link>
        <i class="fa fa-window-maximize"></i>
      </el-button>
      <el-button v-else class="toggle-button" link>
        <i class="fa fa-window-minimize"></i>
      </el-button>
    </div>
    <div class="chat-content" v-if="!isMinimized">
      <el-scrollbar class="chat-messages">
        <div class="chat-message" v-for="(message, index) in conversationHistory" :key="index" :class="message.role">
          <div class="message" :class="message.role">
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

<script>
import axios from 'axios';

export default {
  data() {
    return {
      isChatVisible: true,
      isMinimized: true,
      message: '',
      conversationHistory: [],
      isRequsetInProgress: false,
      userEmail: '',
      recognition: null,
      recognizing: false,
      activeClass: 'inactive',
      timer: null,
      elapsedTime: 0,
    };
  },
  props: {
    systemPrompt: {
      type: String,
      required: true,
    },
    pageName: {
      type: String,
      required: true,
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

      const self = this;
      setTimeout(() => {
        console.log('scrollToBottom');
        self.scrollToBottom();
      }, 5000);
    },
    fetchData() {
      const apiUrl = this.baseUrlForApiCall + 'get_conversation';
      axios.get(apiUrl, {
        params: {
          userEmail: this.userEmail,
          token: localStorage.getItem('token'),
          display_on_page: this.pageName
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

      const apiUrl = this.baseUrlForApiCall + 'ai_request';
      axios.post(apiUrl, {
        message: message,
        userEmail: this.userEmail,
        systemPrompt: this.systemPrompt,
        token: localStorage.getItem('token'),
        display_on_page: this.pageName
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
          role: 'assistant'
        });

        if(this.pageName === 'dashboard') {
          this.dashboardData = response.data.dashboard;
          const eventName = "update-dashboard-boxes";
          this.emitter.emit(eventName, this.dashboardData);
        } 
        else if(this.pageName === 'investment-guru') {
          const graphData = response.data.graph_data;
          const recommendations = response.data.recommendations;
          const assets = response.data.assets;

          const eventName = "update-analysis-page";
          this.emitter.emit(eventName, { graphData, recommendations, assets });
        }

        this.scrollToBottom();
      })
      .catch((error) => {
        console.log(error);
        this.isRequsetInProgress = false;
      });
    },
    scrollToBottom() {
      this.$nextTick(() => {
        const chatMessages = this.$el.querySelector('.chat-messages');
        if (chatMessages) {
          chatMessages.scrollTop = chatMessages.scrollHeight;
          console.log('scrollToBottom', chatMessages.scrollHeight);
        }
        
      });
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
</style>