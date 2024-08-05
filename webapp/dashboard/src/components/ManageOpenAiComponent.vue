<template>
    <div>
      <el-button @click="openAiModal" link>Manage OpenAI</el-button>
      
      <el-dialog
        title="Set your own OpenAI API key and Model"
        v-model="dialogVisible"
        :append-to-body="true"
        width="30%">
        <el-form :model="openAiForm" ref="openAiForm" :rules="openAiFormRules" @submit.native.prevent="saveSettings">
          <el-form-item label="API Key" :label-width="formLabelWidth" prop="apiKey">
            <el-input v-model="openAiForm.apiKey" autocomplete="off"></el-input>
          </el-form-item>
          <el-form-item label="Model" :label-width="formLabelWidth" prop="model">
            <el-select v-model="openAiForm.model" placeholder="Select">
              <el-option label="GPT-4o-mini" value="gpt-4o-mini"></el-option>
              <el-option label="GPT-4o" value="gpt-4o"></el-option>
              <el-option label="GPT-4-turbo" value="gpt-4-turbo"></el-option>
              <el-option label="GPT-4" value="gpt-4"></el-option>
              <el-option label="GPT-3.5-turbo" value="gpt-3.5-turbo"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button @click="dialogVisible = false">Cancel</el-button>
            <el-button type="primary" native-type="submit">Save</el-button>
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
        openAiForm: {
          apiKey: '',
          model: ''
        },
        openAiFormRules: {
          apiKey: [
            { required: true, message: 'Please enter your OpenAI API key', trigger: 'blur' }
          ],
          model: [
            { required: true, message: 'Please select a model', trigger: 'change' }
          ]
        },
        formLabelWidth: '80px',
        userEmail: '',
      };
    },
    mounted() {
      this.userEmail = localStorage.getItem('email');
      
      let interval = setInterval(() => {
        console.log('Checking for user email:', this.userEmail);
        if (this.userEmail) {
          console.log('User email found:', this.userEmail);
          this.getSavedSettings();
          clearInterval(interval);
        } else {
          // reload the page
          location.reload();
        }
      }, 2000);
    },
    methods: {
      openAiModal() {
        this.dialogVisible = true;
        console.log('OpenAI Modal opened');
      },
      getSavedSettings() {
        const apiUri = this.baseUrlForApiCall + 'settings';
        axios.post(apiUri, {
          token: localStorage.getItem('token'),
          email: this.userEmail
        })
        .then((response) => {
          this.openAiForm.apiKey = response.data.openai_api_key;
          this.openAiForm.model = response.data.openai_model;
        })
        .catch((error) => {
          console.log(error);
        });
      },
      saveSettings() {
        this.$refs.openAiForm.validate((valid) => {
          if (valid) {
            const apiUri = this.baseUrlForApiCall + 'settings/openai';
            axios.post(apiUri, {
              apiKey: this.openAiForm.apiKey,
              model: this.openAiForm.model,
              token: localStorage.getItem('token'),
              email: localStorage.getItem('email')
            })
            .then((response) => {
              this.$message({
                message: 'Settings saved successfully',
                type: 'success'
              });
              this.dialogVisible = false;
            })
            .catch((error) => {
              console.log(error);
            });
          } else {
            console.log('Error! Please enter valid data');
            return false;
          }
        });
      }
    }


    
  };
  </script>
