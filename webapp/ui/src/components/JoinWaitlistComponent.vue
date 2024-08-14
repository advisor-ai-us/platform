<template>
  <div>
    <header class="logo-in-header">
      <a href="/"><img src="/logo.png" alt="Advisor AI Logo"></a>
      <!-- <h1>Get Started Now</h1>
      <p>An AI Powered Collaborative Investment Analysis</p> -->
    </header>
  
    <el-card class="join-waitlist-card">
      <h2 style="margin-top: 0;">Join the Waitlist</h2>
      <el-form :model="waitlistForm" @submit.native.prevent="handleJoinWaitlist" ref="waitlistForm" :rules="waitlistRules" label-position="top">
        <!-- Existing Fields -->
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
          <el-input type="textarea" v-model="waitlistForm.aboutYourself" :rows="2" placeholder="Tell us about yourself..."></el-input>
        </el-form-item>
        <el-form-item label="Biggest Problem to Solve" prop="biggestProblem">
          <el-input type="textarea" v-model="waitlistForm.biggestProblem" :rows="2" placeholder="What's the biggest problem you hope to solve with an AI Finance analyst?"></el-input>
        </el-form-item>
        <el-form-item label="Invite Code">
          <el-input v-model="waitlistForm.inviteCode" autocomplete="off" @keyup.enter="handleInviteCode" @blur="handleInviteCode" :disabled="inviteCodeValid === 'valid'" @input="inviteCodeValid = ''"></el-input>

          <span v-if="inviteCodeValid === 'valid'" style="color: green;line-height: 14px;font-style: italic;font-size: small;">
            <el-icon style="vertical-align: bottom;"><Select /></el-icon>
            Invite code is valid
          </span>
          <span v-else-if="inviteCodeValid === 'invalid'" style="color: red;line-height: 14px;font-style: italic;font-size: small;">
            <el-icon style="vertical-align: bottom;"><CloseBold /></el-icon>
            Invite code is invalid
          </span>

        </el-form-item>

        <!-- Credit Card Information -->
        <el-form-item label="Card Information" class="card-element" :style="{ display: inviteCodeValid === 'valid' ? 'block' : 'none' }">
          <div id="card-element" style="padding: 10px; border: 1px solid #d9d9d9; border-radius: 4px;"></div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" native-type="submit">Join Waitlist</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios';
import { loadStripe } from '@stripe/stripe-js';
import { Select, CloseBold } from '@element-plus/icons-vue';

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
      },
      inviteCodeValid: '',
      stripe: null,
      cardElement: null
    };
  },
  components: {
    Select,
    CloseBold
  },
  async mounted() {

    setTimeout(async() => {
      this.stripe = await loadStripe('pk_test_51PmwLHRu672bSSgB1fn413d8zIpQaJXQuoNYDf0F1odsXdKzUxEloAw0E1r67I7oe7khbujftmgJaSOF7thhYIo900SGo2gZbM'); // Replace with your Stripe publishable key
      const elements = this.stripe.elements();
      this.cardElement = elements.create('card');
      this.cardElement.mount('#card-element');
    }, 2000);
  },
  methods: {
    handleJoinWaitlist() {
      this.$refs.waitlistForm.validate(async (valid) => {
        if (valid) {
          // Create a payment method and handle the payment
          const { error, paymentMethod } = await this.stripe.createPaymentMethod({
            type: 'card',
            card: this.cardElement,
            billing_details: {
              name: this.waitlistForm.fullName,
              email: this.waitlistForm.email
            }
          });

          // if (error) {
          //   this.$message({
          //     message: error.message,
          //     type: 'error'
          //   });
          //   return;
          // }

          axios.post(this.baseUrlForApiCall + 'join_waitlist', {
            ...this.waitlistForm,
            //paymentMethodId: paymentMethod.id
          })
            .then((response) => {
              this.$message({
                message: 'You have been added to the waitlist successfully',
                type: 'success'
              });
              this.clearForm();
            })
            .catch((error) => {
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
    handleInviteCode() {
      if (this.waitlistForm.inviteCode) {
        axios.post(this.baseUrlForApiCall + 'validate_invite_code', { inviteCode: this.waitlistForm.inviteCode })
          .then((response) => {
            if (response.data.valid) {
              this.inviteCodeValid = 'valid';
            } else {
              this.inviteCodeValid = 'invalid';
            }
          })
          .catch((error) => {
            this.inviteCodeValid = 'invalid';
          });
      }
    },
    clearForm() {
      this.waitlistForm.fullName = '';
      this.waitlistForm.email = '';
      this.waitlistForm.password = '';
      this.waitlistForm.aboutYourself = '';
      this.waitlistForm.biggestProblem = '';
      this.waitlistForm.inviteCode = '';
    }
  }
};
</script>

<style>
.join-waitlist-card {
  max-width: 450px;
  margin: 50px auto;
}
.join-waitlist-card .el-form-item--label-top .el-form-item__label {
  margin-bottom: 0;
  line-height: 17px;
}
.card-element .el-form-item__content {
    display: block;
}
</style>
