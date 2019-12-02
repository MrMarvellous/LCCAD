<template>
  <el-form :model="register" status-icon ref="register" label-width="100px" class="demo-ruleForm">
    <h3 class="title">用户注册</h3>
    <el-form-item label="用户名" prop="username">
      <el-input type="text" v-model="register.username" auto-complete="off"></el-input>
    </el-form-item>
    <el-form-item label="电子邮箱" prop="email">
      <el-input type="text" v-model="register.email" auto-complete="off"></el-input>
    </el-form-item>
    <el-form-item label="密码" prop="password1">
      <el-input type="password" v-model="register.password1" auto-complete="off"></el-input>
    </el-form-item>
    <el-form-item label="确认密码" prop="password2">
      <el-input type="password" v-model="register.password2" auto-complete="off"></el-input>
    </el-form-item>
    <el-form-item>
      <el-button type="primary" @click="submitForm('register')">提交</el-button>
      <el-button @click="resetForm('register')">重置</el-button>
    </el-form-item>
  </el-form>
</template>

<script>
  import AllService from '../../services/allservices.js'
  var allService = new AllService()

  export default {
    data() {
      return {
        register: {
          username:'',
          email: '',
          password1: '',
          password2: '',
        },

      };
    },

    methods: {
      submitForm(formName) {
        this.regist()
      },
      regist () {
        var params={
          username:this.register.username,
          email:this.register.email,
          password1:this.register.password1,
          password2:this.register.password2
        }
        allService.signUp(params, (isOk, data) => {
          if (isOk) {
            console.log(data);
            if(data.error_num===1){
              this.$message.error(data.msg);
            }
            else {
              this.$message.success("注册成功！")
              this.$router.push({name: 'userLogin'})
            }

          } else {
            this.$alert("注册失败！")
          }
        })
      },
      resetForm(formName) {
        this.$refs[formName].resetFields();
      }
    }
  }
</script>
<style scoped>
  .demo-ruleForm {
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
