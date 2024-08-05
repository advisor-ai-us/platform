<template>
    <div class="advisor-personality-tabs">
      <el-tabs v-model="activePersonality" @tab-click="handleTabClick">
        <el-tab-pane name="Dashboard" label="Dashboard"></el-tab-pane>
        <el-tab-pane name="Taxes" label="Tax Advisor"></el-tab-pane>
        <el-tab-pane name="Investments" label="Investment Guru"></el-tab-pane>
        <el-tab-pane name="Expenses" label="Expense Analyst"></el-tab-pane>
        <el-tab-pane name="Retirement" label="Retirement Planner"></el-tab-pane>
        <el-tab-pane name="Legacy" label="Legacy Specialist"></el-tab-pane>
        <el-tab-pane name="Files" label="Document Keeper"></el-tab-pane>
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
  import InvestmentGuru from './InvestmentGuru.vue';
  import ExpenseAnalyst from './ExpenseAnalyst.vue';
  import RetirementPlanner from './RetirementPlanner.vue';
  import LegacySpecialist from './LegacySpecialist.vue';
  import DocumentKeeper from './DocumentKeeper.vue';
  import ManageOpenAiComponent from './ManageOpenAiComponent.vue';
  
  export default {
    data() {
      return {
        activePersonality: 'Taxes', // Default active personality
        userFullName: localStorage.getItem('fullName') || '',
      };
    },
    components: {
      ArrowDown,
      Dashboard,
      TaxAdvisor,
      InvestmentGuru,
      ExpenseAnalyst,
      RetirementPlanner,
      LegacySpecialist,
      DocumentKeeper,
      ManageOpenAiComponent,
    },
    computed: {
      currentPersonalityComponent() {
        switch (this.activePersonality) {
          case 'Dashboard': return Dashboard;
          case 'Taxes': return TaxAdvisor;
          case 'Investments': return InvestmentGuru;
          case 'Expenses': return ExpenseAnalyst;
          case 'Retirement': return RetirementPlanner;
          case 'Legacy': return LegacySpecialist;
          case 'Files': return DocumentKeeper;
          default: return null;
        }
      },
      downloadDB() {
        const token = localStorage.getItem('token');
        return `${this.baseUrlForApiCall}download_db?token=${token}`;
      },
    },
    mounted() {
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
      validateToken(token) {
        // Validate the token
        // If the token is invalid, redirect to the login page
        // Otherwise, continue
        axios.post(`${this.baseUrlForApiCall}validate_token`, { token })
          .then((response) => {
            if (response.data.valid) {
              // Token is valid
              // Save user details to local storage
              localStorage.setItem('email', response.data.userEmail);
              localStorage.setItem('fullName', response.data.fullName);

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
        this.activePersonality = tab.name;
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

