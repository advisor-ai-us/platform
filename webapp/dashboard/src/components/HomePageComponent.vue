<template>
    <el-container class="home-page">
      <el-header>
        <div class="header">
          <h1>Welcome to Advisor AI</h1>
          <div class="auth-links">
            <el-link href="/login">Login</el-link>
            <router-link to="/waitlist">Join waitlist</router-link>
          </div>
        </div>
      </el-header>
      <el-main>
        <div class="main-content">
          <p>Welcome to Advisor AI, your AI financial analyst. Here's what it can do for you:</p>
          <ol>
            <li>Track your investments</li>
            <li>Compare your investments to the S&P 500</li>
            <li>Provide contextual investment recommendations based on your lifecycle stage</li>
            <li>Analyze companies like a human analyst and make buy/sell recommendations</li>
          </ol>
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
    text-align: left;
    margin-top: 50px;
}
.footer {
    text-align: center;
    padding: 10px 0;
    background-color: #f2f2f2;
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
  </style>