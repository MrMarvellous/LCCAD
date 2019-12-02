<template>
  <section style="margin: auto;padding-left: 0;padding-right: 0">
    <el-form ref="form" :model="form" label-width="100px" class="form_class">
      <el-form-item label="病人姓名" prop="name">
        <el-input v-model="form.name" v-if="editOrShow===0"></el-input>
        <span class="span_class" v-if="editOrShow===1">{{ form.name }}</span>
      </el-form-item>
      <el-form-item label="病人性别" prop="sex">
        <el-radio-group v-model="form.sex" v-if="editOrShow===0">
          <el-radio :label="1">男</el-radio>
          <el-radio :label="2">女</el-radio>
        </el-radio-group>
        <span class="span_class" v-if="editOrShow===1">{{ formatSex(form.sex) }}</span>
      </el-form-item>
      <el-form-item label="病人电话" prop="tel">
        <el-input v-model="form.tel" v-if="editOrShow===0"></el-input>
        <span class="span_class" v-if="editOrShow===1">{{ form.tel }}</span>
      </el-form-item>
      <el-form-item label="病人家庭住址" prop="address">
        <el-input v-model="form.address" type="textarea" :rows="2" v-if="editOrShow===0"></el-input>
        <span class="span_class" v-if="editOrShow===1">{{ form.address }}</span>
      </el-form-item>
      <el-form-item label="出生日期" prop="birth">
        <el-date-picker v-model="form.birth" type="date" placeholder="选择日期" v-if="editOrShow===0"/>
        <span class="span_class" v-if="editOrShow===1">{{ formatDate(form.birth) }}</span>
      </el-form-item>
      <el-form-item label="病人病史" prop="pastHistory">
        <el-input v-model="form.pastHistory" type="textarea" :rows="2" v-if="editOrShow===0"></el-input>
        <span class="span_class" v-if="editOrShow===1">{{ form.pastHistory }}</span>
      </el-form-item>
      <el-form-item label="病人备注" prop="remark">
        <el-input v-model="form.remark" type="textarea" :rows="2" v-if="editOrShow===0"></el-input>
        <span class="span_class" v-if="editOrShow===1">{{ form.remark }}</span>
      </el-form-item>
      <!--<el-form-item label="添加CT">-->
      <!--<el-upload-->
      <!--class="upload-demo"-->
      <!--action="http://127.0.0.1:8000/detect/addPatientFile/"-->
      <!--:on-remove="handleRemove"-->
      <!--:before-remove="beforeRemove"-->
      <!--multiple-->
      <!--:limit="2"-->
      <!--:on-exceed="handleExceed"-->
      <!--:on-success="handleUploadSuccess"-->
      <!--:before-upload="beforeFileUpload"-->
      <!--:file-list="fileList">-->
      <!--<el-button size="small" type="primary">点击上传</el-button>-->
      <!--</el-upload>-->
      <!--</el-form-item>-->
      <el-form-item style="text-align: center">
        <el-button @click="editPatientInfo" v-if="editOrShow===1">编辑信息</el-button>
        <el-button @click="savePatientInfo" v-if="editOrShow===0">保存</el-button>
      </el-form-item>
    </el-form>
  </section>
</template>

