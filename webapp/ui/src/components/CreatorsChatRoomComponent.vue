<template>
    <div class="common-layout full-page-chat creators-chat-room">
        <el-container v-if="isPageVisible">
            <el-aside width="250px">
                <el-header>
                    <a href="/">
                        <img src="/logo.png" alt="TalkTo">
                        <h1>TalkTo</h1>
                    </a>
                </el-header>
                <el-row class="creator-list">
                    <el-col :span="24">
                        <h2>Clients</h2>
                    </el-col>
                    <el-col :span="24">
                        <el-input
                            v-model="clientsFilter"
                            placeholder="Search clients"
                            :prefix-icon="Search"
                            clearable
                            @input="filterClients" 
                            class="creator-filter-input"
                        ></el-input>
                        <el-scrollbar>
                            <el-row>
                                <el-col :span="24" v-for="client in filteredClients" :key="client.chat_room_id" class="sidebar-creator-row" :class="{ active: client.chat_room_id === chatRoomId }" @click="goToClientChatPage(client.chat_room_id)">
                                    <div class="creator-row">
                                        <div>
                                            <h3>{{ client.full_name }}</h3>
                                            <p>{{ client.email }}</p>
                                        </div>
                                    </div>
                                </el-col>
                            </el-row>
                        </el-scrollbar>
                    </el-col>
                </el-row>
            </el-aside>
            <el-container>
              <el-header class="chat-room-main-header">
                Chat Room <span v-if="activeClients">- {{ activeClients.full_name }}</span>
              </el-header>
              <el-main>
                <div class="conversation-container" v-if="chatRoomMapping">
                  <el-scrollbar class="conversation-messages" ref="chatScrollbar">
                      <div v-for="(message, index) in conversationHistory" :key="index" class="conversation-message" :class="message.role">
                          <div>
                              <div>
                                  <div v-if="activeClients && message.role === 'user'" class="post-creator-details">
                                      <span class="name">{{ activeClients.full_name }}</span>
                                  </div>
                                  <div class="conversation" :class="message.role">
                                      <div v-html="formattedMessage(message.content)"></div>
                                      <div class="timestamp" v-if="message.timestamp">
                                          {{ new Date(message.timestamp).toLocaleString() }}
                                      </div>
                                  </div>
                              </div>
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
                  <div class="input-container" v-if="chatRoomMapping && chatRoomMapping.is_creator_overtaken === 1">
                    <el-input type="textarea" placeholder="Type a message" v-model="message" @keyup="handleKeyup" class="chat-input-textbox"></el-input>

                    <el-button @mousedown="startVoiceInput" @mouseup="stopVoiceInput" link class="microphone-button" :class="activeClass" :style="{ bottom: recognizing ? '15px' : '26px' }">
                        <i class="fa fa-microphone"></i>
                        <span v-if="recognizing" class="timer">
                            {{ formattedTime }}
                            <img src="/audio-wave-n.gif" alt="" style="height: 30px;vertical-align: middle;">
                        </span>
                    </el-button>
                  </div>
                  <div class="input-container" v-else>
                    <el-alert title="This chat is currently managed by AI." type="warning" center show-icon :closable="false" />
                  </div>

                </div>  
              </el-main>
            </el-container>
        </el-container>
        <el-container v-else>
            <el-row>
                <el-col :span="24">
                    <el-alert
                        title="Error"
                        type="error"
                        description="An error occurred while loading the page. Please try again later."
                        show-icon
                    ></el-alert>
                </el-col>
            </el-row>
        </el-container>
    </div>
</template>

<script setup>
import { Search } from '@element-plus/icons-vue';
</script>

<script>
import axios from 'axios';
import { Select, Search } from '@element-plus/icons-vue';

