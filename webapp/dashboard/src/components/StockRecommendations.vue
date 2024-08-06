<template>
    <div class="stock-recommendations">
      <el-card class="box-card" style="margin: 20px;">
        <div slot="header" class="clearfix stock-recommendations-header">
          <span>Stock Recommendations</span>
        </div>
        <el-row class="stock-recommendations-content">
          <el-col :span="24">
            <el-row v-for="(recommendation, index) in stockRecommendations" :key="index">
              <el-col :span="24">
                <el-divider></el-divider>
                <h4 style="margin: 0 10px;display: inline-block;">
                  Current {{ recommendation.recommendation }} Recommendation:  
                </h4>
                
                <el-button :type="lowerCase(recommendation.recommendation) === 'buy' ? 'success' : lowerCase(recommendation.recommendation) === 'sell' ? 'danger' : 'warning'" size="small" round style="display: inline-block;" @click="goToSystemReportPage(recommendation.stock)">
                  {{ capitalize(recommendation.stock) }}  
                </el-button>

              </el-col>
            </el-row>
          </el-col>
        </el-row>
      </el-card>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  export default {
    name: 'StockRecommendations',
    data() {
      return {
        stockRecommendations: [],
      };
    },
    mounted() {
      this.getStockRecommendations();
    },
    methods: {
      capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
      },
      lowerCase(str) {
        return str.toLowerCase();
      },
      getStockRecommendations() {
        const apiUrl = this.baseUrlForApiCall + '/stock/recommendations';
        axios.get(apiUrl, {
          params: {
            userEmail: localStorage.getItem('email'),
            token: localStorage.getItem('token'),
          },
          headers: {
            'Authorization': null,
            'Content-Type': 'application/json',
          },
        })
          .then((response) => {
            this.stockRecommendations = response.data.recommendations;
          })
          .catch((error) => {
            console.error(error);
          });
      },
      goToSystemReportPage(stock) {
        this.$router.push({ name: 'SystemReport', params: { stock: stock } });
      },
    },
  }
  </script>
  
  <style scoped>
  /* Add your component styles here */
  </style>