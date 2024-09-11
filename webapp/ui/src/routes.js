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
import ConnectWithPeoplePageComponent from './components/ConnectWithPeoplePageComponent.vue';
import JoinCreaterComponent from './components/JoinCreaterComponent.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePageComponent
  },
  {
    path: '/:keyword',
    name: 'ConnectWithPeoplePage',
    component: ConnectWithPeoplePageComponent
  },
  {
    path: '/get/demo',
    name: 'DemoPage',
    component: DemoPageComponent
  },
  { 
    path: '/page/advisor-personality', 
    name: 'AdvisorPersonalityPage',
    component: AdvisorPersonalityTabs 
  },
  {
    path: '/user/login',
    name: 'LoginPage',
    component: LoginCt
  },
  {
    path: '/user/reset-password',
    name: 'ResetPassword',
    component: ResetPasswordComponent
  },
  {
    path: '/user/waitlist',
    name: 'JoinWaitlist',
    component: JoinWaitlistComponent
  },
  {
    path: '/join/creator',
    name: 'JoinCreaterPage',
    component: JoinCreaterComponent
  },
  {
    path: '/stock/:stock',
    name: 'SystemReport',
    component: SystemReport
  },
  {
    path: '/stock/:stock/discuss/:reportOfUid?',
    name: 'DiscussStockReport',
    component: UserEnhancedReport
  },
  {
    path: '/membership/pricing',
    name: 'Pricing',
    component: PricingComponent
  }
];

const router = createRouter({
    history: createWebHistory(),
    routes: routes,
});
export default router;