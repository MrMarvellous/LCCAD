<template>
  <section style="margin: auto;padding-left: 20%;padding-right: 20%">
    <el-form ref="form" :model="form" :rules="rules" label-width="100px" class="form_class">
      <el-form-item label="姓名" prop="name">
        <span class="span_class" v-if="editOrShow===1">{{ form.name }}</span>
        <el-input v-model="form.name" v-if="editOrShow===0"></el-input>
      </el-form-item>
      <el-form-item label="性别" prop="sex">
        <el-radio-group v-model="form.sex" v-if="editOrShow===0">
          <el-radio :label="1">男</el-radio>
          <el-radio :label="2">女</el-radio>
        </el-radio-group>
        <span class="span_class" v-if="editOrShow===1">{{ formatSex(form.sex) }}</span>
      </el-form-item>
      <el-form-item label="电话" prop="tel">
        <el-input v-model="form.tel" v-if="editOrShow===0"></el-input>
        <span class="span_class" v-if="editOrShow===1">{{ form.tel }}</span>
      </el-form-item>
      <el-form-item label="生日" prop="birth">
        <el-date-picker v-model="form.birth" type="date" placeholder="选择日期" v-if="editOrShow===0"></el-date-picker>
        <span class="span_class" v-if="editOrShow===1">{{ formatDate(form.birth) }}</span>
      </el-form-item>
      <el-form-item label="医院" prop="hospital">
        <el-input v-model="form.hospital" v-if="editOrShow===0"></el-input>
        <span class="span_class" v-if="editOrShow===1">{{ form.hospital }}</span>
      </el-form-item>
      <el-form-item label="科室" prop="depart">
        <el-input v-model="form.depart" v-if="editOrShow===0"></el-input>
        <span class="span_class" v-if="editOrShow===1">{{ form.depart }}</span>
      </el-form-item>
      <el-form-item label="简介" prop="description">
        <el-input v-model="form.description" v-if="editOrShow===0"></el-input>
        <span class="span_class" v-if="editOrShow===1">{{ form.description }}</span>
      </el-form-item>

      <el-form-item>
        <el-button @click="editDoctorInfo" v-if="editOrShow===1">编辑信息</el-button>
        <el-button type="primary" @click="onSubmit" v-if="editOrShow===0">保存</el-button>
      </el-form-item>
    </el-form>
  </section>
</template>

<script>
import AllService from "../../services/allservices.js";
import util from "../../common/util";

var allService = new AllService();
export default {
  data() {
    let telValid = (rule, value, callback) => {
      let regExp = /^1[3456789]\d{9}$/;
      let nullExp = /^$/;
      if (regExp.test(value) === false && nullExp.test(value) === false) {
        callback(new Error("号码格式错误"));
      } else {
        callback();
      }
    };

    return {
      form: {
        name: "",
        sex: -1,
        birth: "",
        tel: "",
        hospital: "",
        depart: "",
        description: ""
      },
      doctorId: "",
      editOrShow: 1,
      fileList: [],
      rules: {
        name: [{ required: true, message: "请输入姓名", trigger: "blur" }],
        sex: [{ required: true, message: "请选择性别", trigger: "change" }],
        birth: [{ required: true, message: "请选择出生日期", trigger: "blur" }],
        tel: [
          { required: true, message: "请输入手机号码", trigger: "blur" },
          { validator: telValid, trigger: "blur" }
        ],
        hospital: [{ required: true, message: "请输入医院", trigger: "blur" }],
        depart: [{ required: true, message: "请输入科室", trigger: "blur" }]
      }
    };
  },
  methods: {
    formatDate(date){
      date = new Date(date)
      return util.formatDate.format(date, 'yyyy-MM-dd')
    },
    onSubmit() {
      this.$refs.form.validate(valid => {
        if (valid) {
          this.updateInfo();
        } else {
          console.log("front valid error");
          return false;
        }
      });
    },
    updateInfo() {
      var doctor = {
        id: this.doctorId,
        docName: this.form.name,
        docSex: this.form.sex,
        docBirth: util.formatDate.format(this.form.birth, "yyyy-MM-dd"),
        docTel: this.form.tel,
        docHospital: this.form.hospital,
        docDepart: this.form.depart,
        docDescription: this.form.description
      };
      allService.updateDoctorInfo(doctor, (isOk, data) => {
        if (isOk) {
          if (data.error_num === 1) {
            console.log(data.msg);
            this.$message.error(data.msg);
          } else {
            this.$message.success("修改成功！");
            this.editOrShow = 1;
          }
        } else {
          this.$alert("创建失败！");
        }
      });
    },
    getDoctorInfo() {
      let params = {
        doctorId: this.doctorId
      };
      allService.getDoctorInfo(params, (isOk, data) => {
        if (isOk) {
          if (data.error_num === 1) {
            console.log(data.msg);
            this.$message.error(data.msg);
          } else {
            let temp = this.form;
            temp.name = data.data.doc_name;
            temp.sex = data.data.doc_sex;
            temp.birth = util.formatDate.parse(data.data.doc_birth, 'yyyy-MM-dd');
            temp.tel = data.data.doc_tel;
            temp.hospital = data.data.doc_hospital;
            temp.depart = data.data.doc_depart;
            temp.description = data.data.doc_description;
            this.form = temp;
          }
          console.log('this.form')
          console.log(this.form)
        } else {
          this.$alert("网络错误！");
        }
      });
    },
    editDoctorInfo() {
      this.editOrShow = 0;
    },
    formatSex(value) {
      return value === 1 ? "男" : value === 2 ? "女" : "未知";
    },
  },
  mounted() {
    var user = sessionStorage.getItem("user");
    if (user) {
      user = JSON.parse(user);
      this.doctorId = user.id || "";
    }
    this.getDoctorInfo();
    this.$emit('showButton');
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

.span_class {
  font-size: 15px;
  margin-left: 0px;
}
</style>
