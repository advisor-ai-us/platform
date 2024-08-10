import { createApp } from 'vue'
import './style.css'
import App from './router.vue'
const rootVueApp = createApp(App);

import router from "./routes";
rootVueApp.use(router);

import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
rootVueApp.use(ElementPlus);

/**
 * Install Font Awesome with VueJS 3
 * Ref: https://dev.to/sabbirsobhani/font-awesome-with-vuejs-3-59ee
 */
import { library } from "@fortawesome/fontawesome-svg-core";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { fas } from "@fortawesome/free-solid-svg-icons";
library.add(fas);
import { fab } from "@fortawesome/free-brands-svg-icons";
library.add(fab);
import { far } from "@fortawesome/free-regular-svg-icons";
library.add(far);
import { dom } from "@fortawesome/fontawesome-svg-core";
dom.watch();
import '@fortawesome/fontawesome-free/css/all.css';

rootVueApp.component("font-awesome-icon", FontAwesomeIcon);

/**
 * Install vue3 cookie
 */
import VueCookies from "vue3-cookies";
rootVueApp.use(VueCookies);

/**
 * Install vue3 signature pad for sign policies and ROI
 */
import VueSignaturePad from "vue-signature-pad";
rootVueApp.use(VueSignaturePad);

/**
 * Event bus
 * Ref: https://stackoverflow.com/questions/63471824/vue-js-3-event-bus
 * Where is the event bus is used?
 *  When the active tab changes in the change page then the Ct is informed that the active tab has changed so that it can
 *  set its own caret position correctly.
 * To search places where it has been used search in vscode for the word "emitter"
 */
import mitt from "mitt";
const emitter = mitt();
rootVueApp.config.globalProperties.emitter = emitter;

// set base url
if (process.env.NODE_ENV === 'development') {
    rootVueApp.config.globalProperties.baseUrlForApiCall = 'http://localhost:3003/acr/';
} else {
    rootVueApp.config.globalProperties.baseUrlForApiCall = 'https://www.advisorai.us/acr/';
}

rootVueApp.mount('#app')
