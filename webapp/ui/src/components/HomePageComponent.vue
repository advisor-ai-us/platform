<template>
  <div class="homepage-container">
    <header>
      <img src="/logo.png" alt="Advisor AI Logo">
      <div class="auth-links">
        <el-button type="primary" @click="$router.push('/user/login')">Login</el-button>
        <el-button type="success" @click="$router.push('/user/waitlist')">Join Waitlist</el-button>
        <el-button type="warning" @click="$router.push('/join/creator')">Join as Creator</el-button>
        <el-button type="info" @click="$router.push('/membership/pricing')">Pricing</el-button>
      </div>
    </header>
    
    <div class="container">
      <div class="section">
        <div>
          <el-row class="center-content">
            <el-col :span="24">
              <h1 class="homepage-title">
                talkto.app/<VueTyper
                  :text="dynamicWords"
                  :repeat="Infinity"
                  initial-action="typing"
                  :start-delay="200"
                  :type-delay="100"
                  :erase-delay="1000"
                  :erase-speed="100"
                />
              </h1>
            </el-col>
          </el-row>
        </div>
        <div class="subtitle-container">
          <el-row class="center-content">
            <el-col :span="24">
              <div class="homepage-subtitle">
                <!-- <p style="line-height: 24px;">TalkTo is a platform that allows you to connect with the people you want to talk to.</p> -->
                <el-input
                  v-model="userInput"
                  @keyup.enter="handleEnterKey"
                  placeholder="Who do you want to talk to?"
                  class="user-input1"
                />
                <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
              </div>
            </el-col>
          </el-row>
        </div>
      </div>
    </div>
    <div class="container">
      <div class="section">
        <div>
          <el-row class="center-content">
            <el-col :span="24">
              <h1 class="homepage-title" style="text-align: center;height: auto;">Creators</h1>
            </el-col>
          </el-row>
          <el-row class="search-creators">
            <el-col :span="24">
              <el-input
                v-model="creatorFilter"
                placeholder="Search creators"
                :prefix-icon="Search"
                clearable
                @input="filterCreators" 
                class="search-creators-input"
              />
            </el-col>
          </el-row>
          <el-row class="creators-section">
            <div v-for="creator in filteredCreators" :key="creator.id" class="creator-card">
              <el-card>
                <div>
                    <el-image
                      style="width: 100px; height: 100px"
                      :src="'data:image/png;base64,' + creator.profile_photo"
                      fit="cover"
                    ></el-image>
                  
                    <h2>{{ creator.full_name }}</h2>
                    <p>@{{ creator.username }}</p>
                    <p>{{ creator.occupation }}</p>
                    <el-button type="primary" @click="$router.push(`/${creator.username}`)" size="small">Chat with {{ creator.full_name }}</el-button>
                </div>
              </el-card>
            </div>
          </el-row>

        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { Search } from '@element-plus/icons-vue';
</script>

<script>
import axios from "axios";
export default {
  data() {
    return {
      dynamicWords: ["celebrity", "influencer", "coach", "chhota-bheem", "doremon"],
      userInput: "",
      errorMessage: "",
      creators: [],
      creatorFilter: '',
      filteredCreators: [],
    };
  },
  mounted() {
    this.mfToGetCreator();
  },
  methods: {
    handleEnterKey() {
      // Check if the input contains spaces
      if (/\s/.test(this.userInput)) {
        this.errorMessage = "Input should not contain spaces.";
      } else if (this.userInput.trim() === "") {
        this.errorMessage = "Input cannot be empty.";
      } else {
        // No spaces, proceed to redirect
        this.errorMessage = "";
        this.$router.push(`/${this.userInput}`);
      }
    },
    mfToGetCreator() {
      const apiURL = this.baseUrlForApiCall + 'creators';
      axios.get(apiURL)
        .then(response => {
          this.creators = response.data;
          this.filteredCreators = this.creators;
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
  }
};
</script>

<style>
.homepage-container {
  /* display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center; */
  height: 100vh;
  background-color: #f5f5f5;
  display: block;
  overflow: hidden;
}
.container {
    max-width: 1200px;
    margin: 2em auto;
    padding: 2em;
    background: #fff;
    box-shadow: 0 2px 4px #0000001a;
    border-radius: 8px
}
.homepage-title {
    line-height: 30px;
    font-weight: bold;
    margin: 0 auto 20px auto;
    height: 60px;
    max-width: 475px;
    text-align: left;
}

.homepage-subtitle {
  font-size: 1.2em;
  color: #555;
  text-align: center;
}

.user-input {
  padding: 10px;
  font-size: 1em;
  margin-top: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.error {
  color: red;
  margin-top: 10px;
}

.center-content {
  text-align: center;
}
header img {
    max-height: 50px;
}

header .auth-links {
    float: right;
}

header {padding: 10px;}

.creator-card {
    text-align: center;
    margin: 10px;
}

.creator-card img.el-image__inner {
    border-radius: 50%;
    border: 1px solid #dcdfe6;
}

.creator-card h2 {
    margin: 0;
    font-size: 1rem;
}

.creator-card p {
    margin: 5px 0;
    color: #acafb4;
    font-size: 0.8rem;
}
</style>
