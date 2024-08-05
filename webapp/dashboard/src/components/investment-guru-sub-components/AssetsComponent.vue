<template>
    <div>
      <!-- <el-slider v-model="sliderValue" :min="sliderMinValue" :max="sliderMaxValue" :show-stops="true" :show-tooltip="true" tooltip-visible="always" @input="filterAssetsByDate" :format-tooltip="formatTooltip"></el-slider> -->

        <el-button type="primary" @click="addAsset" size="small" style="float: right;">Add Asset</el-button>
          <el-table :data="assets">
            <el-table-column prop="asset" label="Asset"></el-table-column>
            <el-table-column prop="qty" label="Qty"></el-table-column>
            <el-table-column prop="price" label="Price"></el-table-column>
            <el-table-column prop="value" label="Value"></el-table-column>
            <el-table-column prop="account" label="Account"></el-table-column>
            <el-table-column label="Actions">
              <template #default="scope">
                <el-button-group>
                  <el-button size="small" type="warning" @click="editAsset(scope.$index, scope.row)">E</el-button>
                  <el-button size="small" type="danger" @click="deleteAsset(scope.$index, scope.row)">D</el-button>
                </el-button-group>
              </template>
            </el-table-column>
        </el-table>

        <!-- Asset Dialog -->
        <el-dialog :title="assetFormTitle" v-model="visibleAssetDialog" width="30%">
            <el-form :model="assetFormFields" ref="assetForm" :rules="assetRules" label-width="80px">
                <el-form-item label="Asset" prop="asset">
                    <el-input v-model="assetFormFields.asset"></el-input>
                </el-form-item>
                <el-form-item label="Qty" prop="qty">
                    <el-input v-model="assetFormFields.qty"></el-input>
                </el-form-item>
                <el-form-item label="Price" prop="price">
                    <el-input v-model="assetFormFields.price"></el-input>
                </el-form-item>
                <el-form-item label="Value" prop="value">
                    <el-input v-model="assetFormFields.value"></el-input>
                </el-form-item>
                <el-form-item label="Account" prop="account">
                    <el-input v-model="assetFormFields.account"></el-input>
                </el-form-item>
                <el-form-item style="margin-bottom: 0;">
                    <el-button type="primary" @click="saveAsset">Save</el-button>
                    <el-button @click="visibleAssetDialog = false">Cancel</el-button>
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
      assets: [],
      visibleAssetDialog: false,
      assetFormType: 'add',
      assetFormTitle: 'Add Asset',
      assetFormFields: {
        asset: '',
        qty: '',
        price: '',
        value: '',
        account: ''
      },
      assetRules: {
        asset: [
          { required: true, message: 'Please enter the asset name', trigger: 'blur' }
        ],
        qty: [
          { required: true, message: 'Please enter the quantity', trigger: 'blur' }
        ],
        price: [
          { required: true, message: 'Please enter the price', trigger: 'blur' }
        ],
        value: [
          { required: true, message: 'Please enter the value', trigger: 'blur' }
        ],
      },
      sliderMinValue: 0,
      sliderMaxValue: 0,
      sliderValue: 0,
    };
  },
  mounted() {
    // Fetch assets data from the API
    this.getAssets();

    const eventName = "update-analysis-page";
    this.emitter.on(eventName, (data) => {
      this.assets = data.assets.filter((row) => {
        return row.row_end === null;
      });
    });
  },
  methods: {
    getAssets() {
        const apiUrl = this.baseUrlForApiCall + 'assets';
        axios.get(apiUrl, {
            params: {
            email: localStorage.getItem('email'),
            token: localStorage.getItem('token')
            }
        })
        .then((response) => {
            this.assets = response.data.rows.filter((row) => {
                return row.row_end === null;
            });

            // Convert timestamps to days since epoch
            this.sliderMinValue = this.timestampToDays(response.data.slider_info.slider_min);
            this.sliderMaxValue = this.timestampToDays(response.data.slider_info.slider_max);
            this.sliderValue = this.sliderMaxValue;
        })
        .catch((error) => {
            console.error('Error fetching assets:', error);
        });
    },
    timestampToDays(timestamp) {
      return Math.floor(timestamp / (1000 * 60 * 60 * 24));
    },
    daysToTimestamp(days) {
      return days * 1000 * 60 * 60 * 24;
    },
    formatTooltip(val) {
      const timestamp = this.daysToTimestamp(val);
      return new Date(timestamp).toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' });
    },
    addAsset() {
      this.assetFormTitle = 'Add Asset';
      this.assetFormType = 'add';
      this.visibleAssetDialog = true;
    },
    editAsset(index, row) {
      this.assetFormTitle = 'Edit Asset';
      this.assetFormType = 'edit';
      this.visibleAssetDialog = true;

      // Set the form values
      this.assetFormFields.asset_id = row.id;
      this.assetFormFields.asset = row.asset;
      this.assetFormFields.qty = row.qty;
      this.assetFormFields.price = row.price;
      this.assetFormFields.value = row.value;
      this.assetFormFields.account = row.account;

    },
    saveAsset() {
      this.$refs.assetForm.validate((valid) => {
        if (valid) {
          let apiUrl = '';
          let data = {};
          if (this.assetFormType === 'add') {
            apiUrl = this.baseUrlForApiCall + 'assets/add';
            data = {
              email: localStorage.getItem('email'),
              token: localStorage.getItem('token'),
              asset: this.assetFormFields.asset,
              qty: this.assetFormFields.qty,
              price: this.assetFormFields.price,
              value: this.assetFormFields.value,
              account: this.assetFormFields.account
            };            
          } else {
            apiUrl = this.baseUrlForApiCall + 'assets/edit';
            data = {
              email: localStorage.getItem('email'),
              token: localStorage.getItem('token'),
              id: this.assetFormFields.asset_id,
              asset: this.assetFormFields.asset,
              qty: this.assetFormFields.qty,
              price: this.assetFormFields.price,
              value: this.assetFormFields.value,
              account: this.assetFormFields.account
            };
          }

          axios.post(apiUrl, data)
          .then((response) => {
            this.getAssets();
            this.visibleAssetDialog = false;

            this.$message({
              message: 'Asset saved successfully',
              type: 'success'
            });

            // Clear the form fields
            this.assetFormFields.asset = '';
            this.assetFormFields.qty = '';
            this.assetFormFields.price = '';
            this.assetFormFields.value = '';
            this.assetFormFields.account = '';
          })
          .catch((error) => {
            console.error('Error adding asset:', error);
          });
        }
        else {
          return false;
        }
      });
    },
    deleteAsset(index, row) {
      // set prompt to confirm delete
      this.$confirm('Are you sure you want to delete this asset?', 'Warning', {
        confirmButtonText: 'OK',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }).then(() => {
        // delete the asset
        axios.post(this.baseUrlForApiCall + 'assets/delete', {
          email: localStorage.getItem('email'),
          token: localStorage.getItem('token'),
          id: row.id
        })
        .then((response) => {
          this.getAssets();
          this.$message({
            message: 'Asset deleted successfully',
            type: 'success'
          });
        })
        .catch((error) => {
          console.error('Error deleting asset:', error);
        });
      }).catch(() => {
        // do nothing
      });
    },
    filterAssetsByDate() {
      // const [minDay, maxDay] = this.sliderValue;
      // const minTimestamp = this.daysToTimestamp(minDay);
      // const maxTimestamp = this.daysToTimestamp(maxDay);
      // this.filteredAssets = this.assets.filter(asset => {
      //   const assetTimestamp = new Date(asset.date).getTime();
      //   return assetTimestamp >= minTimestamp && assetTimestamp <= maxTimestamp;
      // });
      console.log('Filtering assets by date', this.sliderValue);
    },
  }
};
</script>