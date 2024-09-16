<template>
  <div class="homepage-container">
    <header class="header">
      <div class="header-content">
        <div class="logo-title">
          <img src="/logo.png" alt="TalkTo Logo" class="logo">
          <h1 class="site-title">TalkTo</h1>
        </div>
        <nav class="nav-links" v-if="!loggedInUser">
          <el-button type="primary" @click="$router.push('/user/login')">Login</el-button>
          <el-button type="success" @click="$router.push('/user/waitlist')">Join Waitlist</el-button>
          <el-button type="warning" @click="$router.push('/join/creator')">Join as Creator</el-button>
          <el-button type="info" @click="$router.push('/membership/pricing')">Pricing</el-button>
        </nav>
        <div class="user-info" v-if="loggedInUser">
          <span>Welcome, {{ loggedInUser.fullName }}</span>
          <el-button type="warning" @click="$router.push('/creator/edit')" v-if="loggedInUser.role === 'creator'">Edit Profile</el-button>
          <el-button type="danger" @click="mfToLogout">Logout</el-button>
        </div>
      </div>
    </header>

    <main class="main-content">
      <section class="hero">
        <div class="hero-content">
          <h1 class="hero-title">Experience Unique Conversations</h1>
          <p class="hero-subtitle">Connect with virtual personalities crafted by real creators</p>
          <el-button type="primary" size="large" @click="scrollToFeaturedPersonalities">Start Exploring</el-button>
        </div>
      </section>

      <section class="features">
        <div class="feature">
          <i class="el-icon-chat-dot-round"></i>
          <h3>Engaging Chats</h3>
          <p>Interact with diverse virtual personas</p>
        </div>
        <div class="feature">
          <i class="el-icon-user"></i>
          <h3>Unique Personalities</h3>
          <p>Explore a wide range of characters</p>
        </div>
        <div class="feature">
          <i class="el-icon-magic-stick"></i>
          <h3>Tailored Experiences</h3>
          <p>Every conversation is one-of-a-kind</p>
        </div>
      </section>

      <section id="featured-personalities" class="creators">
        <h2 class="section-title">Featured Personalities</h2>
        <el-input
          v-model="creatorFilter"
          placeholder="Search creators"
          :prefix-icon="Search"
          clearable
          @input="filterCreators" 
          class="search-creators-input"
        />
        <div class="creators-grid">
          <el-card v-for="creator in filteredCreators" :key="creator.id" class="creator-card">
            <el-image
              :src="'data:image/png;base64,' + creator.profile_photo"
              fit="cover"
              class="creator-image"
            ></el-image>
            <h3>{{ creator.full_name }}</h3>
            <p class="creator-username">@{{ creator.username }}</p>
            <p class="creator-occupation">{{ creator.occupation }}</p>
            <p class="known-language">
              Speaks: 
              <el-tag v-for="language in creator.languages" :key="language" size="small" type="primary" style="margin: 2px;">{{ language }}</el-tag>
            </p>
            <el-button type="primary" @click="$router.push(`/${creator.username}`)" size="small">Chat with {{ creator.full_name }}</el-button>
          </el-card>
        </div>
      </section>
    </main>

    <footer class="footer">
      <p>&copy; 2024 TalkTo AI. All rights reserved.</p>
    </footer>
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
      isLoggedIn: false,
      loggedInUser: null,
    };
  },
  mounted() {
    this.mfToGetCreator();
    
    const token = localStorage.getItem('token');
    if (token) {
      this.validateToken(token);
    }
  },
  methods: {
    validateToken(token) {
      axios.post(this.baseUrlForApiCall + 'validate_token', { token })
        .then((response) => {
          if (response.data.valid) {
            this.loggedInUser = response.data;
          } else {
            localStorage.removeItem('token');
          }
        })
        .catch((error) => {
          console.error(error);
          localStorage.removeItem('token');
        });        
    },
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
    mfToLogout() {
      localStorage.removeItem('token');
      this.loggedInUser = null;
      this.isLoggedIn = false;
      this.$router.push('/');
    },
    scrollToFeaturedPersonalities() {
      const featuredSection = document.getElementById('featured-personalities');
      if (featuredSection) {
        featuredSection.scrollIntoView({ behavior: 'smooth' });
      }
    }
  }
};
</script>

<style>
.homepage-container {
  font-family: Arial, sans-serif;
  color: #333;
  min-height: 100vh;
}
.homepage-container .header {
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 1rem;
}
.homepage-container .header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
}
.homepage-container .logo {
  height: 40px;
}
.homepage-container .nav-links button, .user-info button {
  margin-left: 1rem;
}
.homepage-container .main-content {
  max-width: 1200px;
  min-height: calc(100vh - 300px);
  margin: 0 auto;
  padding: 2rem 1rem;
}
.homepage-container .hero {
  text-align: center;
  margin-bottom: 4rem;
  background-color: #f0f7ff;
  border-radius: 10px;
  padding: 3rem;
}
.homepage-container .hero-content {
  max-width: 800px;
  margin: 0 auto;
}
.homepage-container .hero-title {
  font-size: 3rem;
  margin: 0 0 1rem 0;
  color: #1a1a1a;
  line-height: 50px;
}
.homepage-container .hero-subtitle {
  font-size: 1.2rem;
  color: #666;
  margin-bottom: 2rem;
}
.homepage-container .features {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4rem;
}
.homepage-container .feature {
  flex: 1;
  text-align: center;
  padding: 1.5rem;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  transition: transform 0.3s ease;
}
.homepage-container .feature:hover {
  transform: translateY(-10px);
}
.homepage-container .feature i {
  font-size: 3rem;
  color: #409EFF;
  margin-bottom: 1rem;
}
.homepage-container .feature h3 {
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
}
.homepage-container .feature p {
  font-size: 1rem;
  color: #666;
}
.homepage-container .section-title {
  font-size: 2rem;
  text-align: center;
  margin-bottom: 2rem;
}
.homepage-container .search-creators-input {
  max-width: 400px;
  margin: 0 auto 2rem;
  display: block;
}
.homepage-container .search-creators-input .el-input__wrapper {
    width: 100%;
}
.homepage-container .creators-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 2rem;
}
.homepage-container .creator-card {
  text-align: center;
}
.homepage-container .creator-image {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  margin-bottom: 1rem;
}
.homepage-container .creator-username {
  color: #666;
  margin: 4px 0;
  font-size: 0.9rem;
}
.homepage-container .creator-occupation {
  font-style: italic;
  margin: 0;
  font-size: 0.9rem;
}
.homepage-container p.known-language {
    margin: 8px 0;
    font-size: 0.9rem;
}
.homepage-container .footer {
  background-color: #f5f5f5;
  text-align: center;
  padding: 1rem;
  margin-top: 4rem;
}
.homepage-container .logo-title {
  display: flex;
  align-items: center;
}
.homepage-container .site-title {
  margin-left: 10px;
  font-size: 1.5rem;
  font-weight: bold;
  color: #333;
}
.homepage-container .el-card.creator-card h3 {
    margin: 0;
}
</style>