<script>
  import AllService from "../../../services/allservices.js";
  import util from "../../../common/util";

  var allService = new AllService();
  export default {
    data() {
      return {
        patient: {
          id: "",
          name: "",
          sex: -1,
          tel: "",
          address: "",
          birth: "",
          pastHistory: "",
          remark: ""
        },
        form: {
          name: "",
          sex: -1,
          tel: "",
          address: "",
          birth: "",
          pastHistory: "",
          remark: ""
        },
        fileList: [],
        editOrShow: 1 //edit: 0 ;show: 1
      };
    },
    methods: {
      formatSex: function (value) {
        return value === 1 ? "男" : value === 2 ? "女" : "未知";
      },
      formatDate(date) {
        date = new Date(date);
        return util.formatDate.format(date, "yyyy-MM-dd");
      },
      getPatientInfo() {
        let temp = this.form;
        temp.name = this.patient.patient_name;
        temp.sex = this.patient.patient_sex;
        temp.tel = this.patient.patient_tel;
        temp.address = this.patient.patient_address;
        temp.birth = util.formatDate.parse(
          this.patient.patient_birth,
          "yyyy-MM-dd"
        );
        //temp.birth = this.patient.patient_birth
        temp.pastHistory = this.patient.patient_past_history;
        temp.remark = this.patient.patient_remark;
        this.form = temp;
        console.log(this.form);
      },
      editPatientInfo() {
        this.editOrShow = 0;
      },
      savePatientInfo() {
        this.editOrShow = 1;
        let param = this.form;
        param.id = this.patient.id;
        param.birth = util.formatDate.format(this.form.birth, "yyyy-MM-dd");
        console.log("params");
        console.log(param);
        allService.updatePatientInfo(param, (isOk, data) => {
          if (isOk) {
            if (data.error_num === 0) {
              this.$message.success("修改成功！");
              this.patient = data.data[0];
              this.getPatientInfo();
            } else {
              this.$message.error(data.msg);
            }
          } else {
            this.$message.error("修改失败！");
          }
        });
      },
      handleRemove(file, fileList) {
        console.log(file, fileList);
      },
      beforeRemove(file, fileList) {
        return this.$confirm(`确定移除 ${file.name}？`);
      },
      handleExceed(files, fileList) {
        this.$message.warning(
          `当前限制选择 2 个文件，本次选择了 ${
            files.length
            } 个文件，共选择了 ${files.length + fileList.length} 个文件`
        );
      },
      handleUploadSuccess(res, file) {
        console.log(file);
        var filename = file.name;
        var lastindex = filename.lastIndexOf(".");
        var purename = filename.slice(0, lastindex);
        console.log(purename);
        var params = {
          patient_id: this.patient.id,
          filename: purename
        };

        allService.addCTInfo(params, (isOk, data) => {
          if (isOk) {
            if (data.error_num === 0) {
              this.$message.success("add success");
            } else {
              this.$message.error(data.msg);
            }
          } else {
            this.$message.error("网络错误");
          }
        });

        console.log(res);
        console.log(file);
        if (res.error_num === 0) {
          this.fileList.append(file.name);
          this.$message.success(this.fileList[0] + "upload success");
        } else {
          this.$message.error(res.msg);
        }
      },
      beforeFileUpload(file) {
        const isZip = file.type === "application/x-zip-compressed";
        console.log(file.type);
        if (!isZip) {
          this.$message.error("上传文件只能是zip格式!");
        }
        return isZip;
      },
      backToIndex() {
        this.$router.push({name: "docIndex"});
      }
    },
    mounted() {
      var user = sessionStorage.getItem("user");
      if (user) {
        user = JSON.parse(user);
        this.doctorId = user.id || "";
      }
      var patient = sessionStorage.getItem("patient");
      if (patient) {
        patient = JSON.parse(patient);
        this.patient = patient;
        console.log("this.patient");
        console.log(this.patient);
      }
      this.getPatientInfo();
    },
    activated() {
      var user = sessionStorage.getItem("user");
      if (user) {
        user = JSON.parse(user);
        this.doctorId = user.id || "";
      }
      var patient = sessionStorage.getItem("patient");
      if (patient) {
        patient = JSON.parse(patient);
        this.patient = patient;
        console.log("this.patient");
        console.log(this.patient);
      }
      this.getPatientInfo();
    }
  };
</script>

<style scoped>
  .form_class {
    margin-left: auto;
    margin-right: auto;
    width: 80%;
  }

  .span_class {
    font-size: 15px;
    margin-left: 0px;
  }
</style>
