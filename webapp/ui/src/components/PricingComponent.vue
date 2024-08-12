<template>
  <div>
    <header>
      <a href="/"><img src="/logo.png" alt="Advisor AI Logo"></a>
      <h1>Get Started Now</h1>
      <p>An AI Powered Collaborative Investment Analysis</p>
    </header>
  
    <div class="pricing-container">
      <h1>Pricing</h1>
      <p class="beta-notice">
        Our product is currently in beta stage. Sign up now to become a Pioneer and lock in your price for life!
      </p>
      <div class="pricing-options">
        <div class="pricing-card">
          <h2>Developed Countries</h2>
          <p class="price">$5/month</p>
          <el-button type="primary" @click="signUp('developed')">Sign Up</el-button>
        </div>
        <div class="pricing-card">
          <h2>Developing Countries</h2>
          <p class="price">₹50/month</p>
          <el-button type="primary" @click="signUp('developing')">Sign Up</el-button>
        </div>
      </div>
      <div class="usage-info">
        <h3>Usage Information</h3>
        <p>For more details, please see our <el-button type="text" @click="toggleUsagePolicy">Usage Policy</el-button>.</p>
      </div>
      <transition name="fade">
        <div v-show="showUsagePolicy" class="usage-policy">
          <h3>Usage Policy</h3>
          <p>Normal usage is defined as up to 100 API calls per day or 3000 API calls per month, whichever comes first.</p>
          <p>If you exceed this limit:</p>
          <ul>
            <li>You will be notified when you reach 80% of the normal usage limit.</li>
            <li>Any usage beyond the normal limit will incur additional charges based on our current API costs.</li>
            <li>These additional charges will be billed at the end of your billing cycle.</li>
          </ul>
          <p>We reserve the right to modify these limits and charges, but as a Pioneer user, your base subscription price will remain locked in for life.</p>
          <el-button type="text" @click="toggleUsagePolicy">Close</el-button>
        </div>
      </transition>
    </div>
  </div>
</template>
  
  <script>
  export default {
    data() {
      return {
        showUsagePolicy: false
      }
    },
    methods: {
      signUp(pricingType) {
        // Implement sign-up logic here
        console.log(`Signing up for ${pricingType} pricing`);
        this.$router.push('/waitlist');
      },
      toggleUsagePolicy() {
        this.showUsagePolicy = !this.showUsagePolicy;
      }
    }
  }
  </script>
  
  <style scoped>
  .pricing-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
    text-align: center;
  }
  
  .beta-notice {
    background-color: #f0f0f0;
    padding: 1rem;
    border-radius: 4px;
    margin-bottom: 2rem;
  }
  
  .pricing-options {
    display: flex;
    justify-content: space-around;
    flex-wrap: wrap;
  }
  
  .pricing-card {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 2rem;
    margin: 1rem;
    width: 300px;
  }
  
  .price {
    font-size: 1.5rem;
    font-weight: bold;
    margin: 1rem 0;
  }
  
  .features {
    text-align: left;
    padding-left: 20px;
    margin-bottom: 1rem;
  }
  
  .usage-info {
    margin-top: 2rem;
    background-color: #f9f9f9;
    padding: 1rem;
    border-radius: 4px;
  }
  
  .usage-policy {
    background-color: #f0f0f0;
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    padding: 1rem;
    margin-top: 1rem;
  }
  
  .fade-enter-active, .fade-leave-active {
    transition: opacity 0.5s;
  }
  .fade-enter, .fade-leave-to {
    opacity: 0;
  }
  </style>