<template>
    <div class="stock-recommendations">
      <el-card class="box-card" style="margin: 20px;">
        <div slot="header" class="clearfix stock-recommendations-header">
          <span>Stock Recommendations</span>
          <el-button type="primary" size="small" @click="openAddAssetPopup()" :icon="CirclePlus" round style="margin-left: 10px;">
            Add asset
          </el-button>
        </div>
        <el-row class="stock-recommendations-content">
          <el-col :span="24">
            <el-row v-for="(recommendation, index) in stockRecommendations" :key="index">
              <el-col :span="24">
                <el-divider></el-divider>
                <h4 style="margin: 0 10px;display: inline-block;" v-if="recommendation.recommendation">
                  Current {{ recommendation.recommendation }} Recommendation:  
                </h4>
                <h4 style="margin: 0 10px;display: inline-block;" v-else>
                  Being generated by AI
                </h4>
                
                <el-button :type="!recommendation.recommendation ? 'primary' : lowerCase(recommendation.recommendation) === 'buy' ? 'success' : lowerCase(recommendation.recommendation) === 'sell' ? 'danger' : 'warning'" size="small" round style="display: inline-block;" @click="goToSystemReportPage(recommendation.stock)">
                  {{ capitalize(recommendation.stock) }}  
                </el-button>

              </el-col>
            </el-row>
          </el-col>
        </el-row>
      </el-card>

      <!-- Add asset dialog -->
      <el-dialog title="Add asset" v-model="isAddAssetDialogVisible" width="30%">
        <el-form ref="addAssetForm" :model="addAssetForm" @submit.native.prevent="handleAddAsset" :rules="addAssetRules">
          <el-form-item label="Asset name" prop="stockName">
            <el-input v-model="addAssetForm.stockName" autocomplete="off"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" native-type="submit">Add Asset</el-button>
          </el-form-item>
        </el-form>
      </el-dialog>
    </div>
  </template>
  
  <script setup>
  import { CirclePlus } from '@element-plus/icons-vue';
  </script>

  <script>
  import axios from 'axios';

  export default {
    name: 'StockRecommendations',
    data() {
      return {
        stockRecommendations: [],
        isAddAssetDialogVisible: false,
        addAssetForm: {
          stockName: '',
        },
        addAssetRules: {
          stockName: [
            { required: true, message: 'Please enter a asset name', trigger: 'blur' },
          ],
        },
      };
    },
    mounted() {
      this.getStockRecommendations();
    },
    methods: {
      openAddAssetPopup() {
        this.isAddAssetDialogVisible = true;
      },
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
        //this.$router.push({ name: 'SystemReport', params: { stock: stock } });
        // go to this route with page refresh
        window.location.href = `/${stock}`;
      },
      handleAddAsset() {
        this.$refs.addAssetForm.validate((valid) => {
          if (valid) {
            const apiUrl = this.baseUrlForApiCall + 'stock/add';
            axios.post(apiUrl, {
              stockName: this.addAssetForm.stockName,
              userEmail: localStorage.getItem('email'),
              token: localStorage.getItem('token'),
            }, {
              headers: {
                'Authorization': null,
                'Content-Type': 'application/json',
              },
            })
              .then((response) => {
                this.$message({
                  message: 'Asset added successfully',
                  type: 'success',
                });
                this.isAddAssetDialogVisible = false;
                this.addAssetForm.stockName = '';
                this.getStockRecommendations();
              })
              .catch((error) => {
                console.error(error);
                this.$message({
                  message: error.response.data.error,
                  type: 'error',
                });
              });
          } else {
            console.log('Form validation failed');
            return false;
          }
        });
      },
    },
  }
  </script>