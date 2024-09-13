<template>
  <div class="user-page-container">
    <el-card class="header-card">
        <Header />
    </el-card>
    
    <div class="edit-profile-container">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card class="profile-card">
            <div class="profile-header">
              <el-avatar :size="150" :src="imageUrl || '/default-avatar.png'" />
              <h2>{{ creatorForm.fullName }}</h2>
              <p>@{{ creatorForm.username }}</p>
            </div>
            <el-upload 
                v-if="activeTab === 'profile'"
                class="avatar-uploader"
                action="#"
                :auto-upload="false"
                :on-change="handlePhotoChange"
                :show-file-list="false">
                <el-button type="primary" size="small">Change Profile Photo</el-button>
            </el-upload>
          </el-card>
        </el-col>
        <el-col :span="16">
          <el-card class="edit-form-card">
            <el-tabs v-model="activeTab">
                <el-tab-pane label="Edit Profile" name="profile">
                    <el-form :model="creatorForm" :rules="creatorRules" ref="creatorForm" label-position="top" @submit.native.prevent="handleCreatorForm">
                        <el-row :gutter="20">
                            <el-col :span="12">
                            <el-form-item label="Full Name" prop="fullName">
                                <el-input v-model="creatorForm.fullName" />
                            </el-form-item>
                            </el-col>
                            <el-col :span="12">
                            <el-form-item label="Email" prop="email">
                                <el-input v-model="creatorForm.email" disabled />
                            </el-form-item>
                            </el-col>
                        </el-row>
                        <el-row :gutter="20">
                            <el-col :span="12">
                            <el-form-item label="Age" prop="age">
                                <el-input v-model="creatorForm.age" />
                            </el-form-item>
                            </el-col>
                            <el-col :span="12">
                            <el-form-item label="Gender" prop="gender">
                                <el-select v-model="creatorForm.gender" placeholder="Select gender">
                                <el-option label="Male" value="male"></el-option>
                                <el-option label="Female" value="female"></el-option>
                                <el-option label="Other" value="other"></el-option>
                                </el-select>
                            </el-form-item>
                            </el-col>
                        </el-row>
                        <el-form-item label="Education" prop="education">
                            <el-input v-model="creatorForm.education" />
                        </el-form-item>
                        <el-form-item label="Occupation" prop="occupation">
                            <el-input v-model="creatorForm.occupation" />
                        </el-form-item>
                        <el-form-item label="Location" prop="location">
                            <el-input v-model="creatorForm.location" />
                        </el-form-item>
                        <el-form-item label="Languages" prop="languages">
                            <el-checkbox-group v-model="creatorForm.languages">
                            <el-checkbox label="English" value="English"></el-checkbox>
                            <el-checkbox label="Spanish" value="Spanish"></el-checkbox>
                            <el-checkbox label="French" value="French"></el-checkbox>
                            <el-checkbox label="German" value="German"></el-checkbox>
                            <el-checkbox label="Chinese" value="Chinese"></el-checkbox>
                            <el-checkbox label="Japanese" value="Japanese"></el-checkbox>
                            <el-checkbox label="Other" value="Other"></el-checkbox>
                            </el-checkbox-group>
                        </el-form-item>
                        <el-form-item>
                            <el-button type="primary" native-type="submit">Save Changes</el-button>
                        </el-form-item>
                        </el-form>
                </el-tab-pane>
                <el-tab-pane label="Improve Prompt" name="prompt">
                    <ImprovePromptComponent />
                </el-tab-pane>
            </el-tabs>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { Plus } from '@element-plus/icons-vue';
import Header from './Header.vue';
import ImprovePromptComponent from './ImprovePromptComponent.vue';

export default {
  data() {
    return {
      creatorForm: {
        fullName: '',
        email: '',
        age: '',
        gender: '',
        education: '',
        occupation: '',
        location: '',
        languages: [],
        username: '',
      },
      creatorRules: {
        fullName: [
          { required: true, message: 'Please enter your full name', trigger: 'blur' },
        ],
        age: [
          { required: true, message: 'Please enter your age', trigger: 'blur' },
        ],
        gender: [
          { required: true, message: 'Please select your gender', trigger: 'change' }
        ],
        education: [
          { required: true, message: 'Please enter your education', trigger: 'blur' }
        ],
        occupation: [
          { required: true, message: 'Please enter your occupation', trigger: 'blur' }
        ],
        location: [
          { required: true, message: 'Please enter your location', trigger: 'blur' }
        ],
        languages: [
          { type: 'array', required: true, message: 'Please select at least one language', trigger: 'change' }
        ],
      },
      imageUrl: '',
      profilePhoto: null,
      activeTab: 'prompt',
    }
  },
  components: {
    Plus,
    Header,
    ImprovePromptComponent
  },
  mounted() {
    this.fetchCreatorProfile();
  },
  methods: {
    fetchCreatorProfile() {
      const apiUrl = this.baseUrlForApiCall + 'get_creator_profile';
      axios.get(apiUrl, {
        params: {
          email: localStorage.getItem('email'),
          token: localStorage.getItem('token')
        }
      })
      .then(response => {
        const profile = response.data;
        this.creatorForm = {
          fullName: profile.full_name,
          email: profile.email,
          age: parseInt(profile.age),
          gender: profile.gender,
          education: profile.education,
          occupation: profile.occupation,
          location: profile.location,
          languages: profile.languages,
          username: profile.username,
        };
        this.imageUrl = 'data:image/png;base64,' + profile.profile_photo;
      })
      .catch(error => {
        console.error('Error fetching creator profile:', error);
        this.$message.error('Failed to fetch creator profile');

        this.$router.push({ name: 'LoginPage' });
      });
    },
    handleCreatorForm() {
      this.$refs.creatorForm.validate((valid) => {
        if (valid) {
          if (!this.profilePhoto && !this.imageUrl) {
            this.$message({
              message: 'Please upload a profile photo',
              type: 'error'
            });
            return;
          }

          const formData = new FormData();
          formData.append('token', localStorage.getItem('token'));
          formData.append('fullName', this.creatorForm.fullName);
          formData.append('email', this.creatorForm.email);
          formData.append('age', this.creatorForm.age);
          formData.append('gender', this.creatorForm.gender);
          formData.append('education', this.creatorForm.education);
          formData.append('occupation', this.creatorForm.occupation);
          formData.append('location', this.creatorForm.location);
          formData.append('languages', JSON.stringify(this.creatorForm.languages));
          formData.append('username', this.creatorForm.username);
          if (this.profilePhoto) {
            formData.append('profilePhoto', this.profilePhoto);
          }

          const apiUrl = this.baseUrlForApiCall + 'update_creator_profile';
          axios.post(apiUrl, formData, {
            headers: {
              'Content-Type': 'multipart/form-data'
            },
            params: {
              email: localStorage.getItem('email'),
              token: localStorage.getItem('token')
            }
          })
          .then(response => {
            this.$message({
              message: 'Creator profile updated successfully',
              type: 'success'
            });
          })
          .catch(error => {
            this.$message({
              message: 'Profile update failed: ' + error.response.data.error,
              type: 'error'
            });
          });
        } else {
          this.$message({
            message: 'Please fill in all required fields correctly',
            type: 'error'
          });
          return false;
        }
      });
    },
    handlePhotoChange(file) {
      this.profilePhoto = file.raw;
      this.imageUrl = URL.createObjectURL(file.raw);

      //console.log('Profile photo:', this.imageUrl);
    }
  }
}
</script>

<style>

</style>