// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'
import storage from './vuex/store'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import $ from '../build/jquery-vendor'
import 'font-awesome/css/font-awesome.min.css'
import './assets/myicon/iconfont.css'
import './assets/myicon/iconfont.js'
import VueDirectiveImagePreviewer from 'vue-directive-image-previewer'
import 'vue-directive-image-previewer/dist/assets/style.css'
Vue.use(VueDirectiveImagePreviewer)
require("./common/locwin");

Vue.config.productionTip = false

Vue.use(ElementUI)

router.beforeEach((to, from, next) => {
  sessionStorage.setItem('lastRoute', from.path)
  if (to.path == '/login') {
    sessionStorage.removeItem('user');
  }
  if(from.path =='/login'){
    next()
  }
  let user = JSON.parse(sessionStorage.getItem('user'));
  if (!user && to.path != '/login') {
    next({ path: '/login' })
  } else {
    next()
  }
})

new Vue({
  el: '#app',
  router,
  storage,
  components: { App },
  template: '<App/>'
})
