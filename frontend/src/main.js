import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import * as echarts from 'echarts/core'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import { createApp } from 'vue'
import VChart from 'vue-echarts'

import App from './App.vue'
import { i18n } from './i18n'
import router from './router'
import './style.css'
import './theme'

echarts.use([LineChart, BarChart, GridComponent, TooltipComponent, CanvasRenderer])

const app = createApp(App)
app.component('VChart', VChart)
app.use(router)
app.use(ElementPlus)
app.use(i18n)
app.mount('#app')
