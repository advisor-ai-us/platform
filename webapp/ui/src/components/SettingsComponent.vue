<template>
    <div>
      <el-button @click="openSettingsModal" link>Settings</el-button>
      
      <el-dialog
        title="Tab Settings"
        v-model="dialogVisible"
        :append-to-body="true"
        width="30%">
        <el-form>
          <el-form-item v-for="tab in tabSettings" :key="tab.name" :label="tab.label">
            <el-tag :type="tab.name === 'referral' || tab.name === 'portfolio' ? 'success' : 'warning'" effect="dark" size="small" round style="margin-right: 10px;">
              {{ tab.name === 'referral' || tab.name === 'portfolio' ? 'Beta' : 'Alpha' }}
            </el-tag>
            <el-switch v-model="tab.enabled" @change="saveSettings"></el-switch>
          </el-form-item>
        </el-form>
      </el-dialog>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        dialogVisible: false,
        tabSettings: [
          { name: 'Dashboard', label: 'Dashboard', enabled: false },
          { name: 'Taxes', label: 'Tax Advisor', enabled: false },
          { name: 'portfolio', label: 'Portfolio Performance', enabled: false },
          { name: 'Expenses', label: 'Expense Analyst', enabled: false },
          { name: 'Retirement', label: 'Retirement Planner', enabled: false },
          { name: 'Legacy', label: 'Legacy Specialist', enabled: false },
          { name: 'Files', label: 'Document Keeper', enabled: false },
          { name: 'StockRecommendations', label: 'Stock Recommendations', enabled: false },
          { name: 'referral', label: 'Referral Management', enabled: false },
          { name: 'MentalHealth', label: 'Mental Health Advisor', enabled: false },
        ],
      };
    },
    mounted() {
      this.loadSettings();
    },
    methods: {
      openSettingsModal() {
        this.dialogVisible = true;
      },
      loadSettings() {
        const apiUrl = this.baseUrlForApiCall + 'get_tab_settings';
        axios.post(apiUrl, {
          email: localStorage.getItem('email'),
          token: localStorage.getItem('token')
        })
        .then((response) => {
          if (response.data.settings) {
            this.tabSettings = JSON.parse(response.data.settings);
          } else {
            this.tabSettings.forEach((tab) => {
              if (tab.name === 'StockRecommendations' || tab.name === 'portfolio') {
                tab.enabled = true;
              }
            });
          }
        })
        .catch((error) => {
          console.error('Error loading tab settings:', error);
        });
      },
      saveSettings() {
        const apiUrl = this.baseUrlForApiCall + 'save_tab_settings';
        axios.post(apiUrl, {
          email: localStorage.getItem('email'),
          token: localStorage.getItem('token'),
          settings: JSON.stringify(this.tabSettings)
        })
        .then(() => {
          this.$emit('settings-updated', this.tabSettings);
        })
        .catch((error) => {
          console.error('Error saving tab settings:', error);
        });
      },
    },
  };
  </script>