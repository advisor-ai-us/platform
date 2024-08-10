<template>
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
  </div>
</template>

<script>
export default {
  methods: {
    signUp(pricingType) {
      // Implement sign-up logic here
      console.log(`Signing up for ${pricingType} pricing`);
      this.$router.push('/waitlist');
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
</style>
