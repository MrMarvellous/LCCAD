import Vue from 'vue'
import Router from 'vue-router'
import vuex from 'vuex'


Vue.use(Router)
Vue.use(vuex)

const Login = resolve => require(['../components/User/login.vue'], resolve)
const Register = resolve => require(['../components/User/register.vue'], resolve)
const AdminIndex = resolve => require(['../components/User/adminPage.vue'], resolve)
const DocIndex = resolve => require(['../components/Doctor/index.vue'], resolve)
const home = resolve => require(['../components/Home.vue'], resolve)
const addPatient = resolve => require(['../components/Doctor/addPatient.vue'], resolve)

const docInfo = resolve => require(['../components/Doctor/docInfo.vue'], resolve)

const diagPage = resolve => require(['../components/Diagnosis/diagnosisPage.vue'], resolve)
const selectPage = resolve => require(['../components/Diagnosis/selectPic.vue'], resolve)
const ctDetail = resolve => require(['../components/Diagnosis/showImages.vue'], resolve)

const ctImages = resolve => require(['../components/CTDiagnosis/showImages.vue'], resolve)
const ctResult = resolve => require(['../components/CTDiagnosis/showResults.vue'], resolve)
const ctFull = resolve => require(['../components/CTDiagnosis/showFull.vue'], resolve)

export default new Router({
  routes: [
    {
      path: '/doctor',
      component: home,
      name: 'home',
      iconCls: 'el-icon-message',//图标样式class
      children: [
        {path: '/admin/index',component: AdminIndex, name: 'adminIndex'},
        {path: '/doctor/index', component: DocIndex, name: 'docIndex'},
        {path: '/doctor/addPatient', component: addPatient, name: 'addPatient'},
        {
          path: '/doctor/diagIndex',
          component: diagPage,
          name: 'diagIndex',
          meta: {keepAlive: true},
        },
        {path: '/doctor/docInfo', component: docInfo, name: 'docInfo'},
        {path: '/doctor/CTDetail', component: ctDetail, name: 'ctDetail'},
        {path: '/doctor/selectPage', component: selectPage, name: 'selectPage'},
        {path: '/doctor/ctResult', component: ctResult, name: 'ctResult'},
        {path: '/doctor/ctFull', component: ctFull, name: 'ctFull'},
      ]
    },

    {
      path: '/login',
      name: 'userLogin',
      component: Login
    },
    {
      path: '/register',
      name: 'userRegister',
      component: Register
    },

  ]
})
