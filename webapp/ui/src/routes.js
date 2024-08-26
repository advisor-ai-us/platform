import { createRouter, createWebHistory } from "vue-router";
import AdvisorPersonalityTabs from './components/AdvisorPersonalityTabsComponent.vue';
import LoginCt from './components/LoginComponent.vue';
import ResetPasswordComponent from './components/ResetPasswordComponent.vue';
import HomePageComponent from './components/HomePageComponent.vue';
import JoinWaitlistComponent from './components/JoinWaitlistComponent.vue';
import UserEnhancedReport from './components/stock-picker/UserEnhancedReport.vue';
import SystemReport from './components/stock-picker/SystemReport.vue';
import DemoPageComponent from './components/DemoPageComponent.vue';
import PricingComponent from './components/PricingComponent.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePageComponent
  },
  {
    path: '/demo',
    name: 'DemoPage',
    component: DemoPageComponent
  },
  { 
    path: '/advisor-personality', 
    name: 'AdvisorPersonalityPage',
    component: AdvisorPersonalityTabs 
  },
  {
    path: '/login',
    name: 'LoginPage',
    component: LoginCt
  },
  {
    path: '/reset-password',
    name: 'ResetPassword',
    component: ResetPasswordComponent
  },
  {
    path: '/waitlist',
    name: 'JoinWaitlist',
    component: JoinWaitlistComponent
  },
  {
    path: '/:stock',
    name: 'SystemReport',
    component: SystemReport
  },
  {
    path: '/:stock/discuss/:reportOfUid?',
    name: 'DiscussStockReport',
    component: UserEnhancedReport
  },
  {
    path: '/pricing',
    name: 'Pricing',
    component: PricingComponent
  }
];

const router = createRouter({
    history: createWebHistory(),
    routes: routes,
});
export default router;