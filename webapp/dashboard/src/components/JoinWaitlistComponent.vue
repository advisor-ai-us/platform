<template>
  <el-card class="join-waitlist-card">
    <h2>Join the Waitlist</h2>
    <el-form :model="waitlistForm" @submit.native.prevent="handleJoinWaitlist" ref="waitlistForm" :rules="waitlistRules" label-position="top">
      <el-form-item label="Full Name" prop="fullName">
        <el-input v-model="waitlistForm.fullName" autocomplete="off"></el-input>
      </el-form-item>
      <el-form-item label="Email" prop="email">
        <el-input v-model="waitlistForm.email" autocomplete="off"></el-input>
      </el-form-item>
      <el-form-item label="Password" prop="password">
        <el-input v-model="waitlistForm.password" type="password" autocomplete="off"></el-input>
      </el-form-item>
      <el-form-item label="About Yourself" prop="aboutYourself">
        <el-input type="textarea" v-model="waitlistForm.aboutYourself" :rows="4" placeholder="Tell us about yourself..."></el-input>
      </el-form-item>
      <el-form-item label="Biggest Problem to Solve" prop="biggestProblem">
        <el-input type="textarea" v-model="waitlistForm.biggestProblem" :rows="4" placeholder="What's the biggest problem you hope to solve with an AI Finance analyst?"></el-input>
      </el-form-item>
      <el-form-item label="Invite Code">
        <el-input v-model="waitlistForm.inviteCode" autocomplete="off"></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" native-type="submit">Join Waitlist</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      waitlistForm: {
        fullName: '',
        email: '',
        password: '',
        aboutYourself: '',
        biggestProblem: '',
        inviteCode: ''
      },
      waitlistRules: {
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
        ],
        aboutYourself: [
          { required: true, message: 'Please tell us about yourself', trigger: 'blur' }
        ],
        biggestProblem: [
          { required: true, message: 'Please describe the biggest problem you hope to solve', trigger: 'blur' }
        ]
      }
    };
  },
  methods: {
    handleJoinWaitlist() {
      this.$refs.waitlistForm.validate((valid) => {
        if (valid) {
          axios.post(this.baseUrlForApiCall + 'join_waitlist', this.waitlistForm)
            .then((response) => {
              this.$message({
                message: 'You have been added to the waitlist successfully',
                type: 'success'
              });
              this.waitlistForm.fullName = '';
              this.waitlistForm.email = '';
              this.waitlistForm.password = '';
              this.waitlistForm.aboutYourself = '';
              this.waitlistForm.biggestProblem = '';
              this.waitlistForm.inviteCode = '';
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
    }
  }
};
</script>

<style scoped>
.join-waitlist-card {
  max-width: 450px;
  margin: 50px auto;
}
.join-waitlist-card .el-form-item--label-top .el-form-item__label {
    margin-bottom: 0;
}
</style>