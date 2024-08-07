<template>
  <el-container class="home-page">
    <el-header>
      <div class="header">
        <div class="logo">
          <img src="/ai+us-logo.png" alt="AdvisorAI Logo" class="logo-image">
        </div>
        <div class="menu" v-if="isLoggedIn">
          <router-link to="/advisor-personality" class="menu-item">Advisor AI</router-link>
        </div>
        <div class="menu" v-else>
          <router-link to="/login" class="menu-item">Login</router-link>
          <router-link to="/waitlist" class="menu-item">Join waitlist</router-link>
        </div>
      </div>
    </el-header>
    <el-main>
      <div class="main-content">
        <h1 style="margin-top: 0;">Welcome to advisorai.us – It's all about AI + US!</h1>

        <p>At advisorai.us, we're revolutionizing investment analysis by integrating AI with the collaborative principles of Git. Our platform allows users to harness the power of AI to analyze financial reports while also leveraging community contributions to continually refine and improve investment insights.</p>

        <h2>How it works:</h2>

        <el-row :gutter="20">
          <el-col :span="isMobile ? 24 : 12">
            <el-card class="feature-card">
              <h3>Upload Reports</h3>
              <p>Users upload PDFs of financial reports, SEC filings, and other relevant documents about a company. Whether it's Google, Microsoft, or any other stock, our platform processes all types of financial data.</p>
            </el-card>
          </el-col>
          <el-col :span="isMobile ? 24 : 12" :style="isMobile ? 'margin-top: 20px;' : ''">
            <el-card class="feature-card">
              <h3>AI Analysis</h3>
              <p>The LLM analyzes the uploaded documents, extracting key insights, identifying trends, and providing comprehensive stock recommendations. It's like having a team of financial experts working for you around the clock.</p>
            </el-card>
          </el-col>
        </el-row>

        <el-row :gutter="20" style="margin-top: 20px;">
          <el-col :span="isMobile ? 24 : 12">
            <el-card class="feature-card">
              <h3>Collaborate and Fork</h3>
              <p>Similar to Git, you can fork existing reports. See an analysis you like? Fork it! Add more documents, bring in additional data, and create a personalized version of the report. This fosters a dynamic and collaborative environment where insights are continually refined.</p>
            </el-card>
          </el-col>
          <el-col :span="isMobile ? 24 : 12" :style="isMobile ? 'margin-top: 20px;' : ''">
            <el-card class="feature-card">
              <h3>Share and Improve</h3>
              <p>Share your reports with the community, allowing others to benefit from your insights and build upon them. The more data and perspectives we gather, the smarter and more accurate our AI becomes.</p>
            </el-card>
          </el-col>
        </el-row>

        <h2>Why advisorai.us?</h2>

        <ul>
          <li><strong>Community-Driven Insights:</strong> Leverage the collective intelligence of a passionate investment community. Your inputs help create richer, more accurate analyses.</li>
          <li><strong>Advanced AI Technology:</strong> The LLM continuously learns and adapts, providing cutting-edge financial insights and recommendations.</li>
          <li><strong>Fun and Engaging:</strong> We make investing not just profitable but also enjoyable. Engage with the community, share your findings, and see how your contributions help others.</li>
        </ul>

        <p>Join us at advisorai.us, where AI and US come together to make smarter investment decisions. It's all about collaboration, innovation, and making your financial journey successful and enjoyable.</p>

        <el-button type="primary" @click="goToWaitlist" class="get-started-btn">Get Started Now</el-button>
      </div>
    </el-main>
    <el-footer>
      <div class="footer">
        <el-row>
          <el-col :span="isMobile ? 24 : 16">
            <p>© 2024 Advisor AI. All rights reserved.</p>
          </el-col>
          <el-col :span="isMobile ? 24 : 8" :style="isMobile ? 'margin-top: 15px;' : ''">
            <p>
              <el-icon style="font-size: 1.2rem;vertical-align: text-bottom;margin: 0 3px 1px 0;"><HomeFilled /></el-icon>
              <strong>Contact Us:</strong>
            </p>
            <p>101 California Avenue </p>
            <p>D100A</p>
            <p>Palo Alto, CA 94306</p>
          </el-col>
        </el-row>
      </div>
    </el-footer>
  </el-container>
