<template>
  <div>
    <!-- Header Section -->
    <el-header class="header">
      <div class="logo">
        <el-badge value="Beta" class="item" color="#67c23a">
          TalkTo.app
        </el-badge>
      </div>
      <el-button type="primary" class="join-button" @click="$router.push('/join/creator')">Join as a Creator</el-button>
    </el-header>

    <!-- Main Banner -->
    <section class="banner">
      <h1>Become a Creator on TalkTo.app</h1>
      <p>Expand your reach and monetize your expertise with TalkTo.app</p>
      <el-button type="success" class="cta-button" @click="$router.push('/join/creator')">Join Now</el-button>
    </section>

    <!-- Who We're Looking For Section -->
    <section class="who-section">
      <h2>Who We're Looking For</h2>
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="field in fields" :key="field">
          <el-card class="profession-card">
            <el-icon class="profession-icon"><User /></el-icon>
            <p>{{ field }}</p>
          </el-card>
        </el-col>
      </el-row>
    </section>

    <!-- How It Works Section -->
    <section class="how-section">
      <h2>How It Works: 3 Simple Steps</h2>
      <el-row :gutter="20">
        <el-col :xs="24" :sm="24" :md="8">
          <el-card class="how-card">
            <h3>1. Create Your AI Replica</h3>
            <p>Share your expertise and personality to create an AI version of yourself that others can interact with 24/7.</p>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="24" :md="8">
          <el-card class="how-card">
            <h3>2. Set Your Pricing</h3>
            <p>Choose how much users pay to interact with your AI replica or to connect with you directly.</p>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="24" :md="8">
          <el-card class="how-card">
            <h3>3. Connect with Clients</h3>
            <p>Use our map-based system to help people find and connect with you or your AI replica.</p>
          </el-card>
        </el-col>
      </el-row>
    </section>

    <!-- Why Join TalkTo.app Section -->
    <!-- <section class="why-section">
      <h2>Why Join TalkTo.app?</h2>
      <ul class="why-list">
        <li><el-icon><Check /></el-icon> Reach a global audience 24/7</li>
        <li><el-icon><Check /></el-icon> Monetize your expertise effortlessly</li>
        <li><el-icon><Check /></el-icon> Provide personalized support at scale</li>
        <li><el-icon><Check /></el-icon> Enhance your professional brand</li>
        <li><el-icon><Check /></el-icon> Join a community of like-minded experts</li>
      </ul>
      <el-button type="success" class="cta-button" @click="$router.push('/join/creator')">Join as a Creator</el-button>
    </section> -->
    <el-row class="why-join-row">
      <el-col :xs="24" :sm="12" :md="14" :lg="16">
        <section class="why-section">
          <h2>Why Join TalkTo.app?</h2>
          <ul class="why-list">
            <li><el-icon><Check /></el-icon> Reach a global audience 24/7</li>
            <li><el-icon><Check /></el-icon> Monetize your expertise effortlessly</li>
            <li><el-icon><Check /></el-icon> Provide personalized support at scale</li>
            <li><el-icon><Check /></el-icon> Enhance your professional brand</li>
            <li><el-icon><Check /></el-icon> Join a community of like-minded experts</li>
          </ul>
        </section>
      </el-col>
      <el-col :xs="24" :sm="12" :md="10" :lg="8">
        <section class="join-form-section">
          <h2>Join as a Creator</h2>
          <el-form ref="form" :model="form" label-position="top" :rules="rules">
            <el-form-item label="Name" prop="name">
              <el-input v-model="form.name" placeholder="Enter your name"></el-input>
            </el-form-item>
            <el-form-item label="Email" prop="email">
              <el-input v-model="form.email" type="email"></el-input>
            </el-form-item>
            <el-form-item label="Password" prop="password">
              <el-input v-model="form.password" type="password"></el-input>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="onSubmit">Submit</el-button>
            </el-form-item>
          </el-form>
        </section>
      </el-col>
    </el-row>

    <!-- Footer Section -->
    <el-footer class="footer">
      <div>© 2024 TalkTo.app. All rights reserved.</div>
    </el-footer>
  </div>
</template>

<script setup>
import { User, Check } from '@element-plus/icons-vue';
</script>

<script>
export default {
  data() {
    return {
      fields: [
        "Therapist", "YouTuber", "Nutritionist", "Dietitian", "Wellness Coach", 
        "Mental Health Expert", "Telemedicine Provider", "Fitness Expert", 
        "Meditation Guide", "Sleep Specialist", "Pharmacist", "Health Influencer", 
        "Patient Advocate", "Medical Researcher", "Holistic Health Practitioner"
      ],
      form: {
        name: '',
        email: '',
        password: ''
      },
      rules: {
        name: [
          { required: true, message: 'Please enter your name', trigger: 'blur' }
        ],
        email: [
          { required: true, message: 'Please enter your email', trigger: 'blur' },
          { type: 'email', message: 'Please enter a valid email', trigger: ['blur', 'change'] }
        ],
        password: [
          { required: true, message: 'Please enter your password', trigger: 'blur' }
        ]
      }
    };
  },
  methods: {
    onSubmit() {
      console.log('Form submitted:', this.form);
    }
  }
}
</script>

