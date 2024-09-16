<template>
    <div class="homepage-container">
        <header class="header">
            <div class="header-content">
                <div class="logo-title">
                <el-link href="/" :underline="false">
                    <img src="/logo.png" alt="TalkTo Logo" class="logo">
                    <h1 class="site-title">TalkTo</h1>
                </el-link>
                </div>
                <nav class="nav-links">
                    <el-button type="primary" @click="$router.push('/user/login')">Login</el-button>
                    <el-button type="success" @click="$router.push('/user/waitlist')">Join Waitlist</el-button>
                    <el-button type="info" @click="$router.push('/membership/pricing')">Pricing</el-button>
                </nav>
            </div>
        </header>
        <main class="main-content">
            <el-card class="join-creator-card">
                <template #header>
                    <div class="card-header">
                        <h2 style="margin: 0;">Join as a Creater</h2>
                    </div>
                </template>
                
                <el-form :model="createrForm" :rules="createrRules" ref="createrForm" label-position="top" @submit.native.prevent="handleCreaterForm" :inline="true">
                    <el-form-item label="Full Name" prop="fullName">
                        <el-input v-model="createrForm.fullName" autocomplete="off"></el-input>
                    </el-form-item>
                    <el-form-item label="Email" prop="email">
                        <el-input v-model="createrForm.email" autocomplete="off"></el-input>
                    </el-form-item>
                    <el-form-item label="Password" prop="password">
                        <el-input v-model="createrForm.password" type="password" autocomplete="off"></el-input>
                    </el-form-item>
                    <el-form-item label="Age" prop="age">
                        <el-input v-model="createrForm.age" autocomplete="off"></el-input>
                    </el-form-item>                
                    <el-form-item label="Gender" prop="gender">
                        <el-select v-model="createrForm.gender" placeholder="Select gender">
                            <el-option label="Male" value="male"></el-option>
                            <el-option label="Female" value="female"></el-option>
                        </el-select>
                    </el-form-item>
                    <el-form-item label="Education" prop="education">
                        <el-input v-model="createrForm.education" autocomplete="off"></el-input>
                    </el-form-item>
                    <el-form-item label="Occupation" prop="occupation">
                        <el-input v-model="createrForm.occupation" autocomplete="off"></el-input>
                    </el-form-item>
                    <el-form-item label="Location" prop="location">
                        <el-input v-model="createrForm.location" autocomplete="off"></el-input>
                    </el-form-item>
                    <el-form-item label="Languages" prop="languages">
                        <el-checkbox-group v-model="createrForm.languages">
                            <el-checkbox label="English" value="English"></el-checkbox>
                            <el-checkbox label="Spanish" value="Spanish"></el-checkbox>
                            <el-checkbox label="French" value="French"></el-checkbox>
                            <el-checkbox label="German" value="German"></el-checkbox>
                            <el-checkbox label="Chinese" value="Chinese"></el-checkbox>
                            <el-checkbox label="Japanese" value="Japanese"></el-checkbox>
                            <el-checkbox label="Other" value="Other"></el-checkbox>
                        </el-checkbox-group>
                    </el-form-item>
                    <el-form-item label="Profile Photo" prop="profilePhoto">
                        <el-upload
                            class="avatar-uploader"
                            action="#"
                            :auto-upload="false"
                            :on-change="handlePhotoChange"
                            :show-file-list="false">
                            <img v-if="imageUrl" :src="imageUrl" class="avatar">
                            <el-icon v-else class="avatar-uploader-icon">
                                <Plus />
                            </el-icon>
                        </el-upload>
                    </el-form-item>
                    <el-form-item style="margin: 0;width: 100%;">
                        <el-button type="primary" native-type="submit">Join as Creater</el-button>
                    </el-form-item>
                </el-form>
                <p class="login-link">
                    Already have an account? <el-button type="primary" link @click="$router.push('/user/login')">Sign in</el-button>
                </p>
            </el-card>
        </main>
        <footer class="footer">
            <p>&copy; 2024 TalkTo AI. All rights reserved.</p>
        </footer>
    </div>
</template>

<script>
import axios from 'axios';
import { Plus } from '@element-plus/icons-vue';
export default {
    data() {
        return {
            createrForm: {
                fullName: '',
                email: '',
                password: '',
                age: '',
                gender: '',
                education: '',
                occupation: '',
                location: '',
                languages: [],
            },
            createrRules: {
                fullName: [
                    { required: true, message: 'Please enter your full name', trigger: 'blur' },
                ],
                email: [
                    { required: true, message: 'Please enter your email', trigger: 'blur' },
                    { type: 'email', message: 'Please enter a valid email', trigger: ['blur', 'change'] }
                ],
                password: [
                    { required: true, message: 'Please enter your password', trigger: 'blur' },
                    { min: 6, message: 'Password length should be at least 6 characters', trigger: 'blur' }
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
                // profilePhoto: [
                //     { required: true, message: 'Please upload a profile photo', trigger: 'change' }
                // ]
            },
            imageUrl: '',
            profilePhoto: null,
        }
    },
    components: {
        Plus
    },
    methods: {
        handleCreaterForm() {
            this.$refs.createrForm.validate((valid) => {
                if (valid) {
                    if (!this.profilePhoto) {
                        this.$message({
                            message: 'Please upload a profile photo',
                            type: 'error'
                        });
                        return;
                    }

                    const formData = new FormData();
                    formData.append('fullName', this.createrForm.fullName);
                    formData.append('email', this.createrForm.email);
                    formData.append('password', this.createrForm.password);
                    formData.append('age', this.createrForm.age);
                    formData.append('gender', this.createrForm.gender);
                    formData.append('education', this.createrForm.education);
                    formData.append('occupation', this.createrForm.occupation);
                    formData.append('location', this.createrForm.location);
                    formData.append('languages', JSON.stringify(this.createrForm.languages));
                    formData.append('profilePhoto', this.profilePhoto);

                    // Assuming you have an API endpoint for creator registration
                    const apiURL = this.baseUrlForApiCall + 'register_creator';
                    axios.post(apiURL, formData, {
                        headers: {
                            'Content-Type': 'multipart/form-data'
                        }
                    })
                    .then(response => {
                        this.$message({
                            message: 'Creator registered successfully',
                            type: 'success'
                        });
                        // Redirect to LoginPage page
                        this.$router.push('/user/login');
                    })
                    .catch(error => {
                        this.$message({
                            message: 'Registration failed: ' + error.response.data.error,
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
        }
    }
}
</script>

<style>
.join-creator-card {
    max-width: 550px;
    margin: 0 auto;
    padding: 20px;
}
.join-creator-card .el-form-item--label-top .el-form-item__label {
  margin-bottom: 0;
  line-height: 17px;
}
.card-element .el-form-item__content {
    display: block;
}
.join-creator-card .el-input {
  --el-input-width: 220px;
}
.join-creator-card .el-select {
  --el-select-width: 220px;
}
.avatar-uploader .el-upload {
    border: 2px dashed #d9d9d9;
    border-radius: 6px;
    cursor: pointer;
    position: relative;
    overflow: hidden;
}
.avatar-uploader .el-upload:hover {
    border-color: #409EFF;
}
i.el-icon.avatar-uploader-icon {
    font-size: 2rem;
    padding: 20px;
}
.avatar {
    width: 80px;
    height: 80px;
    display: block;
}
.login-link {
    text-align: center;
    margin-top: 20px;
}
</style>