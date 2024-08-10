<template>
  <div class="referral-management">
    <h2>Referral Management</h2>
    <el-button @click="generateNewCode" type="primary">Generate New Referral Code</el-button>
    <el-table :data="referralCodes" style="width: 100%">
      <el-table-column prop="code" label="Referral Code" />
      <el-table-column prop="signups" label="Signups" />
      <el-table-column prop="createdAt" label="Created At" />
    </el-table>
  </div>
</template>

<script>
export default {
  name: 'ReferralManagement',
  data() {
    return {
      referralCodes: [
        // Sample data, replace with actual data from your backend
        { code: 'ABC123', signups: 5, createdAt: '2023-04-15' },
        { code: 'XYZ789', signups: 2, createdAt: '2023-04-20' },
      ],
    };
  },
  methods: {
    generateNewCode() {
      // Implement the logic to generate a new referral code
      // This should typically involve a backend API call
      console.log('Generating new referral code');
      // After generating, update the referralCodes array with the new code
    },
  },
};
</script>