<style scoped>
/* General Layout */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: 'Helvetica Neue', Arial, sans-serif;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 5%;
  background-color: #002b5c;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  flex-wrap: wrap;
}

.logo {
  color: white;
  font-size: 26px;
  font-weight: bold;
  height: auto;
}

.join-button {
  background-color: #67c23a;
  color: white;
  padding: 10px 20px;
  font-size: 16px;
  border-radius: 5px;
  transition: background-color 0.3s;
  width: 100%;
  max-width: 200px;
}

.join-button:hover {
  background-color: #56a32a;
}

.banner {
  text-align: center;
  padding: 140px 5%;
  background-image: url('/background-image.webp');
  background-size: cover;
  background-position: center;
  color: white;
  font-weight: 300;
  box-shadow: inset 0 0 2000px rgba(0, 0, 0, 0.3);
  min-height: 450px;
}

.banner h1 {
  font-size: 32px;
  margin-bottom: 20px;
  font-weight: bold;
  line-height: 28px;
}

.banner p {
  font-size: 18px;
  margin-bottom: 30px;
}

.cta-button {
  padding: 12px 30px;
  font-size: 18px;
  background-color: #67c23a;
  border-radius: 5px;
  transition: background-color 0.3s;
  margin: 35px auto auto auto;
  display: block;
  overflow: hidden;
  height: auto;
  width: 100%;
  max-width: 250px;
}

.cta-button:hover {
  background-color: #56a32a;
}

/* Who We're Looking For Section */
.who-section {
  padding: 50px 5%;
  background-color: #f7f9fc;
}

.who-section h2 {
  font-size: 28px;
  text-align: center;
  margin-bottom: 40px;
}

.profession-card {
  text-align: center;
  padding: 20px;
  background-color: #fff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s;
  margin-bottom: 20px;
}

.profession-card:hover {
  transform: translateY(-10px);
}

.profession-icon {
  font-size: 40px;
  color: #409EFF;
  margin-bottom: 10px;
}

/* How It Works Section */
.how-section {
  padding: 50px 5%;
}

.how-section h2 {
  font-size: 28px;
  text-align: center;
  margin-bottom: 40px;
}

.how-card {
  padding: 20px;
  background-color: #fff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  min-height: 175px;
  line-height: 20px;
  margin-bottom: 20px;
}

.how-card:hover {
  transform: translateY(-10px);
}

.how-card h3 {
  font-size: 20px;
  margin-bottom: 15px;
  font-weight: bold;
}

/* Why Join Section */
.why-section {
  /* padding: 50px 5%; */
  background-color: #f7f9fc;
  display: flex;
  flex-direction: column;
}

.why-section h2, 
.join-form-section h2 {
  font-size: 28px;
  text-align: center;
  margin-bottom: 40px;
}

.why-list {
  list-style: none;
  padding: 0;
  margin: 0 auto;
  max-width: 375px;
  margin-bottom: 20px;
}

.why-list li {
  font-size: 16px;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
}

.why-list i {
  color: #67c23a;
  margin-right: 10px;
}

/* Footer Section */
.footer {
  text-align: center;
  padding: 20px;
  background-color: #002b5c;
  color: white;
  font-size: 14px;
}

.why-join-row {
  display: flex;
  align-items: flex-start;
  padding: 50px 5%;
  background-color: #f7f9fc;
}

.why-section {
  padding-right: 20px; /* Ensure there's some space between the text and the form */
}

.join-form-section {
  padding: 30px 50px;
  background-color: #fff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  border-radius: 5px;
}

.join-form-section h2 {
  font-size: 28px;
  text-align: center;
  margin-bottom: 20px;
}

.join-form-section .el-form-item {
  margin-bottom: 20px;
}

.join-form-section .el-input,
.join-form-section .el-button {
  width: 100%;
}

.join-form-section .el-button {
  background-color: #67c23a;
  color: white;
  padding: 12px 20px;
  font-size: 16px;
  border-radius: 5px;
  transition: background-color 0.3s;
}

.join-form-section .el-button:hover {
  background-color: #56a32a;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .header {
    flex-direction: column;
    align-items: center;
  }

  .logo {
    line-height: 30px;
  }

  .join-button {
    width: auto;
    padding: 10px;
  }

  .banner h1 {
    font-size: 28px;
  }

  .banner p {
    font-size: 16px;
  }

  .who-section h2,
  .how-section h2,
  .why-section h2 {
    font-size: 24px;
  }

  .why-list {
    padding: 0 20px;
  }
}

@media (max-width: 480px) {
  .banner h1 {
    font-size: 24px;
  }

  .banner p {
    font-size: 14px;
  }

  .cta-button {
    font-size: 16px;
    padding: 10px 20px;
  }

  .who-section h2,
  .how-section h2,
  .why-section h2 {
    font-size: 22px;
  }

  .profession-card,
  .how-card {
    padding: 15px;
  }

  .why-list li {
    font-size: 14px;
  }
}
</style>

<style>
.el-form-item--label-top .el-form-item__label {
    margin: 0 !important;
}
</style>