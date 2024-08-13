<template>
    <div>
      <el-button @click="openShareModal" link>Share</el-button>
      
      <el-dialog
        title="Share account"
        v-model="dialogVisible"
        :append-to-body="true"
        width="30%">
        <el-form :model="openShareForm" ref="openShareForm" :rules="openShareFormRules" @submit.native.prevent="saveSettings">
          <el-form-item label="Email Addresses" :label-width="formLabelWidth" prop="emailAddresses">
            <el-input v-model="openShareForm.emailAddresses" autocomplete="off"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button @click="dialogVisible = false">Cancel</el-button>
            <el-button type="primary" native-type="submit">Share</el-button>
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
        openShareForm: {
          emailAddresses: '',
        },
        openShareFormRules: {
          emailAddresses: [
            { required: true, message: 'Please enter email addresses', trigger: 'blur' }
          ]
        },
        formLabelWidth: '135px',
        userEmail: '',
      };
    },
    mounted() {
      this.userEmail = localStorage.getItem('email');
    },
    methods: {
      openShareModal() {
        this.dialogVisible = true;
      },
      saveSettings() {
        this.$refs.openShareForm.validate((valid) => {
          if (valid) {
            console.log('Email Addresses:', this.openShareForm.emailAddresses);
            this.dialogVisible = false;
          } else {
            console.log('Error! Please enter valid data');
            return false;
          }
        });
      }
    }


    
  };
  </script>
