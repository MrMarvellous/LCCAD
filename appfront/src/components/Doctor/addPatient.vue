<template>
  <section style="margin: auto;padding-left: 20%;padding-right: 20%">
    <el-form ref="form" :model="form" :rules='rules' label-width="100px" class="form_class">
      <el-form-item label="病人姓名" prop="name">
        <el-input v-model="form.name"></el-input>
      </el-form-item>
      <el-form-item label="病人性别" prop="sex">
        <el-radio-group v-model="form.sex">
          <el-radio :label="1">男</el-radio>
          <el-radio :label="2">女</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="病人电话" prop="tel">
        <el-input v-model="form.tel"></el-input>
      </el-form-item>
      <el-form-item label="病人生日" prop="birth">
        <el-date-picker
          v-model="form.birth"
          type="date"
          placeholder="选择日期">
        </el-date-picker>
      </el-form-item>
      <el-form-item label="病人住址" prop="address">
        <el-input v-model="form.address"></el-input>
      </el-form-item>
      <el-form-item label="病人病史" prop="pastHistory">
        <el-input v-model="form.pastHistory" type="textarea" :rows="2"></el-input>
      </el-form-item>

      <el-form-item label="病人备注" prop="remark">
        <el-input v-model="form.remark" type="textarea" :rows="2"></el-input>
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="onSubmit">立即创建</el-button>
        <el-button @click="backToIndex">返回首页</el-button>
      </el-form-item>
    </el-form>

  </section>

</template>

<script>
  import AllService from '../../services/allservices.js'
  import util from '../../common/util'

  var allService = new AllService()
  export default {
    data() {
      let telValid = (rule, value, callback) => {
        let regExp = /^1[3456789]\d{9}$/;
        let nullExp = /^$/;
        if (regExp.test(value) === false && nullExp.test(value) === false) {
          callback(new Error('号码格式错误'))
        } else {
          callback();
        }
      };
      let ageValid = (rule, value, callback) => {
        let ageExp = /^(?:[1-9][0-9]?|1[01][0-9]|120)$/;//年龄是1-120之间有效
        if (ageExp.test(value) === false) {
          callback(new Error('年龄输入错误'))
        } else {
          callback();
        }
      };
      return {
        form: {
          name: '',
          sex: -1,
          birth: '',
          doctorId: '',
          address: '',
          pastHistory: '',
          tel: '',
          remark: ''
        },
        fileList: [],
        rules: {
          name: [
            {required: true, message: '请输入姓名', trigger: 'blur'}
          ],
          sex: [
            {required: true, message: '请选择性别', trigger: 'change'}
          ],
          birth: [
            {required: true, message: '请选择出生日期', trigger: 'blur'}
          ],
          address: [
            {required: true, message: '请输入患者住址', trigger: 'blur'}
          ],
          pastHistory: [
            {min: 0, max: 256, message: '长度最多是256个字符', trigger: 'change'}
          ],
          tel: [
            {validator: telValid, trigger: 'blur'}
          ],
          remark: [
            {min: 0, max: 256, message: '长度最多是256个字符', trigger: 'change'}
          ]
        }
      }
    },
    methods: {
      onSubmit() {
        this.$refs.form.validate((valid => {
          if (valid) {
            this.addPt()
          } else {
            console.log('front valid error')
            return false
          }
        }))
      },
      getNowTime() {
        var date = new Date()
        console.log(date)
        date.setHours(date.getHours() + 8)
        console.log(date)
        return util.formatDate.format(date, 'yyyy-MM-dd hh:mm:ss')
      },
      addPt() {
        var patient = {
          patient_name: this.form.name,
          patient_sex: this.form.sex,
          patient_birth: util.formatDate.format(this.form.birth, 'yyyy-MM-dd'),
          patient_doc: this.form.doctorId,
          patient_address: this.form.address,
          patient_past_history: this.form.pastHistory,
          patient_tel: this.form.tel,
          patient_remark: this.form.remark,
          patient_add_time: this.getNowTime(),
        }
        allService.addPatient(patient, (isOk, data) => {
          if (isOk) {
            if (data.error_num === 1) {
              console.log(data.msg);
              this.$message.error(data.msg);
            } else {

              this.$message.success("创建成功！");
              this.$router.push({name: 'docIndex'})
            }
          } else {
            this.$alert("创建失败！")
          }
        })
      },
      handleRemove(file, fileList) {
        console.log(file, fileList);
      },
      beforeRemove(file, fileList) {
        return this.$confirm(`确定移除 ${ file.name }？`);
      },
      handleExceed(files, fileList) {
        this.$message.warning(`当前限制选择 3 个文件，本次选择了 ${files.length} 个文件，共选择了 ${files.length + fileList.length} 个文件`);
      },
      beforeFileUpload(file) {
        const isZip = file.type === 'application/x-zip-compressed'
        console.log(file.type)
        if (!isZip) {
          this.$message.error('上传文件只能是zip格式!');
        }
        return isZip
      },
      backToIndex() {
        this.$router.push({name: 'docIndex'})
      }
    },
    mounted() {
      var user = sessionStorage.getItem('user');
      if (user) {
        user = JSON.parse(user);
        this.form.doctorId = user.id || '';
      }
      console.log("this.form.doctorId")
      console.log(this.form.doctorId)
    }
  }

</script>

<style scoped>
  .form_class {
    margin-top: 20px;
    margin-left: auto;
    margin-right: auto;
    margin-bottom: 50px;
    width: 60%;
    min-width: 600px;
  }

</style>
