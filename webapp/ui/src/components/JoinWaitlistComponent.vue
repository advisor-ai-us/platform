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
          <el-button type="primary" @click="$router.push('/user/login')">Login</el-button>
          <el-button type="warning" @click="$router.push('/join/creator')">Join as Creator</el-button>
          <el-button type="info" @click="$router.push('/membership/pricing')">Pricing</el-button>
        </nav>
      </div>
    </header>
    <main class="main-content">
      <el-card class="join-waitlist-card">
        <template #header>
          <div class="card-header">
            <h2 class="login-title">Join the Waitlist</h2>
          </div>
        </template>
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
          <!-- <el-form-item label="About Yourself" prop="aboutYourself">
            <el-input type="textarea" v-model="waitlistForm.aboutYourself" :rows="2" placeholder="Tell us about yourself..."></el-input>
          </el-form-item>
          <el-form-item label="Biggest Problem to Solve" prop="biggestProblem">
            <el-input type="textarea" v-model="waitlistForm.biggestProblem" :rows="2" placeholder="What's the biggest problem you hope to solve with an AI Finance analyst?"></el-input>
          </el-form-item> -->
          <el-form-item label="Discount code">
            <el-input v-model="waitlistForm.discountCode" autocomplete="off" @keyup.enter="handleDiscountCode" @blur="handleDiscountCode" :disabled="discountCodeValid === 'valid'" @input="discountCodeValid = ''"></el-input>

            <span v-if="discountCodeValid === 'valid'" style="color: green;line-height: 14px;font-style: italic;font-size: small;">
              <el-icon style="vertical-align: bottom;"><Select /></el-icon>
              Discount code is valid
            </span>
            <span v-else-if="discountCodeValid === 'invalid'" style="color: red;line-height: 14px;font-style: italic;font-size: small;">
              <el-icon style="vertical-align: bottom;"><CloseBold /></el-icon>
              Discount code is invalid
            </span>

          </el-form-item>

          <!-- Credit Card Information -->
          <el-form-item label="Card Information" class="card-element">
            <div id="card-element" style="padding: 10px; border: 1px solid #d9d9d9; border-radius: 4px;"></div>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" native-type="submit">Join Waitlist</el-button>
          </el-form-item>
        </el-form>
        <p class="login-link">
          Already have an account? <el-button type="primary" link @click="$router.push('/user/login')">Sign in</el-button>
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
        discountCode: ''
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
      discountCodeValid: '',
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
      this.stripe = await loadStripe(import.meta.env.VITE_STRIPE_API_KEY);
      const elements = this.stripe.elements();
      this.cardElement = elements.create('card');
      this.cardElement.mount('#card-element');
    }, 2000);
  },
  methods: {
    handleJoinWaitlist() {
      this.$refs.waitlistForm.validate(async (valid) => {
        if (valid) {
          // Check if discountCodeValid is invalid and return
          if (this.waitlistForm.discountCode && this.discountCodeValid === 'invalid') {
            this.$message({
              message: 'Discount code is invalid',
              type: 'error'
            });
            return;
          }

          let paymentMethodId = null;

          // Create a payment method and handle the payment
          const { error, paymentMethod } = await this.stripe.createPaymentMethod({
            type: 'card',
            card: this.cardElement,
            billing_details: {
              name: this.waitlistForm.fullName,
              email: this.waitlistForm.email
            }
          });

          if (error) {
            this.$message({
              message: error.message,
              type: 'error'
            });
            return;
          }
          
          if (error) {
            this.$message({
              message: error.message || 'Card information is invalid',
              type: 'error'
            });
            return;
          }

          paymentMethodId = paymentMethod.id;

          axios.post(this.baseUrlForApiCall + 'join_waitlist', {
            ...this.waitlistForm,
            paymentMethodId: paymentMethodId
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
    handleDiscountCode() {
      if (this.waitlistForm.discountCode) {
        axios.post(this.baseUrlForApiCall + 'validate_discount_code', { discountCode: this.waitlistForm.discountCode })
          .then((response) => {
            if (response.data.valid) {
              this.discountCodeValid = 'valid';
            }
            else {
              this.discountCodeValid = 'invalid';
            }
          })
          .catch((error) => {
            this.discountCodeValid = 'invalid';
          });
      }
    },
    clearForm() {
      this.waitlistForm.fullName = '';
      this.waitlistForm.email = '';
      this.waitlistForm.password = '';
      this.waitlistForm.aboutYourself = '';
      this.waitlistForm.biggestProblem = '';
      this.waitlistForm.discountCode = '';
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
.login-link {
  text-align: center;
  margin-top: 20px;
}
</style>
