<template>
  <div class="advisor-personality-tabs" style="padding: 0 10px;">
    <el-tabs v-model="activePersonality" @tab-click="handleTabClick">
      <el-tab-pane v-for="tab in enabledTabs" :key="tab.name" :name="tab.name" :label="tab.label"></el-tab-pane>
    </el-tabs>
    <component :is="currentPersonalityComponent"></component>

    <div class="user-details">
      <el-dropdown @command="handleUserDropdownCommand">
        <span class="el-dropdown-link">
          <el-avatar size="small" src="/user-icon.png" style="vertical-align: middle;"></el-avatar>
          {{ userFullName }}
          <el-icon class="el-icon--right" style="vertical-align: middle;">
            <arrow-down />
          </el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item>
              <el-link :href="downloadDB" :underline="false">Download DB</el-link>
            </el-dropdown-item>
            <el-dropdown-item><ManageOpenAiComponent /></el-dropdown-item>
            <el-dropdown-item><SettingsComponent @settings-updated="updateTabSettings" /></el-dropdown-item>
            <el-dropdown-item><ShareComponent /></el-dropdown-item>
            <el-dropdown-item command="logout">Logout</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { ArrowDown } from '@element-plus/icons-vue';
import Dashboard from './DashboardComponent.vue';
import TaxAdvisor from './TaxAdvisor.vue';
import PortfolioPerformance from './PortfolioPerformance.vue';
import ExpenseAnalyst from './ExpenseAnalyst.vue';
import RetirementPlanner from './RetirementPlanner.vue';
import LegacySpecialist from './LegacySpecialist.vue';
import DocumentKeeper from './DocumentKeeper.vue';
import ManageOpenAiComponent from './ManageOpenAiComponent.vue';
import SettingsComponent from './SettingsComponent.vue';
import StockRecommendations from './StockRecommendations.vue';
import ReferralManagement from './ReferralManagement.vue';
import ShareComponent from './ShareComponent.vue';

export default {
  data() {
    return {
      //activePersonality: 'Dashboard',
      activePersonality: '',
      userFullName: localStorage.getItem('fullName') || '',
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
      ],
    };
  },
  components: {
    ArrowDown,
    Dashboard,
    TaxAdvisor,
    PortfolioPerformance,
    ExpenseAnalyst,
    RetirementPlanner,
    LegacySpecialist,
    DocumentKeeper,
    ManageOpenAiComponent,
    SettingsComponent,
    StockRecommendations,
    ReferralManagement,
    ShareComponent
  },
  props: {
    defaultActiveTab: {
      type: String,
      default: '',
      required: false,
    },
  },
  computed: {
    enabledTabs() {
      const enabledTabs = this.tabSettings.filter(tab => tab.enabled);
      console.log('enabledTabs:', this.defaultActiveTab);
      if (enabledTabs.length > 0 && this.defaultActiveTab !== 'none') {
        this.activePersonality = enabledTabs[0].name;
      }
      return enabledTabs;
    },
    currentPersonalityComponent() {
      switch (this.activePersonality) {
        case 'Dashboard': return Dashboard;
        case 'Taxes': return TaxAdvisor;
        case 'portfolio': return PortfolioPerformance;
        case 'Expenses': return ExpenseAnalyst;
        case 'Retirement': return RetirementPlanner;
        case 'Legacy': return LegacySpecialist;
        case 'Files': return DocumentKeeper;
        case 'StockRecommendations': return StockRecommendations;
        case 'referral': return ReferralManagement;
        default: return null;
      }
    },
    downloadDB() {
      const token = localStorage.getItem('token');
      return `${this.baseUrlForApiCall}download_db?token=${token}`;
    },
  },
  mounted() {
    this.loadTabSettings();
    // Check if the user is logged in
    // If not, redirect to the login page
    const token = localStorage.getItem('token');
    if (!token) {
      this.$router.push({ name: 'LoginPage' });
    } else {
      this.validateToken(token);
    }
  },
  methods: {
    loadTabSettings() {
      const apiUrl = this.baseUrlForApiCall + 'get_tab_settings';
      axios.post(apiUrl, {
        email: localStorage.getItem('email'),
        token: localStorage.getItem('token')
      })
      .then((response) => {
        if (response.data.settings) {
          this.tabSettings = JSON.parse(response.data.settings);
        } else {
          // If no settings are found, enable where name=StockRecommendations and portfolio
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
    updateTabSettings(newSettings) {
      this.tabSettings = newSettings;
      if (!this.enabledTabs.find(tab => tab.name === this.activePersonality)) {
        this.activePersonality = this.enabledTabs[0].name;
      }
      
      const apiUrl = this.baseUrlForApiCall + 'save_tab_settings';
      axios.post(apiUrl, {
        email: localStorage.getItem('email'),
        token: localStorage.getItem('token'),
        settings: JSON.stringify(this.tabSettings)
      })
      .then(() => {
        console.log('Tab settings saved successfully');
      })
      .catch((error) => {
        console.error('Error saving tab settings:', error);
      });
    },
    validateToken(token) {
      // Validate the token
      // If the token is invalid, redirect to the login page
      // Otherwise, continue
      axios.post(`${this.baseUrlForApiCall}validate_token`, { token })
        .then((response) => {
          if (response.data.valid) {
            // Token is valid
            // Save user details to local storage
            //localStorage.setItem('email', response.data.userEmail);
            //localStorage.setItem('fullName', response.data.fullName);

            // Set the user's full name
            this.userFullName = response.data.fullName;
          } else {
            // Token is invalid
            // Redirect to the login page
            this.$router.push({ name: 'LoginPage' });
          }
        })
        .catch((error) => {
          // Redirect to the login page
          this.$router.push({ name: 'LoginPage' });
        });
    },
    handleTabClick(tab) {
      //this.$router.push({ name: 'AdvisorPersonalityPage' });
      this.activePersonality = tab.name;

      // Call a event to update the tab
      this.emitter.emit('update-tab-settings', this.activePersonality);
    },
    handleUserDropdownCommand(command) {
      if(command === 'logout') {
        // Clear local storage
        localStorage.removeItem('token');
        localStorage.removeItem('email');
        localStorage.removeItem('fullName');

        // Redirect to the login page
        this.$router.push({ name: 'LoginPage' });
      }
    },
  }
};
</script>

<style>
li.el-dropdown-menu__item {
    display: block;
}
li.el-dropdown-menu__item button.el-button.is-link {
    width: 100%;
    display: block;
    text-align: left;
    padding: 5px 0;
}
</style>