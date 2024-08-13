<template>
  <div class="referral-management" style="padding: 0 10px;">
    <h2 style="display: inline-block; margin-bottom: 10px;">Referral Management</h2>
    <el-button @click="mfToVisibleRefferalForm()" type="primary" size="small" round style="display: inline-block; margin: 0 0 10px 10px;" :disabled="isReferralCodeGenerating">
      Generate New Referral Code
    </el-button>
    <!-- <el-icon class="is-loading" v-if="isReferralCodeGenerating" style="margin-left: 10px;color:#ff0000;">
      <Loading />
    </el-icon>
    <span v-if="isReferralCodeGenerating" style="color:#ff0000;vertical-align: text-bottom;font-style: italic;">
      Generating new referral code...
    </span> -->
    <el-table :data="referralCodes" style="width: 100%">
      <el-table-column prop="code" label="Referral Code" />
      <el-table-column prop="signups" label="Signups" />
      <el-table-column prop="createdAt" label="Created At" />
    </el-table>

    <!-- Referral Code Dialog -->
    <el-dialog
      title="Referral Code"
      v-model="isReferralDialogVisible"
      width="30%"
      :before-close="() => isReferralDialogVisible = false"
    >
      <el-form label-position="top">
        <el-form-item label="Referral Code">
          <el-input v-model="newReferralCode" autocomplete="off">
            <!-- <template #append>
              <el-button type="primary" @click="createRandomCode(8)">Generate</el-button>
            </template> -->
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="generateNewCode()" :disabled="isReferralCodeGenerating">Save</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>
  </div>
</template>

<script setup>
import { Loading } from '@element-plus/icons-vue';
</script>

<script>
import axios from 'axios';

export default {
  name: 'ReferralManagement',
  data() {
    return {
      isReferralCodeGenerating: false,
      referralCodes: [],
      isReferralDialogVisible: false,
      newReferralCode: '',
    };
  },
  mounted() {
    // Fetch referral codes from the backend
    const apiUrl = this.baseUrlForApiCall + 'referral-codes';
    axios.get(apiUrl, {
        params: {
          email: localStorage.getItem('email'),
          token: localStorage.getItem('token'),
        },
      }
    )
    .then((response) => {
      this.referralCodes = response.data;
    })
    .catch((error) => {
      console.error('Error fetching referral codes:', error);
    });
  },
  methods: {
    mfToVisibleRefferalForm() {
      this.isReferralDialogVisible = true;
    },
    createRandomCode(length) {
      const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
      let result = '';
      const charactersLength = characters.length;
      for (let i = 0; i < length; i++) {
        result += characters.charAt(Math.floor(Math.random() * charactersLength));
      }

      this.newReferralCode = result;
      return result;
    },
    generateNewCode() {
      if (!this.newReferralCode) {
        this.$message({
          message: 'Please enter a referral code',
          type: 'warning',
        });
        return;
      }

      this.isReferralCodeGenerating = true;
      const newReferralCode = this.newReferralCode;
      const apiUrl = this.baseUrlForApiCall + 'referral-codes';
      axios.post(apiUrl, { 
          code: newReferralCode,
          email: localStorage.getItem('email'),
          token: localStorage.getItem('token'),
        })
        .then((response) => {
          this.referralCodes.push(
            { 
              code: newReferralCode, 
              signups: 0, 
              createdAt: new Date().toISOString().slice(0, 19).replace('T', ' ') 
            }
          );

          this.$message({
            message: 'New referral code generated successfully',
            type: 'success',
          });
        })
        .catch((error) => {
          console.error('Error generating new referral code:', error);
        })
        .finally(() => {
          this.isReferralCodeGenerating = false;
          this.isReferralDialogVisible = false;
        });
    },
  },
};
</script>

<style>
header.el-dialog__header.show-close {
    padding: 5px !important;
    margin-bottom: 10px;
}
</style>
