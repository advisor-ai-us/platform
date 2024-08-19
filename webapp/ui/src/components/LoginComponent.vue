<template>
  <div class="advisor-login-signup">
    <header class="logo-in-header">
      <a href="/"><img src="/logo.png" alt="Advisor AI Logo"></a>
      <!-- <h1>Get Started Now</h1>
      <p>An AI Powered Collaborative Investment Analysis</p> -->
    </header>

    <el-card class="login-signup-card">
      <el-tabs v-model="activeTab" type="card">
        <el-tab-pane label="Login" name="login">
          <el-form :model="loginForm" @submit.native.prevent="handleLogin" ref="loginForm" :rules="loginRules">
            <el-form-item label="Email" prop="email">
              <el-input v-model="loginForm.email" autocomplete="off"></el-input>
            </el-form-item>
            <el-form-item label="Password" prop="password">
              <el-input v-model="loginForm.password" type="password" autocomplete="off"></el-input>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" native-type="submit">Login</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        <!--
        <el-tab-pane label="Signup" name="signup">
          <el-form :model="signupForm" @submit.native.prevent="handleSignup" ref="signupForm" :rules="signupRules">
            <el-form-item label="Full Name" prop="fullName">
              <el-input v-model="signupForm.fullName" autocomplete="off"></el-input>
            </el-form-item>
            <el-form-item label="Email" prop="email">
              <el-input v-model="signupForm.email" autocomplete="off"></el-input>
            </el-form-item>
            <el-form-item label="Password" prop="password">
              <el-input v-model="signupForm.password" type="password" autocomplete="off"></el-input>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" native-type="submit">Signup</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      -->
      </el-tabs>
    </el-card>
  </div>
</template>
  
  <script>
  import axios from 'axios';
  export default {
    data() {
      return {
        activeTab: 'login',
        loginForm: {
          email: '',
          password: ''
        },
        signupForm: {
          fullName: '',
          email: '',
          password: ''
        },
        loginRules: {
          email: [
            { required: true, message: 'Please enter your email', trigger: 'blur' },
            { type: 'email', message: 'Please enter a valid email', trigger: ['blur', 'change'] }
          ],
          password: [
            { required: true, message: 'Please enter your password', trigger: 'blur' },
            { min: 5, message: 'Password must be at least 6 characters', trigger: 'blur' }
          ]
        },
        signupRules: {
          fullName: [
            { required: true, message: 'Please enter your full name', trigger: 'blur' }
          ],
          email: [
            { required: true, message: 'Please enter your email', trigger: 'blur' },
            { type: 'email', message: 'Please enter a valid email', trigger: ['blur', 'change'] }
          ],
          password: [
            { required: true, message: 'Please enter your password', trigger: 'blur' },
            { min: 6, message: 'Password must be at least 6 characters', trigger: 'blur' }
          ]
        }
      };
    },
    mounted() {
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
              this.$router.push({ name: 'AdvisorPersonalityPage' });
            } else {
              localStorage.removeItem('token');
            }
          })
          .catch((error) => {
            console.error(error);
            localStorage.removeItem('token');
          });        
      },
      handleLogin() {
        this.$refs.loginForm.validate((valid) => {
          if (valid) {
            axios.post(this.baseUrlForApiCall + 'login', this.loginForm)
              .then((response) => {
                this.$message({
                  message: 'Login successful',
                  type: 'success'
                });

                // Save token in local storage
                localStorage.setItem('token', response.data.token);
                localStorage.setItem('email', response.data.userEmail);
                localStorage.setItem('fullName', response.data.fullName);

                // Go to dashboard with page reload
                this.$router.push({ name: 'AdvisorPersonalityPage' });
              })
              .catch((error) => {
                console.error(error);
                this.$message({
                  message: error.response.data.error,
                  type: 'error'
                });
              });
          } else {
            console.log('Form validation failed');
            return false;
          }
        });        
      },
      handleSignup() {
        this.$refs.signupForm.validate((valid) => {
          if (valid) {
            axios.post(this.baseUrlForApiCall + 'signup', this.signupForm)
              .then((response) => {
                console.log(response);
                this.$message({
                  message: 'Signup successful',
                  type: 'success'
                });
                this.activeTab = 'login';
              })
              .catch((error) => {
                console.error(error);
                this.$message({
                  message: 'Signup failed',
                  type: 'error'
                });
              });
          } else {
            console.log('Form validation failed');
            return false;
          }
        });
      }
    }
  };
  </script>
  
  