export default {
  data() {
    return {
      isPageVisible: false,
      message: '',
      conversationHistory: [],
      isRequsetInProgress: false,
      userEmail: '',
      recognition: null,
      recognizing: false,
      activeClass: 'inactive',
      timer: null,
      elapsedTime: 0,
      clients: [],
      activeClients: null,
      clientsFilter: '',
      filteredClients: [],
      chatRoomId: null,
      chatRoomMapping: null,
    };
  },
  components: {
    Select,
    Search
  },
  mounted() {
    this.userEmail = localStorage.getItem('email');
    if (!this.userEmail) {
      location.reload();
    }

    this.chatRoomId = parseInt(this.$route.params.chatRoomId);

    this.getClients();
    if (this.chatRoomId) {
      this.fetchData();
    }

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
    goToClientChatPage(chat_room_id) {
        window.location.href = `/creators/chat-room/${chat_room_id}`;
    },
    getClients() {
      const apiUrl = this.baseUrlForApiCall + 'get_clients';
      axios.get(apiUrl, {
        params: {
          userEmail: this.userEmail,
          token: localStorage.getItem('token'),
        },
        headers: {
          "Authorization": null,
          'Content-Type': 'application/json'
        }
      })
      .then(response => {
            this.clients = response.data;
            this.filteredClients = this.clients;

            // Active creator is the creator whose username matches the advisorPersonalityName
            if (this.clients.length > 0 && this.chatRoomId) {
                this.activeClients = this.clients.find(client => client.chat_room_id === this.chatRoomId);
            }

            this.isPageVisible = true;
        })
        .catch(error => {
          console.log(error);
          this.isPageVisible = false;
        });
    },
    filterClients() {
      if (this.clientsFilter) {
        this.filteredClients = this.clients.filter(creator =>
          creator.full_name.toLowerCase().includes(this.clientsFilter.toLowerCase()) ||
          creator.username.toLowerCase().includes(this.clientsFilter.toLowerCase()) || 
          creator.education.toLowerCase().includes(this.clientsFilter.toLowerCase()) || 
          creator.location.toLowerCase().includes(this.clientsFilter.toLowerCase()) || 
          creator.occupation.toLowerCase().includes(this.clientsFilter.toLowerCase())
        );
      } else {
        this.filteredClients = this.clients;
      }
    },
    fetchData() {
      const apiUrl = this.baseUrlForApiCall + 'get_client_conversation';
      const self = this;
      axios.get(apiUrl, {
        params: {
          userEmail: this.userEmail,
          token: localStorage.getItem('token'),
          chatRoomId: this.chatRoomId
        },
        headers: {
          "Authorization": null,
          'Content-Type': 'application/json'
        }
      })
      .then((response) => {
        console.log(response);
        this.conversationHistory = response.data.conversation;   
        this.chatRoomMapping = response.data.mapping;
        
        // scroll to bottom after 5 seconds
        setTimeout(() => {
          self.scrollToBottom();
        }, 1000);
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
        role: 'user',
        timestamp: new Date().toISOString()
      });

      this.scrollToBottom();

      const apiUrl = this.baseUrlForApiCall + 'chat_incoming_message';
      axios.post(apiUrl, {
        message: message,
        userEmail: this.userEmail,
        token: localStorage.getItem('token'),
        advisorPersonalityName: this.advisorPersonalityName,
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
          role: 'assistant',
          timestamp: new Date().toISOString()
        });

        this.scrollToBottom();
      })
      .catch((error) => {
        console.log(error);
        this.isRequsetInProgress = false;
      });
    },
    scrollToBottom() {
      this.$nextTick(() => {
        const chatScrollbar = this.$refs.chatScrollbar;
        if (chatScrollbar) {
          const chatMessages = this.$el.querySelector('.conversation-container');
          if (chatMessages && chatMessages.scrollHeight > 0) {
            const scrollHeight = chatMessages.scrollHeight * 99999;
            chatScrollbar.setScrollTop(scrollHeight);
          }
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
.common-layout.full-page-chat .conversation-container .el-scrollbar__wrap {
    display: flex;
    flex-direction: column-reverse;
}

.common-layout.full-page-chat.creators-chat-room {
  color: #000;
}
.common-layout.full-page-chat.creators-chat-room aside.el-aside,
.common-layout.full-page-chat.creators-chat-room .input-container textarea,
.common-layout.full-page-chat.creators-chat-room .creator-filter-input .el-input__wrapper,
header.el-header.chat-room-main-header {
    background-color: #f0f7ff;
    border-right: 1px solid #94b4d8;
    color: #000;
}
.common-layout.full-page-chat.creators-chat-room .sidebar-creator-row,
header.el-header.chat-room-main-header {
  border-bottom: 1px solid #94b4d8;
}
.common-layout.full-page-chat.creators-chat-room main.el-main {
  background-color: #fff;
}
.common-layout.full-page-chat.creators-chat-room .creator-filter-input .el-input__wrapper .el-input__inner,
.common-layout.full-page-chat.creators-chat-room .creator-filter-input .el-input__wrapper span.el-input__prefix, 
.common-layout.full-page-chat.creators-chat-room .creator-filter-input .el-input__wrapper span.el-input__suffix,
.common-layout.full-page-chat.creators-chat-room .microphone-button,
.common-layout.full-page-chat.creators-chat-room header > a,
.common-layout.full-page-chat.creators-chat-room .creator-row p,
.common-layout.full-page-chat.creators-chat-room .conversation-message .conversation .timestamp {
  color: #000;
}
.common-layout.full-page-chat.creators-chat-room .el-row.creator-list h2 {
  background-color: #94b4d8;
  border-color: #94b4d8;
}
.common-layout.full-page-chat.creators-chat-room .sidebar-creator-row:hover, 
.common-layout.full-page-chat.creators-chat-room .sidebar-creator-row.active {
  background-color: #94b4d8;
}
header.el-header.chat-room-main-header {
  text-align: center;
  font-size: 1.2rem;
}
.common-layout.full-page-chat.creators-chat-room .conversation.assistant {
    background: #f0f7ff;
    border-color: #94b4d8;
    float: right;
}
.common-layout.full-page-chat.creators-chat-room .conversation.user {
    background: #94b4d8;
    border-color: #94b4d8;
    float: left;
}
</style>