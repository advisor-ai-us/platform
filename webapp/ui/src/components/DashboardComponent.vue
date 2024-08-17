<script>
import axios from 'axios';
import ChatComponent from './ChatComponent.vue';

export default {
  data() {
    return {
      dashboardData: [],
      systemPrompt: '',
      advisorPersonalityName: 'dashboard',
    };
  },
  components: {
    ChatComponent
  }, 
  mounted() {
    // get user email from local storage and set it to userEmail, if not available then reload the page
    this.userEmail = localStorage.getItem('email');
    if (!this.userEmail) {
      // go to login page
      this.$router.push({ name: 'LoginPage' });
    }

    // fetch data from the server
    const eventName = "update-dashboard-boxes";
    this.emitter.on(eventName, (data) => {
      this.dashboardData = data;
    });

    // this.systemPrompt = "You are a financial coach called coolFin. You are going to need to create a user profile for a user. The information you need to collect is Name, Age, Gender, Location, Monthly expenses, Monthly income, Education, Marital status, Children, Financial institutions where he has an account, allow the user to enter the assets he has at those financial institutions. Allow the user to ask questions about which assets he has at what financial institution. Allow the user to transfer assets from one FI to another. If the user starts to give non-sensical answers be kind to the user and tell the user they can answer later. Maintain a jovial positive personality with the user. \n Let the user know that when you ask the user a question he can give the answer to that question or ask a question based on the profile thats already created. Also with each question show an approximate percentage of profile already completed. \n Ask the user one question at a time. And you become the financial coach called 'Cool Fin' and introduce yourself as such. \n Return response only in JSON format. The first key of the JSON will be 'MsgForUser' and the second key of JSON will be 'memory'. In the memory JSON return to me the key and value pair with action for the last question. The action would be add/edit/delete. For example, the final response should be in the format like: \n { \"MsgForUser\": \"Could you please tell me your gender? (Profile completion: 10%)\", \"memory\": { \"Name\": \"Raj\", \"Action\": \"add\" }}.";

    // // Add facts to the system prompt
    // this.systemPrompt += "\n [USER_FACTS]";

    // // In the system promopt let the AI know about the user dashboard
    // this.systemPrompt += "\n\nThe third key of json will be dashboard. The user has a dashboard that has 4 boxes in it. I am now going to give you the current content of the 4 boxes. You can add or update the content of these boxes. The 4 default boxes are goal, recommendations, assets/liabilities and income/expense. To make changes to the content of these boxes inside the JSON return me dashboard box name, box content, and action. So you may return dashboard goal buy a car add. If you do not have enough information you can return to me goal:not enough information, recommendations: not enough information, assets/liabilities: not enough information, income/expense: not enough information. \n [DASHBOARD_DATA]";
  },
  methods: {
    myToGetDashboardData(key) {
      let value = 'not enough information';
      if (Array.isArray(this.dashboardData)) {
        this.dashboardData.forEach((item) => {
          if(item.key === key) {
            value = item.value;
          }
        });
      }
      return value;
    }
  }
};
</script>

<template>
  <div class="common-layout ai-assistant-webpage">
    <el-container>
      <el-main>
        <div class="layout-container">
          <div class="grid-container">
            <div class="grid-item">
              <h4>Goals:</h4>
              <div class="goal-list">
                <div class="goal-item">
                  {{ myToGetDashboardData('goal') }}
                </div>
              </div>
            </div>
            <div class="grid-item">
              <h4>Recommendations:</h4>
              <div class="recommendation-list">
                <div class="recommendation-item">
                  {{ myToGetDashboardData('recommendations') }}
                </div>
              </div>
            </div>
            <div class="grid-item">
              <h4>Assets/Liabilities:</h4>
              <div class="asset-list">
                <div class="asset-item">
                  {{ myToGetDashboardData('assets/liabilities') }}
                </div>
              </div>
            </div>
            <div class="grid-item">
              <h4>Income/Expenses:</h4>
              <div class="income-expense-list">
                <div class="income-expense-item">
                  {{ myToGetDashboardData('income/expense') }}
                </div>
              </div>
            </div>
          </div>
          <ChatComponent :systemPrompt="systemPrompt" :advisorPersonalityName="advisorPersonalityName" />
        </div>
      </el-main>
    </el-container>
  </div>
</template>