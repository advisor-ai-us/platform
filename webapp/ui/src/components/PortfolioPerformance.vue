<template>
  <div class="portfolio-performance-page">
    <el-tabs v-model="activeTab" type="border-card">
      <el-tab-pane label="Analysis" name="analysis">
        <div class="analysis-content">
          <AnalysisComponent />
        </div>
      </el-tab-pane>
      <el-tab-pane label="Assets" name="assets">
        <div class="assets-content">
          <AssetsComponent />
        </div>
      </el-tab-pane>
      <el-tab-pane label="Accounts" name="accounts">
        <div class="accounts-content">
          <AccountComponent />
        </div>
      </el-tab-pane>
    </el-tabs>
    <ChatComponent :systemPrompt="systemPrompt" :advisorPersonalityName="advisorPersonalityName" />
  </div>
</template>

<script>
import AnalysisComponent from './portfolio-performance-sub-components/AnalysisComponent.vue';
import AssetsComponent from './portfolio-performance-sub-components/AssetsComponent.vue';
import AccountComponent from './portfolio-performance-sub-components/AccountComponent.vue';
import ChatComponent from './ChatComponent.vue';

export default {
  data() {
    return {
      activeTab: 'analysis',
      systemPrompt: '',
      advisorPersonalityName: 'portfolio-performance',
    };
  },
  components: {
    AnalysisComponent,
    AssetsComponent,
    AccountComponent,
    ChatComponent,
  },
  mounted() {},
  methods: {
    
  }
};
</script>
