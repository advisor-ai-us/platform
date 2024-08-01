import { createRouter, createWebHistory } from "vue-router";
import AdvisorPersonalityTabs from './components/AdvisorPersonalityTabsComponent.vue';
import LoginCt from './components/LoginComponent.vue';
import HomePageComponent from './components/HomePageComponent.vue';
import JoinWaitlistComponent from './components/JoinWaitlistComponent.vue';
import DiscussionComponent from './components/stock-picker/DiscussionComponent.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePageComponent
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
    path: '/waitlist',
    name: 'JoinWaitlist',
    component: JoinWaitlistComponent
  },
  {
    path: '/:stock/discuss',
    name: 'Discussion',
    component: DiscussionComponent
  }
];

const router = createRouter({
    history: createWebHistory(),
    routes: routes,
});
export default router;