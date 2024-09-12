<template>
    <div class="common-layout full-page-chat">
        <el-container>
            <!-- <el-header><a href="/">
                <img src="/logo.png" alt="Advisor AI Logo"></a>
            </el-header> -->
            
            <el-aside width="250px">
                <el-header>
                    <a href="/">
                        <img src="/logo.png" alt="TalkTo">
                        <h1>TalkTo</h1>
                    </a>
                </el-header>
                <el-row class="creator-list">
                    <el-col :span="24">
                        <h2>Creators</h2>
                    </el-col>
                    <el-col :span="24">
                        <el-input
                            v-model="creatorFilter"
                            placeholder="Search creators"
                            :prefix-icon="Search"
                            clearable
                            @input="filterCreators" 
                            class="creator-filter-input"
                        ></el-input>
                        <el-scrollbar>
                            <el-row>
                                <el-col :span="24" v-for="creator in filteredCreators" :key="creator.id" class="sidebar-creator-row" :class="{ active: creator.username === advisorPersonalityName }" @click="goToCreatorPage(creator.username)">
                                    <div class="creator-row">
                                        <div>
                                            <el-image style="width: 40px; height: 40px" :src="'data:image/png;base64,' + creator.profile_photo" fit="cover"></el-image>
                                        </div>
                                        <div>
                                            <h3>{{ creator.full_name }}</h3>
                                            <p>{{ creator.occupation }}</p>
                                        </div>
                                    </div>
                                </el-col>
                            </el-row>
                        </el-scrollbar>
                    </el-col>
                </el-row>
            </el-aside>
            <el-main>
                <div class="conversation-container">
                    <el-scrollbar class="conversation-messages" ref="chatScrollbar">
                        <div class="creator-profile" v-if="activeCreator">
                            <div class="creator-details">
                                <h3>{{ activeCreator.full_name }}</h3>
                                <p style="font-size: 0.8rem;">{{ activeCreator.occupation }}</p>
                                <p>@{{ activeCreator.username }}</p>
                            </div>

                            <el-image class="top-right-creator-photo" :src="'data:image/png;base64,' + activeCreator.profile_photo" fit="cover"></el-image>
                        </div>
                        <div v-for="(message, index) in conversationHistory" :key="index" class="conversation-message" :class="message.role">
                            <div>
                                <div class="creator-profile-left-post" v-if="activeCreator && message.role === 'assistant'">
                                    <el-image class="creator-photo-for-post" :src="'data:image/png;base64,' + activeCreator.profile_photo" fit="cover"></el-image>
                                </div>
                                <div>
                                    <div v-if="activeCreator && message.role === 'assistant'" class="post-creator-details">
                                        <span class="name">{{ activeCreator.full_name }}</span>
                                    </div>
                                    <div class="conversation" :class="message.role">
                                        <div v-html="formattedMessage(message.content)"></div>
                                        <div class="timestamp" v-if="message.timestamp">
                                            {{ new Date(message.timestamp).toLocaleString() }}
                                            <span class="read-icon" v-if="message.role === 'user'">
                                                <el-icon><Select /></el-icon>
                                                <el-icon><Select /></el-icon>
                                            </span>
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
                    <div class="input-container">
                        <el-input type="textarea" placeholder="Type a message" v-model="message" @keyup="handleKeyup" class="chat-input-textbox"></el-input>

                        <el-button @mousedown="startVoiceInput" @mouseup="stopVoiceInput" link class="microphone-button" :class="activeClass" :style="{ bottom: recognizing ? '15px' : '26px' }">
                            <i class="fa fa-microphone"></i>
                            <span v-if="recognizing" class="timer">
                                {{ formattedTime }}
                                <img src="/audio-wave-n.gif" alt="" style="height: 30px;vertical-align: middle;">
                            </span>
                        </el-button>
                    </div>
                </div>  

            </el-main>
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
      message: '',
      conversationHistory: [],
      isRequsetInProgress: false,
      userEmail: '',
      recognition: null,
      recognizing: false,
      activeClass: 'inactive',
      timer: null,
      elapsedTime: 0,
      creators: [],
      activeCreator: null,
      creatorFilter: '',
      filteredCreators: [],
    };
  },
  components: {
    Select,
    Search
  },
  props: {
    advisorPersonalityName: {
      type: String,
      required: true,
    },
  },
  mounted() {
    this.userEmail = localStorage.getItem('email');
    if (!this.userEmail) {
      location.reload();
    }

    this.getCreators();
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
    goToCreatorPage(username) {
        window.location.href = `/${username}`;
    },
    getCreators() {
      const apiUrl = this.baseUrlForApiCall + 'creators';
      axios.get(apiUrl)
        .then(response => {
            this.creators = response.data;
            this.filteredCreators = this.creators;

            // Active creator is the creator whose username matches the advisorPersonalityName
            if (this.creators.length > 0) {
                this.activeCreator = this.creators.find(creator => creator.username === this.advisorPersonalityName);
            }
        })
        .catch(error => {
          console.log(error);
        });
    },
    filterCreators() {
      if (this.creatorFilter) {
        this.filteredCreators = this.creators.filter(creator =>
          creator.full_name.toLowerCase().includes(this.creatorFilter.toLowerCase()) ||
          creator.username.toLowerCase().includes(this.creatorFilter.toLowerCase()) || 
          creator.education.toLowerCase().includes(this.creatorFilter.toLowerCase()) || 
          creator.location.toLowerCase().includes(this.creatorFilter.toLowerCase()) || 
          creator.occupation.toLowerCase().includes(this.creatorFilter.toLowerCase())
        );
      } else {
        this.filteredCreators = this.creators;
      }
    },
    fetchData() {
      const apiUrl = this.baseUrlForApiCall + 'get_conversation';
      const self = this;
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
          role: 'assistant'
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
</style>