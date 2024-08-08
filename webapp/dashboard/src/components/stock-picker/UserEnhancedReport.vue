<template>
  <div>
    <AdvisorPersonalityTabsComponent :defaultActiveTab="`none`" />
    <div class="stock-picker-content" v-if="!isPageDisabled">
      <h2 class="stock-picker-content__title">
        <el-tooltip class="box-item" effect="dark" :content="`Go to ` + stock + ` report page`" placement="top-start">
          <el-link @click="goToSystemReportPage()" style="cursor: pointer;font-size: 1.25rem;vertical-align: bottom;">
            <el-icon><Back /></el-icon>
          </el-link>
        </el-tooltip>
        {{ capitalize(stock) }} AI analysis discussion
      </h2>

      <el-card class="stock-piker-graphs">
        <div slot="header" class="stock-picker-manage_pdf__header">
          <h3>Graphs</h3>
        </div>
        <div class="stock-picker-manage_pdf__content">
          <el-row>
            <el-col :span="24">
              <canvas id="projected-profit-chart" style="width: 100%; height: 400px;"></canvas>
            </el-col>
          </el-row>
        </div>
      </el-card>

      <el-card class="stock-picker-manage_pdf" style="margin-top: 20px;">
        <div slot="header" class="stock-picker-manage_pdf__header">
          <h3>Manage PDF</h3>
        </div>
        <div class="stock-picker-manage_pdf__content upload-form">
          <el-form>
            <el-form-item>
              <el-input size="small" placeholder="Heading below which the content of this PDF is sent to LLM" v-model="heading"></el-input>
            </el-form-item>
            <el-form-item label="Upload PDF">
              <input class="el-input__inner" type="file" @change="handleFiles" multiple accept="application/pdf" ref="fileInput" />
            </el-form-item>
            <el-form-item>
              <el-button size="small" type="primary" @click="uploadFiles" :loading="isRequestRunning" :disabled="isRequestRunning" round plain>Upload</el-button>
            </el-form-item>
          </el-form>
        </div>
        <div class="stock-picker-manage_pdf__content pdf-list">
          <el-divider content-position="left" style="margin: 20px 0 12px 0;"><h4 style="margin: 0;">Uploaded PDF</h4></el-divider>

          <el-table :data="allSavedPDFs" style="width: 100%">
            <el-table-column type="expand">
              <template #default="props">
                <div v-html="formattedPdfContent(props.row.pdf_content)"></div>
              </template>
            </el-table-column>
            <el-table-column prop="heading" label="Heading">
              <template #default="props">
                <div 
                  class="editable-heading"
                  contenteditable="true" 
                  @keypress.enter.prevent="handleEnterPress(props.row)" 
                  @blur="sendHeadingToServer(props.row)" 
                  @input="updateHeading" 
                  :ref="`editableHeading_` + props.row.id"
                >{{ props.row.heading || `null` }}</div>
              </template>
            </el-table-column>
            <el-table-column prop="pdf_name" label="PDF Name">
              <template #default="props">
                <!-- <el-link :underline="false" :href="props.row.pdf_path" target="_blank" type="primary">{{ props.row.pdf_name }}</el-link> -->
                 {{ props.row.pdf_name }}
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="Uploaded On" width="150">
              <template #default="props">
                {{ moment(props.row.created_at).format("MMM Do YYYY") }}
              </template>
            </el-table-column>
            <el-table-column prop="id" label="Action" width="100">
              <template #default="props">
                <el-button type="danger" size="small" link @click="mfToDeletePdf(props.row.id)">Delete</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-card>
      <el-card class="stock-picker-manage_pdf" style="margin-top: 20px;">
        <div slot="header" class="stock-picker-manage_pdf__header">
          <h3>Stock Report</h3>
        </div>
        <div class="stock-picker-manage_pdf__content">
          <el-row>
            <el-col :span="24">
              <h4 style="margin-bottom: 10px;">Recommendation:</h4>
              <p style="margin-top: 0;">{{ reportData.recommendation || 'not found' }}</p>
            </el-col>
            <el-col :span="24">
              <h4 style="margin-bottom: 10px;">Justification:</h4>
              <p style="margin-top: 0;">{{ reportData.justification || 'not found' }}</p>
            </el-col>
            <el-col :span="24">
              <h4 style="margin-bottom: 10px;">Net Present Value:</h4>
              <p style="margin-top: 0;">{{ reportData.net_present_value || 'not found' }}</p>
            </el-col>
            <el-col :span="24">
              <h4 style="margin-bottom: 10px;">Discount Rate:</h4>
              <p style="margin-top: 0;">{{ reportData.discount_rate || 'not found' }}</p>
            </el-col>
            <el-col :span="24">
              <h4 style="margin-bottom: 10px;">Comparison between NPV and Market value:</h4>
              <p style="margin-top: 0;">{{ reportData.comparison || 'not found' }}</p>
            </el-col>
          </el-row>
        </div>
      </el-card>
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
import { Back } from '@element-plus/icons-vue';

