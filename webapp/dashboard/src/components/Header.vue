<template>
    <el-row class="advisorai-header">
        <el-col class="advisorai-header__title" :span="20">
            <h1>Advisor AI</h1>
        </el-col>
        <el-col class="advisorai-header__user" :span="4">
            <el-dropdown @command="handleUserDropdownCommand" style="float: right; margin: 7px 10px 0 0;">
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
        </el-col>
    </el-row>
</template>

<script>
import { ArrowDown } from '@element-plus/icons-vue';
import ManageOpenAiComponent from './ManageOpenAiComponent.vue';
export default {
    data() {
        return {
            userFullName: localStorage.getItem('fullName') || '',
        };
    },
    components: {
        ArrowDown,
        ManageOpenAiComponent,
    },
    computed: {
        downloadDB() {
            const token = localStorage.getItem('token');
            return `${this.baseUrlForApiCall}download_db?token=${token}`;
        },
    },
    methods: {
        handleUserDropdownCommand(command) {
            if (command === 'logout') {
                localStorage.clear();
                this.$router.push('/login');
            }
        },
    },
};
</script>

<style>
.advisorai-header {
    border-bottom: 1px solid #dcdfe6;
    height: 40px;
}
.advisorai-header__title h1 {
    font-size: 1.25rem;
    margin: 10px 0 0 25px;
}
</style>