</template>

<script>
import { HomeFilled } from '@element-plus/icons-vue';
export default {
  name: 'HomePage',
  data() {
    return {
      isMobile: false,
      isLoggedIn: false,
    };
  },
  components: {
    HomeFilled,
  },
  mounted() {
    const token = localStorage.getItem('token');
    if (token) {
      this.isLoggedIn = true;
    }

    // Add a listener for window resize events
    window.addEventListener('resize', this.handleWindowResize);
    this.handleWindowResize();
  },
  beforeDestroy() {
    // Remove the listener when the component is destroyed
    window.removeEventListener('resize', this.handleWindowResize);
  },
  methods: {
    handleWindowResize() {
      this.isMobile = window.innerWidth <= 700;
    },
    goToWaitlist() {
      this.$router.push('/waitlist');
    }
  }
}
</script>

<style>
header.el-header {
    position: fixed;
    left: 0;
    right: 0;
    top: 0;
    z-index: 999;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 30px 0 40px;
  background-color: #409EFF;
  color: white;
}
main.el-main {
    margin-top: 45px;
}
.menu {
  display: flex;
  position: relative;
}

.menu-item {
  display: inline-block;
  padding: 8px 18px;
  margin: 0 5px;
  text-decoration: none;
  color: white;
  background: linear-gradient(to right, #FAF45F, #F60100);
  position: relative;
  clip-path: polygon(0 0, 90% 0, 100% 50%, 90% 100%, 0 100%, 10% 50%);
  transition: background-color 0.3s;
}
.menu-item:hover {
  background: linear-gradient(to right, #ffcc00, #ff3300);
}
.auth-links {
  display: flex;
  gap: 15px;
}
.main-content {
  text-align: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}
.feature-card {
  height: 100%;
  text-align: left;
}
.feature-card ul {
  padding-left: 20px;
}
.get-started-btn {
  margin-top: 20px;
  font-size: 1.2em;
  padding: 12px 24px;
}
header.el-header, footer.el-footer {
  padding: 0;
}
.main-content > h1 {
  font-size: 2.2em;
  line-height: 30px;
  background: linear-gradient(to right, #FAF45F, #F60100);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  transition: background-color 0.3s;
}

.auth-links a {
  color: #fff;
  text-decoration: none;
  margin-left: 15px;
}

h2 {
  margin-bottom: 20px;
  color: #409EFF;
  font-weight: bold;
}

h3 {
  color: #409EFF;
  margin: 0;
}

.el-row {
  margin-top: 30px;
}

.logo {
  display: flex;
  align-items: center;
}

.logo-image {
  height: 40px;
  width: auto;
  padding: 5px 0;
}

p {
  line-height: 22px;
  margin-bottom: 0;
}

@media (max-width: 768px) {
  .header {
    align-items: flex-start;
    padding: 10px 5px 10px 10px;
  }

  .auth-links {
    margin-top: 10px;
  }

  h1, h2 {
    font-size: 1.5em !important;
  }

  .get-started-btn {
    width: 100%;
  }

  .logo-image {
    height: 24px;
  }

  .footer {
    padding: 10px !important;
  }
  #app .main-content {
    padding: 0;
  }
}

h1, h2 {
  color: #409EFF;
  line-height: 26px;
  font-size: 2em;
}

.feature-card {
  height: 100%;
}

.get-started-btn {
  margin-top: 20px;
}

ul {
  padding-left: 0;
  list-style: none;
  text-align: left;
  line-height: 24px;
}

.footer {
  background: #409EFF;
  color: #fff;
  padding: 10px 40px;
}

.footer > .el-row {
  margin: 0;
}

.footer > .el-row p {
  margin: 0;
  font-size: 0.9rem;
}
</style>