import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

export default {
  data() {
    return {
      isPageDisabled: false,
      stock: '',
      userFullName: localStorage.getItem('fullName') || '',
      heading: '',
      selectedFiles: null,
      isRequestRunning: false,
      allSavedPDFs: [],
      updatedHeadingValue: '',
      enterPressed: false,
      recommendation: '',
      justification: '',
      reportOfUid: null,
      reportData: {},

      // for chat component
      systemPrompt: '',
      pageName: 'stock-picker-discussion',
      projectedProfitChart: null,
    };
  },
  created() {
    this.moment = moment;
  },
  components: {
    Header,
    ChatComponent,
    AdvisorPersonalityTabsComponent,
    Back,
  },
  computed: {
    formattedPdfContent: function() {
        return function(pdfContent) {
            return pdfContent.replace(/\n/g, '<br>');
        }
    },
  },
  mounted() {
    this.stock = this.$route.params.stock;

    if (this.$route.params.reportOfUid) {
      this.reportOfUid = this.$route.params.reportOfUid;
    }

    // if token and email are not present in localStorage, redirect to login page
    if (!localStorage.getItem('token') || !localStorage.getItem('email')) {
      this.$router.push('/login');
    }

    // Get all saved PDFs for this report
    this.mfToGetAllSavedPDFs();

    this.mfToGetStockReport();

    // read data from event listener
    const eventName = "update-stock-report";
    this.emitter.on(eventName, (data) => {
      this.reportData = data.reportRow;

      this.makeProjectedProfitChart();
    });

    // read update-tab-settings event
    this.emitter.on('update-tab-settings', (tab) => {
      if (tab !== 'none') {
        this.isPageDisabled = true;
      }
    });
  },
  methods: {
    goToSystemReportPage() {
      this.$router.push({ name: 'SystemReport', params: { stock: this.stock } });
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
          reportOfUid: this.reportOfUid,
          token: localStorage.getItem('token'),
        },
        headers: {
          'Authorization': null,
          'Content-Type': 'application/json',
        },
      }).then((response) => {
        this.reportData = response.data.reportData;

        this.makeProjectedProfitChart();
      }).catch((error) => {
        console.error('Error:', error);
      });
    },
    mfToGetAllSavedPDFs: function() {
      const apiUrl = this.baseUrlForApiCall + "stock/get-pdfs";
      axios.get(apiUrl, {
        params: {
          stock: this.stock,
          userEmail: localStorage.getItem('email'),
          token: localStorage.getItem('token'),
        },
        headers: {
          'Authorization': null,
          'Content-Type': 'application/json',
        },
      }).then((response) => {
        console.log(response);
        this.allSavedPDFs = response.data;
      }).catch((error) => {
        console.error('Error:', error);
      });
    },
    handleFiles: function(event) {
      this.selectedFiles = event.target.files;

      // Validate file type - only PDFs
      for (let i = 0; i < this.selectedFiles.length; i++) {
        if (this.selectedFiles[i].type !== "application/pdf") {
          alert("Only PDF files are allowed.");
          this.selectedFiles = null;
          return; // Exit the function if a non-PDF file is encountered
        }
      }
    },
    uploadFiles: function() {
      if (!this.selectedFiles) {
        alert("Please select files first.");
        return;
      }

      this.isRequestRunning = true;

      // Prepare FormData
      const formData = new FormData();
      for (let i = 0; i < this.selectedFiles.length; i++) {
        formData.append("files", this.selectedFiles[i]);
      }
      formData.append("heading", this.heading);
      formData.append("stock", this.stock);
      formData.append("userEmail", localStorage.getItem('email'));
      formData.append("token", localStorage.getItem('token'));

      // Upload the files to the server
      const apiUrl = this.baseUrlForApiCall + "stock/upload-pdf";
      axios.post(apiUrl, formData, {
        headers: {
          'Authorization': null,
          "Content-Type": "multipart/form-data",
        },
      }).then((response) => {
        console.log(response);
        this.isRequestRunning = false;
        this.selectedFiles = null;
        this.heading = '';
        if (this.$refs.fileInput) {
          this.$refs.fileInput.value = ''; // Reset native file input
        }

        this.mfToGetAllSavedPDFs();
      }).catch((error) => {
        console.error('Error:', error);
        this.isRequestRunning = false;
      });
    },
    updateHeading(event) {
      this.updatedHeadingValue = event.target.innerText;
    },
    handleEnterPress(row) {
      this.enterPressed = true; // Set the flag
      this.sendHeadingToServer(row);
    },
    sendHeadingToServer: function(row) {
      if (this.enterPressed) {
        // Reset the flag and exit the method to avoid duplicate API call
        this.enterPressed = false;
        if (this.$refs[`editableHeading_${row.id}`]) {
          this.$refs[`editableHeading_${row.id}`].blur();
        }
        return;
      }

      const editedHeading = this.updatedHeadingValue.trim();

      const apiUrl = this.baseUrlForApiCall + "stock/pdf/update-heading";
      axios.post(apiUrl, {
        heading: editedHeading,
        id: row.id,
        userEmail: localStorage.getItem('email'),
        token: localStorage.getItem('token'),
        stock: this.stock,
      },
      {
        headers: {
          'Authorization': null,
          "Content-Type": "application/json",
        },
      }).then((response) => {
        this.updatedHeadingValue = '';
        this.$message({
          message: 'Heading updated successfully.',
          type: 'success'
        });
      }).catch((error) => {
        console.log('Error:', error);
      });

      if (this.$refs[`editableHeading_${row.id}`]) {
        this.$refs[`editableHeading_${row.id}`].blur();
      }
    },
    mfToDeletePdf: function(pdfId) {
      const self = this;
      this.$confirm('Are you sure you want to delete this PDF?', 'Warning', {
        confirmButtonText: 'OK',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }).then(() => {
        const apiUrl = this.baseUrlForApiCall + "stock/pdf/delete";
        axios.post(apiUrl, {
          id: pdfId,
          userEmail: localStorage.getItem('email'),
          token: localStorage.getItem('token'),
          stock: this.stock,
        },
        {
          headers: {
            'Authorization': null,
            "Content-Type": "application/json",
          },
        }).then((response) => {
          this.$message({
            message: 'PDF deleted successfully.',
            type: 'success'
          });
          this.mfToGetAllSavedPDFs();
        }).catch((error) => {
          console.log('Error:', error);
        });
      }).catch(() => {
        // Do nothing
      });
    },
    makeProjectedProfitChart() {
      const ctx = document.getElementById('projected-profit-chart').getContext('2d');

      // Destroy existing chart instance if it exists
      if (this.projectedProfitChart) {
        this.projectedProfitChart.destroy();
      }

      this.projectedProfitChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: this.reportData.graph_data_x_axis,
          datasets: [{
            label: 'The projected annual profit for the next 20 years.',
            data: this.reportData.graph_data_y_axis,
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgba(54, 162, 235, 1)',
            tension: 0.1
          }]
        },
        options: {
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
      });
    


    }
  },
};
</script>

<style>
.editable-heading {
    color: var(--el-color-primary);
    border-bottom: 2px dashed;
    display: inline;
}
.stock-picker-content {
    padding: 25px;
}
h2.stock-picker-content__title {
    margin: 0 0 15px 0;
    font-size: 1.17em;
    font-weight: 400;
}
.stock-picker-manage_pdf__content.upload-form {
    border: 1px solid #dcdfe6;
    padding: 15px;
    border-radius: 15px;
}
.stock-picker-manage_pdf__header h3 {
    margin: 0 0 10px 0;
    font-weight: 400;
}
</style>