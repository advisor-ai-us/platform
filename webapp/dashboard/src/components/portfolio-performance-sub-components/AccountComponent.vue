<template>
    <div>
        <el-button type="primary" @click="addAccount" size="small" style="float: right;">Add Account</el-button>
          <el-table :data="accounts">
            <el-table-column prop="name" label="Name"></el-table-column>
            <el-table-column prop="account_number" label="Account number"></el-table-column>
            <el-table-column prop="is_it_active" label="Status"></el-table-column>

            <el-table-column label="Actions">
              <template #default="scope">
                <el-button-group>
                  <el-button size="small" type="warning" @click="editAccount(scope.$index, scope.row)">E</el-button>
                  <el-button size="small" type="danger" @click="deleteAccount(scope.$index, scope.row)">D</el-button>
                </el-button-group>
              </template>
            </el-table-column>
        </el-table>

        <!-- Account Dialog -->
        <el-dialog :title="accountFormTitle" v-model="visibleAccountDialog" width="30%">
            <el-form :model="accountFormFields" ref="accountForm" :rules="accountRules" label-width="100px">
                <el-form-item label="Name" prop="name">
                    <el-input v-model="accountFormFields.name"></el-input>
                </el-form-item>
                <el-form-item label="A/c number" prop="account_number">
                    <el-input v-model="accountFormFields.account_number"></el-input>
                </el-form-item>
                <el-form-item label="Status" prop="is_it_active">
                    <el-select v-model="accountFormFields.is_it_active">
                        <el-option label="Active" value="active"></el-option>
                        <el-option label="Inactive" value="inactive"></el-option>
                    </el-select>
                </el-form-item>
                <el-form-item style="margin-bottom: 0;">
                    <el-button type="primary" @click="saveAccount">Save</el-button>
                    <el-button @click="visibleAccountDialog = false">Cancel</el-button>
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
            accounts: [],
            visibleAccountDialog: false,
            accountFormType: 'add',
            accountFormTitle: 'Add Account',
            accountFormFields: {
                name: '',
                account_number: '',
                is_it_active: 'active',
            },
            accountRules: {
                name: [
                { required: true, message: 'Please enter account name', trigger: 'blur' },
                ],
                account_number: [
                { required: true, message: 'Please enter account number', trigger: 'blur' },
                ],
                is_it_active: [
                { required: true, message: 'Please select account status', trigger: 'change' },
                ],
            },
        };
    },
    mounted() {
        this.fetchAccounts();
    },
    methods: {
        addAccount() {
            this.accountFormType = 'add';
            this.accountFormTitle = 'Add Account';
            this.visibleAccountDialog = true;
        },
        editAccount(index, row) {
            this.accountFormType = 'edit';
            this.accountFormTitle = 'Edit Account';
            this.accountFormFields = { ...row };
            this.visibleAccountDialog = true;
        },
        deleteAccount(index, row) {
            this.$confirm('Are you sure you want to delete this account?', 'Warning', {
                confirmButtonText: 'OK',
                cancelButtonText: 'Cancel',
                type: 'warning',
            }).then(() => {
                const apiUrl = this.baseUrlForApiCall + 'accounts/delete';
                axios.post(apiUrl, { 
                    id: row.id,
                    email: localStorage.getItem('email'),
                    token: localStorage.getItem('token')
                }).then(() => {
                    this.accounts.splice(index, 1);
                    this.$message({
                        type: 'success',
                        message: 'Account deleted successfully',
                    });
                });
            });
        },
        saveAccount() {
            this.$refs.accountForm.validate((valid) => {
                if (valid) {
                    if (this.accountFormType === 'add') {
                        const apiUrl = this.baseUrlForApiCall + 'accounts/add';
                        axios.post(apiUrl, {
                            email: localStorage.getItem('email'),
                            token: localStorage.getItem('token'),
                            name: this.accountFormFields.name,
                            account_number: this.accountFormFields.account_number,
                            is_it_active: this.accountFormFields.is_it_active,
                        }).then((response) => {
                            this.fetchAccounts();
                            this.visibleAccountDialog = false;
                            this.$message({
                                type: 'success',
                                message: 'Account added successfully',
                            });
                        });
                    } else {
                        const apiUrl = this.baseUrlForApiCall + 'accounts/edit';
                        axios.post(apiUrl, {
                            email: localStorage.getItem('email'),
                            token: localStorage.getItem('token'),
                            id: this.accountFormFields.id,
                            name: this.accountFormFields.name,
                            account_number: this.accountFormFields.account_number,
                            is_it_active: this.accountFormFields.is_it_active,
                        }).then((response) => {
                            this.fetchAccounts();
                            this.visibleAccountDialog = false;
                            this.$message({
                                type: 'success',
                                message: 'Account updated successfully',
                            });
                        });
                    }

                    // Clear the form fields
                    this.accountFormFields.name = '';
                    this.accountFormFields.account_number = '';
                    this.accountFormFields.is_it_active = 'active';
                }
            });
        },
        fetchAccounts() {
            const apiUrl = this.baseUrlForApiCall + 'accounts';
            axios.get(apiUrl,{
                params: {
                    email: localStorage.getItem('email'),
                    token: localStorage.getItem('token'),
                },
            }).then((response) => {
                this.accounts = response.data;
            });
        },
    },
};
</script>