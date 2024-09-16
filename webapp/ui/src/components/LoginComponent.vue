<template>
  <div class="homepage-container">
    <header class="header">
      <div class="header-content">
        <div class="logo-title">
          <el-link href="/" :underline="false">
            <img src="/logo.png" alt="TalkTo Logo" class="logo">
            <h1 class="site-title">TalkTo</h1>
          </el-link>
        </div>
        <nav class="nav-links">
          <el-button type="success" @click="$router.push('/user/waitlist')">Join Waitlist</el-button>
          <el-button type="warning" @click="$router.push('/join/creator')">Join as Creator</el-button>
          <el-button type="info" @click="$router.push('/membership/pricing')">Pricing</el-button>
        </nav>
      </div>
    </header>

    <main class="main-content">
      <el-card class="login-signup-card">
        <template #header>
          <div class="card-header">
            <h2 class="login-title">Login</h2>
          </div>
        </template>
        <el-form :model="loginForm" @submit.native.prevent="handleLogin" ref="loginForm" :rules="loginRules">
          <el-form-item label="Email" prop="email">
            <el-input v-model="loginForm.email" autocomplete="off"></el-input>
          </el-form-item>
          <el-form-item label="Password" prop="password">
            <el-input v-model="loginForm.password" type="password" autocomplete="off"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" native-type="submit">Login</el-button>
            <el-button type="primary" @click="$router.push({ name: 'ResetPassword' })" link>Reset Password</el-button>
          </el-form-item>
        </el-form>
        <p class="signup-link">
          Don't have an account? <el-button type="primary" link @click="$router.push('/user/waitlist')">Sign up</el-button>
        </p>
      </el-card>
    </main>
    <footer class="footer">
      <p>&copy; 2024 TalkTo AI. All rights reserved.</p>
    </footer>
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
              this.$router.push({ name: 'Home' });
              // if (response.data.role === 'creator') {
              //   this.$router.push({ name: 'EditCreatorPage' });
              // } else {
              //   this.$router.push({ name: 'AdvisorPersonalityPage' });
              // }
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
                this.$router.push({ name: 'Home' });
                // if (response.data.role === 'creator') {
                //   this.$router.push({ name: 'EditCreatorPage' });
                // } else {
                //   this.$router.push({ name: 'AdvisorPersonalityPage' });
                // }
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
    }
  };
  </script>
  
  <style>
.homepage-container {
  font-family: Arial, sans-serif;
  color: #333;
}
.header {
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 1rem;
}
.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
}
.logo-title {
  display: flex;
  align-items: center;
}
.logo {
  height: 40px;
}
.site-title {
  margin-left: 10px;
  font-size: 1.5rem;
  font-weight: bold;
  color: #333;
}
.nav-links button {
  margin-left: 1rem;
}
.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
}
.login-signup-card {
  width: 450px;
  margin: 50px auto;
  padding: 20px;
}
.login-title {
  text-align: center;
  margin: 0;
  font-size: 1.5rem;
  color: #333;
}
.signup-link {
  text-align: center;
  margin: 15px 0 0 0;
}
.signup-link .el-button {
  padding: 0;
}
</style>

