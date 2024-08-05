<template>
    <el-container class="home-page">
      <el-header>
        <div class="header">
          <div class="logo">
            <i class="fas fa-robot logo-icon"></i>
            <span class="logo-text">Advisor<span class="logo-highlight">AI</span></span>
          </div>
          <div class="auth-links">
            <el-link href="/login">Login</el-link>
            <router-link to="/waitlist">Join waitlist</router-link>
          </div>
        </div>
      </el-header>
      <el-main>
        <div class="main-content">
          <h2>Your AI Copilot for Stock Analysis</h2>
          <p>Welcome to Advisor AI, the intelligent assistant that empowers stock analysts and investors. We're here to augment your expertise with cutting-edge AI technology.</p>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card class="feature-card">
                <h3>How Advisor AI Assists You</h3>
                <ul>
                  <li>Real-time market data analysis</li>
                  <li>AI-driven stock screening and filtering</li>
                  <li>Automated financial report interpretation</li>
                  <li>Sentiment analysis of news and social media</li>
                </ul>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card class="feature-card">
                <h3>Benefits for Analysts</h3>
                <ul>
                  <li>Accelerate your research process</li>
                  <li>Uncover hidden patterns in market data</li>
                  <li>Generate comprehensive stock reports in minutes</li>
                  <li>Validate your hypotheses with AI-backed insights</li>
                </ul>
              </el-card>
            </el-col>
          </el-row>
          
          <el-button type="primary" class="get-started-btn">Enhance Your Analysis Now</el-button>
        </div>
      </el-main>
      <el-footer>
        <div class="footer">
          <p>© 2024 Advisor AI. All rights reserved.</p>
          <p>101 California Avenue <br>
             D100A <br>
             Palo Alto, CA 94306</p>
        </div>
      </el-footer>
    </el-container>
  </template>
  
  <script>
  export default {
    name: 'HomePage'
  }
  </script>
  
  <style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  background-color: #409EFF;
  color: white;
}
.auth-links {
  display: flex;
  gap: 15px;
}
.main-content {
  text-align: center;
  margin-top: 50px;
  padding: 0 20px;
}
.feature-card {
  height: 100%;
  text-align: left;
}
.feature-card ul {
  padding-left: 20px;
}
.get-started-btn {
  margin-top: 30px;
  font-size: 1.2em;
  padding: 12px 24px;
}
header.el-header, footer.el-footer {
  padding: 0;
}
.header > h1 {
  font-size: 1.2rem;
  font-weight: 400;
}
.auth-links a {
  color: #fff;
  text-decoration: none;
  margin-left: 15px;
}
h2 {
  font-size: 2.8em;
  margin-bottom: 20px;
  color: #409EFF;
  font-weight: bold;
}
h3 {
  color: #409EFF;
}
.el-row {
  margin-top: 30px;
}

.logo {
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: -1px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-text {
  color: #ffffff;
}

.logo-highlight {
  color: #FFD700;
  font-style: italic;
}

.logo-icon {
  font-size: 1.8rem;
  color: #FFD700;
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    align-items: flex-start;
    padding: 10px 20px;
  }

  .auth-links {
    margin-top: 10px;
  }

  h2 {
    font-size: 2em;
  }

  .main-content {
    margin-top: 30px;
  }

  .get-started-btn {
    width: 100%;
  }

  .logo {
    font-size: 1.2rem;
  }
}
  </style>