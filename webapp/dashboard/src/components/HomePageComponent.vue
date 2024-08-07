<template>
    <el-container class="home-page">
      <el-header>
        <div class="header">
          <div class="logo">
            <img src="/logo.png" alt="AdvisorAI Logo" class="logo-image">
          </div>
          <div class="auth-links">
            <el-link href="/login">Login</el-link>
            <router-link to="/waitlist">Join waitlist</router-link>
          </div>
        </div>
      </el-header>
      <el-main>
        <div class="main-content">
          <h1>Welcome to advisorai.us – It's all about AI + US!</h1>
          
          <p>At advisorai.us, we're revolutionizing investment analysis by integrating AI with the collaborative principles of Git. Our platform allows users to harness the power of AI to analyze financial reports while also leveraging community contributions to continually refine and improve investment insights.</p>
          
          <h2>How It Works:</h2>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card class="feature-card">
                <h3>Upload Reports</h3>
                <p>Users upload PDFs of financial reports, SEC filings, and other relevant documents about a company. Whether it's Google, Microsoft, or any other stock, our platform processes all types of financial data.</p>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card class="feature-card">
                <h3>AI Analysis</h3>
                <p>The LLM analyzes the uploaded documents, extracting key insights, identifying trends, and providing comprehensive stock recommendations. It's like having a team of financial experts working for you around the clock.</p>
              </el-card>
            </el-col>
          </el-row>
          
          <el-row :gutter="20" style="margin-top: 20px;">
            <el-col :span="12">
              <el-card class="feature-card">
                <h3>Collaborate and Fork</h3>
                <p>Similar to Git, you can fork existing reports. See an analysis you like? Fork it! Add more documents, bring in additional data, and create a personalized version of the report. This fosters a dynamic and collaborative environment where insights are continually refined.</p>
              </el-card>
            </el-col>
            <el-col :span="12">
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
          
          <el-button type="primary" class="get-started-btn">Get Started Now</el-button>
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
  display: flex;
  align-items: center;
}

.logo-image {
  height: 40px;
  width: auto;
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

  .logo-image {
    height: 30px;
  }
}

h1, h2 {
  color: #409EFF;
}

.feature-card {
  height: 100%;
}

.get-started-btn {
  margin-top: 20px;
}

ul {
  padding-left: 20px;
}
  </style>