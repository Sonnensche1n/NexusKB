import { createApp } from 'vue'
import './style.less'
import App from './App.vue'
import router from './router/router'
import axios from './libs/axios'
import pinia from './store'
// 引入mock文件
import './mock' // mock 方式，正式发布时，注释掉该处即可

const app = createApp(App).use(router).use(axios).use(pinia)
app.config.globalProperties.$api = axios
app.mount('#app')
