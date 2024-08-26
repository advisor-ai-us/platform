<template>
    <div class="reset-password">
      <header class="logo-in-header">
        <a href="/"><img src="/logo.png" alt="Advisor AI Logo"></a>
      </header>
  
      <el-card class="reset-password-card">
        <h2 style="margin-top: 0;">Reset Password</h2>
        <el-form :model="resetPasswordForm" @submit.native.prevent="handleResetPassword" ref="resetPasswordForm" :rules="resetPasswordRules" label-width="145px" class="reset-password-form" label-position="left">
          <!-- Email Address -->
          <el-form-item label="Email Address" prop="email">
            <el-input v-model="resetPasswordForm.email" autocomplete="off"></el-input>
          </el-form-item>
          
          <!-- New Password -->
          <el-form-item label="New Password" prop="password">
            <el-input v-model="resetPasswordForm.password" type="password" autocomplete="off"></el-input>
          </el-form-item>
          
          <!-- Confirm Password -->
          <el-form-item label="Confirm Password" prop="confirmPassword">
            <el-input v-model="resetPasswordForm.confirmPassword" type="password" autocomplete="off"></el-input>
          </el-form-item>
  
          <el-form-item style="margin-bottom: 0;">
            <el-button type="primary" native-type="submit">Reset Password</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        resetPasswordForm: {
          email: '',
          password: '',
          confirmPassword: ''
        },
        resetPasswordRules: {
          email: [
            { required: true, message: 'Please enter your email address', trigger: 'blur' },
            { type: 'email', message: 'Please enter a valid email', trigger: ['blur', 'change'] }
          ],
          password: [
            { required: true, message: 'Please enter a new password', trigger: 'blur' },
            { min: 6, message: 'Password must be at least 6 characters long', trigger: 'blur' }
          ],
          confirmPassword: [
            { required: true, message: 'Please confirm your new password', trigger: 'blur' },
            { validator: (rule, value, callback) => {
                if (value !== this.resetPasswordForm.password) {
                  callback(new Error('Passwords do not match'));
                } else {
                  callback();
                }
              }, 
              trigger: 'blur'
            }
          ]
        }
      };
    },
    methods: {
      handleResetPassword() {
        this.$refs.resetPasswordForm.validate((valid) => {
          if (valid) {
            // Submit the reset password request
            axios.post(this.baseUrlForApiCall + 'reset_password', {
              email: this.resetPasswordForm.email,
              password: this.resetPasswordForm.password
            })
            .then((response) => {
              this.$message({
                message: 'Password reset successful',
                type: 'success'
              });
              this.resetPasswordForm.email = '';
              this.resetPasswordForm.password = '';
              this.resetPasswordForm.confirmPassword = '';
            })
            .catch((error) => {
              this.$message({
                message: error.response.data.error || 'Failed to reset password',
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
  
  <style>
  .reset-password-card {
    max-width: 500px;
    margin: 50px auto;
  }
  .reset-password-card .el-form-item--label-top .el-form-item__label {
    margin-bottom: 0;
    line-height: 17px;
  }
  </style>
  