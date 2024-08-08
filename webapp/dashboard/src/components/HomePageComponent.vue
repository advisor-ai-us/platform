<template>
  <div>
    <div class="auth-links">
          <el-button type="primary" @click="$router.push('/login')">Login</el-button>
          <el-button type="success" @click="$router.push('/waitlist')">Join Waitlist</el-button>
        </div>

    <header>
      <img src="/logo.png" alt="Advisor AI Logo">
      <h1>Get Started Now</h1>
      <p>An AI Powered Collaborative Investment Analysis</p>
    </header>
    <div class="container">
      <div class="section">
        <el-carousel height="400px">
          <el-carousel-item>
            <img src="/homepage-screenshot-top-part.png" alt="Homepage Screenshot" class="screenshot">
          </el-carousel-item>
          <el-carousel-item>
            <img src="/asset-ai-report.png" alt="Asset AI Report" class="screenshot">
          </el-carousel-item>
        </el-carousel>
        <h2>How it works:</h2>
        <div class="features">
          <div class="feature">
            <h3>Find verifiable reports</h3>
            <p>Our System finds PDF's of financial reports, SEC filings, and other relevant documents about a company. Whether it's Google, Microsoft, or any other stock, our platform processes all types of financial data.</p>
          </div>
          <div class="feature">
            <h3>AI Analysis</h3>
            <p>The LLM analyzes the verified documents, extracting key insights, identifying trends, and providing comprehensive stock recommendations. It's like having a team of financial experts working for you around the clock.</p>
          </div>
          <div class="feature">
            <h3>Collaborate and Fork</h3>
            <p>Similar to Git, you can fork existing reports. See an analysis you like? Fork it! Add more documents, bring in additional data, and create a personalized version of the report. This fosters a dynamic and collaborative environment where insights are continually refined.</p>
          </div>
          <div class="feature">
            <h3>Share and Improve</h3>
            <p>Share your reports with the community, allowing others to benefit from your insights and build upon them. The more data and perspectives we gather, the smarter and more accurate our AI becomes.</p>
          </div>
        </div>
        <h2>Current AI recommendations:</h2>
        <div class="feature">

        <div class="recommendations">
          <div class="recommendation buy">
            <span class="icon">⬆️</span> Google <span class="action"></span>
          </div>
          <div class="recommendation sell">
            <span class="icon">⬇️</span> Nvidia <span class="action"></span>
          </div>
          <div class="recommendation hold">
            <span class="icon">➡️</span> BTC/USD <span class="action"></span>
          </div>
        </div>
        </div>
      </div>
    </div>
    <div class="footer">
      &copy; 2024 Advisor AI. All rights reserved. | Contact Us: 101 California Avenue, D100A, Palo Alto, CA 94306
    </div>
  </div>
</template>

<style scoped>
body {
  font-family: 'Open Sans', sans-serif;
  background: #f5f5f5;
  color: #333;
  margin: 0;
  padding: 0;
}
header {
  background: #fff;
  padding: 40px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  text-align: center;
  border-radius: 8px;
}
header img {
  max-width: 100px;
  margin-bottom: 20px;
}
header h1 {
  font-size: 2.5em;
  margin: 0.2em 0;
  color: #007BFF;
}
header p {
  font-size: 1.2em;
  color: #777;
}
.container {
  max-width: 1200px;
  margin: 2em auto;
  padding: 2em;
  background: #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  border-radius: 8px;
}
.section {
  margin-bottom: 2em;
}
.section h2 {
  font-size: 2em;
  margin-bottom: 1em;
  color: #444;
  text-align: center;
}
.features {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-around;
  text-align: left;
}
.feature {
  flex: 1 1 45%;
  margin: 1em;
  padding: 1em;
  background: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.feature h3 {
  font-size: 1.5em;
  margin-bottom: 0.5em;
  color: #007BFF;
}
.feature p {
  font-size: 1em;
  color: #666;
}
.section ul {
  list-style: none;
  padding: 0;
  text-align: left;
}
.section ul li {
  margin: 0.5em 0;
  padding-left: 20px;
  position: relative;
}
.section ul li::before {
  content: '•';
  position: absolute;
  left: 0;
  color: #007BFF;
}
.button {
  display: inline-block;
  padding: 0.75em 1.5em;
  color: #fff;
  background: #007BFF;
  border-radius: 8px;
  text-decoration: none;
  font-size: 1em;
  text-align: center;
  margin-top: 1em;
  transition: background 0.3s ease;
}
.button:hover {
  background: #0056b3;
}
.recommendations {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 1em;
}
.recommendation {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 80%;
  padding: 1em;
  margin: 0.5em 0;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  font-size: 1.2em;
}
.recommendation .icon {
  font-size: 1.5em;
  margin-right: 0.5em;
}
.recommendation.buy {
  background: #d4edda;
  color: #155724;
}
.recommendation.sell {
  background: #f8d7da;
  color: #721c24;
}
.recommendation.hold {
  background: #fff3cd;
  color: #856404;
}
.recommendation .action {
  font-weight: bold;
}
.footer {
  text-align: center;
  padding: 2em 0;
  color: #777;
  font-size: 0.9em;
}
.screenshot {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}
.auth-links {
  text-align: right;
  margin-bottom: 20px;
}

.auth-links .el-button {
  margin-left: 10px;
}

.el-carousel {
  margin-bottom: 2em;
}

.el-carousel__item {
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>