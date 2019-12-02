<template>
  <el-form :model="form" :rules="rules" ref="form" label-position="left" label-width="0px" class="card-box">
    <h3 class="title">用户登录</h3>
    <el-form-item prop="username">
      <el-input type="text" v-model="form.username" auto-complete="off" placeholder="用户名"></el-input>
    </el-form-item>
    <el-form-item prop="password">
      <el-input type="password" v-model="form.password" auto-complete="off" placeholder="密码"></el-input>
    </el-form-item>
    <el-form-item>
      <el-button type="primary" style="width:100%;" native-type="submit" @click.native.prevent="onSubmit">
        登录
      </el-button>
    </el-form-item>
    <el-form-item>
      <el-button type="text" @click="register" style="float: right">没有账户？去注册</el-button>
    </el-form-item>
  </el-form>
</template>

<script>
  import AllService from '../../services/allservices.js'

  var allService = new AllService()
  export default {
    data () {
      return {
        form: {
          username: '',
          password: ''
        },
        rules: {
          username: [
            {required: true, message: '请输入账号', trigger: 'blur'},
            { min: 2, max: 13, message: '长度在 2 到 13 个字符', trigger: 'blur' }
          ],
          password: [
            {required: true, message: '请输入密码', trigger: 'blur'},
            { min: 1, max: 13, message: '长度在 6 到 13 个字符', trigger: 'blur' }
          ]
        },
      }
    },
    methods: {
      onSubmit () {
        this.$refs.form.validate((valid) => {
          if (valid) {
            this.login()
          }
        })
      },
      login () {
        var params={
          username:this.form.username,
          password:this.form.password
        }
        allService.signIn(params, (isOk, data) => {
          if (isOk) {
            if(data.error_num === 1){
              console.log(data.msg);
              this.$message.error(data.msg);
            }else if(data.data.is_admin===true){
              sessionStorage.setItem('user', JSON.stringify(data.data));
              this.$message.success("登录成功！");
              this.$router.push({name: 'adminIndex'})
            } else {
              sessionStorage.setItem('user', JSON.stringify(data.data));
              this.$message.success("登录成功！");
              this.$router.push({name: 'docIndex'})
            }
          } else {
            this.$alert("登录失败！")
          }
        })
      },
      register(){
        this.$router.push({name: 'userRegister'});
      }


    }
  }
</script>

<style scoped>
  .card-box {
    padding: 35px 35px 15px 35px;
    -webkit-border-radius: 5px;
    border-radius: 5px;
    -moz-border-radius: 5px;
    background-clip: padding-box;
    margin-bottom: 20px;
    background-color: #F9FAFC;
    margin: 120px auto;
    width: 350px;
    border: 2px solid #8492A6;
  }

  .title {
    margin: 0px auto 40px auto;
    text-align: center;
    color: #505458;
  }
</style>
