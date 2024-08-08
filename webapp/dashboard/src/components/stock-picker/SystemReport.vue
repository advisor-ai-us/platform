<template>
  <div>
    <AdvisorPersonalityTabsComponent :defaultActiveTab="`none`" />
    <div class="stock-picker-content" v-if="!isPageDisabled">
      <h2 class="stock-picker-content__title">
        {{ capitalize(stock) }} system report
      </h2>

      <el-row>
        <el-col :span="16">
          <el-card class="stock-picker-manage_pdf" style="margin: 20px 10px 0 0;">
            <div slot="header" class="stock-picker-manage_pdf__header">
              <h3>Stock Report</h3>
            </div>
            <div class="stock-picker-manage_pdf__content">
              <el-row>
                <el-col :span="24">
                  <h4 style="margin-bottom: 10px;">Recommendation:</h4>
                  <p style="margin-top: 0;">{{ stockReport.recommendation || 'not found' }}</p>
                </el-col>
                <el-col :span="24">
                  <h4 style="margin-bottom: 10px;">Reason:</h4>
                  <p style="margin-top: 0;">{{ stockReport.justification || 'not found' }}</p>
                </el-col>
                <el-col :span="24">
                  <h4 style="margin-bottom: 10px;">Net Present Value:</h4>
                  <p style="margin-top: 0;">{{ stockReport.net_present_value || 'not found' }}</p>
                </el-col>
                <el-col :span="24">
                  <h4 style="margin-bottom: 10px;">Discount Rate:</h4>
                  <p style="margin-top: 0;">{{ stockReport.discount_rate || 'not found' }}</p>
                </el-col>
                <el-col :span="24">
                  <h4 style="margin-bottom: 10px;">Comparison between NPV and Market value:</h4>
                  <p style="margin-top: 0;">{{ stockReport.comparison || 'not found' }}</p>
                </el-col>
              </el-row>
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="stock-picker-manage_pdf" style="margin: 20px 0 0 10px;">
            <el-button type="primary" style="margin: 0 auto 20px auto; display: block;" round @click="goToDiscussPage()">Discuss this report with AI analyst</el-button>

            <div slot="header" class="stock-picker-manage_pdf__header">
              <h3>User enhanced Report</h3>
            </div>
            <div class="stock-picker-manage_pdf__content">
              <el-row>
                <el-col :span="24">
                  <el-row v-for="(item, index) in enhancedReport" :key="index">
                    <el-col :span="24">
                      <el-link @click="goToEnhancedReportPage(item.id)" style="cursor: pointer;">
                        <h4 style="margin: 5px 0;">{{ item.name }} - <span style="font-weight: 400;"> {{ item.recommendation }} </span></h4>
                      </el-link>                     
                    </el-col>
                  </el-row>
                </el-col>
              </el-row>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    <ChatComponent :systemPrompt="systemPrompt" :pageName="pageName" :stock="stock" v-if="!isPageDisabled" />
  </div>
</template>

<script>
import axios from 'axios';
import moment from 'moment';
import Header from '../Header.vue';
import ChatComponent from '../ChatComponent.vue';
import AdvisorPersonalityTabsComponent from '../AdvisorPersonalityTabsComponent.vue';

export default {
  data() {
    return {
      isPageDisabled: false,
      stock: '',
      userFullName: localStorage.getItem('fullName') || '',
      heading: '',
      recommendation: '',
      justification: '',
      enhancedReport: [],
      stockReport: {},

      // for chat component
      systemPrompt: '',
      pageName: 'stock-picker-system-report',
    };
  },
  created() {
    this.moment = moment;
  },
  components: {
    Header,
    ChatComponent,
    AdvisorPersonalityTabsComponent,
  },
  computed: {
    
  },
  mounted() {
    this.stock = this.$route.params.stock;

    // if token and email are not present in localStorage, redirect to login page
    if (!localStorage.getItem('token') || !localStorage.getItem('email')) {
      this.$router.push('/login');
    }

    this.mfToGetStockReport();

    // read update-tab-settings event
    this.emitter.on('update-tab-settings', (tab) => {
      if (tab !== 'none') {
        this.isPageDisabled = true;
      }
    });
  },
  methods: {
    goToDiscussPage() {
      this.$router.push({ name: 'DiscussStockReport', params: { stock: this.stock } });
    },
    goToEnhancedReportPage(reportOfUid) {
      this.$router.push({ name: 'DiscussStockReport', params: { stock: this.stock, reportOfUid: reportOfUid } });
    },
    capitalize(str) {
      return str.charAt(0).toUpperCase() + str.slice(1);
    },
    mfToGetStockReport() {
      const apiUrl = this.baseUrlForApiCall + "stock/report";
      axios.get(apiUrl, {
        params: {
          stock: this.stock,
          userEmail: localStorage.getItem('email'),
          reportOfUid: 1,
          token: localStorage.getItem('token'),
        },
        headers: {
          'Authorization': null,
          'Content-Type': 'application/json',
        },
      }).then((response) => {
        this.stockReport = response.data.reportData;

        this.enhancedReport = response.data.enhancedReportList;
      }).catch((error) => {
        console.error('Error:', error);
      });
    },
  },
};
</script>

<style>
.stock-picker-content {
    padding: 25px;
}
h2.stock-picker-content__title {
    margin: 0 0 15px 0;
    font-size: 1.17em;
    font-weight: 400;
}
</style>