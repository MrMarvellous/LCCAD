<!-- 管理CT页面： 包括上传CT ， 管理CT， 显示CT-->
<template>
  <section style="margin: auto;padding-left: 20%;padding-right: 20%">
    <el-form ref="form" :model="form" label-width="100px" class="form_class">
      <el-form-item label="病人症状" prop="symptom">
        <el-input v-model="form.symptom" type="textarea" :rows="2"></el-input>
      </el-form-item>
      <el-form-item label="医生诊断" prop="diagnosis_content">
        <el-input v-model="form.diagnosis_content" type="textarea" :rows="2"></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type='primary' @click="generateReport">生成报告</el-button>
      </el-form-item>
    </el-form>

  </section>
</template>

<script>
  import AllService from "../../../services/allservices.js";

  var allService = new AllService();
  export default {
    data() {
      return {
        form: {
          symptom: '',
          diagnosis_content: '',
        },
        user:{},
        patient:{},

      };
    },
    methods: {
      generateReport() {
        console.log('patient')
        console.log(this.patient)
        console.log('user')
        console.log(this.user)
        var params = {
          patient_name: this.patient.patient_name,
          doctor_name: this.user.doc_name,
          symptom: this.form.symptom+" ",
          diagnosis_content: this.form.diagnosis_content+" "
        }

        allService.generateReport(params, (isOk, data) => {
          if (isOk) {
            this.$message.success('生成报告成功！')
          } else {
            this.$message.error('生成报告失败！')
          }
        })

      },
    },
    mounted() {
      var user = sessionStorage.getItem("user");
      if (user) {
        user = JSON.parse(user);
        this.user = user
      }
      var patient = sessionStorage.getItem("patient");
      if (patient) {
        patient = JSON.parse(patient);
        this.patient = patient;
      }

    }
  };
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
