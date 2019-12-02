<template>
  <keep-alive>
    <section>
      <div class="main-container">
        <patientInfo></patientInfo>
      </div>

      <div class="block"></div>

      <div class="main-container">
        <el-form
          ref="symptomForm"
          :model="symptomForm"
          label-width="100px"
          style="width: 80%;margin-left: auto;margin-right: auto"
        >
          <el-form-item label="症状" prop="symptom">
            <el-input v-model="symptomForm.symptom" type="textarea" :rows="2"></el-input>
          </el-form-item>
          <el-form-item label="CT">
            <el-button
              type="text"
              v-if="symptomForm.hasCT"
              @click="showAllCT"
            >{{symptomForm.ct_name}}</el-button>
            <el-button
              v-if="symptomForm.hasCT"
              type="danger"
              icon="el-icon-delete"
              circle
              @click="deleteCT"
            ></el-button>

            <el-upload
              action="http://127.0.0.1:8000/detect/addPatientFile/"
              :limit="1"
              multiple
              :on-exceed="handleExceed"
              :on-success="handleUploadSuccess"
              :before-upload="beforeFileUpload"
              :show-file-list="false"
              v-else
            >
              <el-button type="text" @click="uploadCT">还没有CT,点击上传</el-button>
            </el-upload>
          </el-form-item>
          <!--<el-form-item label="AI检测结果" v-if="symptomForm.hasCT">-->
          <!--<el-button type="primary" @click="showDetectResult">查看</el-button>-->
          <!--</el-form-item>-->
        </el-form>
      </div>

      <div class="block"></div>

      <div class="main-container">
        <el-form
          ref="summaryForm"
          :model="summaryForm"
          label-width="100px"
          style="width: 80%;margin-left: auto;margin-right: auto"
        >
          <el-form-item label="诊断结果" prop="diagnosisResult">
            <el-input v-model="summaryForm.diagnosisResult" type="textarea" :rows="2"></el-input>
          </el-form-item>

          <el-form-item label="是否有肺结节" prop="hasNodule">
            <el-radio-group v-model="summaryForm.hasNodule">
              <el-radio :label="1">有</el-radio>
              <el-radio :label="0">无</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="添加图片" prop="img_list" v-if="summaryForm.hasNodule===1">
            <el-button
              type="primary"
              @click="gotoSelectPage"
              v-if="summaryForm.img_list.length===0"
            >选择图片</el-button>
            <div v-if="summaryForm.img_list.length!==0">
              <el-row>
                <el-col :span="20">
                  <div
                    style="width:100%;
                       height: 14vw;
                       overflow-x: auto;
                       overflow-y: hidden;
                       white-space: nowrap;"
                  >
                    <img
                      v-for="imgCode in checkList_img"
                      :src="formatImgSrc(imgCode)"
                      style="padding: 0px 5px;width: 15vw; height: 14vw"
                    >
                  </div>
                </el-col>
                <el-col :span="4">
                  <div style="line-height: 14vw;">
                    <el-button
                      style="vertical-align: center"
                      type="danger"
                      icon="el-icon-delete"
                      circle
                      @click="deleteImgList"
                    ></el-button>
                  </div>
                </el-col>
              </el-row>

              <!--<div v-for="imgCode in checkList_img">-->
              <!--<img :src="formatImgSrc(imgCode)"-->
              <!--style="width: 15vw; height: 14vw"/>-->
              <!--</div>-->
              <!--<el-button-->
              <!--type="danger"-->
              <!--icon="el-icon-delete"-->
              <!--circle-->
              <!--@click="deleteImgList"-->
              <!--&gt;</el-button>-->
            </div>
          </el-form-item>

          <el-form-item style="text-align: center">
            <el-button type="primary" @click="generateReport">生成报告</el-button>
          </el-form-item>
        </el-form>
      </div>
    </section>
  </keep-alive>
</template>


<script>
import AllService from "../../services/allservices.js";
import patientInfo from "./components/patientInfo";
import util from "../../common/util";

var allService = new AllService();
export default {
  components: {
    patientInfo
  },
  data() {
    return {
      doctorId: "",
      doctor: "",
      patient: {},
      diagId: "",

      symptomForm: {
        symptom: "",
        hasCT: false,
        ct_id: "",
        ct_name: "",
        ct_path: "",
        upload_time: ""
      },
      fileList: [],

      summaryForm: {
        diagnosisResult: "",
        hasNodule: 0,
        img_list: []
      },
      checkList_img: [],
      lastRoute: "" // store last route path
    };
  },
  methods: {
    getCTInfo() {
      let params = {
        patient_id: this.patient.id,
        ct_name: this.symptomForm.ct_name
      };
      allService.getCTByPatient(params, (isOk, data) => {
        if (isOk) {
          if (data.total === 1) {
            this.symptomForm.hasCT = true;
            this.symptomForm.ct_id = data.data[0].id;
            this.symptomForm.ct_name = data.data[0].ct_name;
            this.symptomForm.ct_path = data.data[0].ct_path;
            this.symptomForm.upload_time = data.data[0].upload_time;
          }
          if (data.total === 0) {
            this.symptomForm.hasCT = false;
            this.symptomForm.ct_id = "";
            this.symptomForm.ct_name = "";
            this.symptomForm.ct_path = "";
            this.symptomForm.upload_time = "";
          }
        }
      });
    },
    formatImgSrc(base64code) {
      return "data:image/jpg;base64," + base64code;
    },
    printList(list) {
      console.log("in print list ");
      console.log(list.length);
      console.log(list);
      let str = "";
      for (let ele in list) {
        str += list[ele];
        if (list.indexOf(list[ele]) !== list.length - 1) {
          str += ", ";
        }
      }
      return str;
    },
    deleteImgList() {
      this.summaryForm.img_list = [];
      this.summaryForm.hasNodule = 0;
      console.log("has click delete button ");
      console.log(this.summaryForm.img_list);
      console.log(this.summaryForm.hasNodule);
    },
    showAllCT() {
      var get_ct_param = {
        name: this.symptomForm.ct_name
      };
      sessionStorage.setItem("allPicParam", JSON.stringify(get_ct_param));
      this.$router.push({ name: "ctDetail" });
    },
    uploadCT() {
      console.log("click upload ct button");
    },
    deleteCT() {
      this.$confirm("确定要删除CT文件吗？", "确定删除", {
        distinguishCancelAndClose: true,
        confirmButtonText: "删除",
        cancelButtonText: "取消删除"
      }).then(() => {
        var ct_id = this.symptomForm.ct_id;
        var temp = this.symptomForm;
        temp.hasCT = false;
        temp.ct_id = "";
        temp.ct_name = "";
        temp.ct_path = "";
        temp.upload_time = "";
        this.symptomForm = temp;
        var params = {
          ct_id: ct_id
        };
        allService.deleteCTInfo(params, (isOk, data) => {
          if (isOk) {
            this.$message.success("删除成功");
          }
        });
      });
    },
    showDetectResult() {},
    handleExceed(files, fileList) {
      this.$message.warning(
        `当前限制选择 1 个文件，本次选择了 ${
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
            this.symptomForm.hasCT = true;
            this.symptomForm.ct_id = data.data.id;
            this.symptomForm.ct_name = data.data.ct_name;
            this.symptomForm.ct_path = data.data.ct_path;
            this.symptomForm.upload_time = data.data.upload_time;
          } else {
            this.$message.error(data.msg);
          }
        } else {
          this.$message.error("网络错误");
        }
      });
    },
    beforeFileUpload(file) {
      const isZip = file.type === "application/x-zip-compressed";
      console.log(file.type);
      if (!isZip) {
        this.$message.error("上传文件只能是zip格式!");
      }
      return isZip;
    },
    formatNow() {
      var now = new Date();
      var dd = now.getDate();
      var mm = now.getMonth() + 1; //一月是0，一定要注意
      var yyyy = now.getFullYear();
      var hour = now.getHours();
      var minutes = now.getMinutes();
      var seconds = now.getSeconds();
      if (dd < 10) {
        dd = "0" + dd;
      }
      if (mm < 10) {
        mm = "0" + mm;
      }
      now =
        mm + "/" + dd + "/" + yyyy + " " + hour + ":" + minutes + ":" + seconds;
      return now.toString();
    },
    formatDate(date) {
      date = new Date(date);
      return util.formatDate.format(date, "yyyy-MM-dd");
    },
    getAge(strBirthday) {
      var returnAge;
      // 根据生日计算年龄（"1995-09-25"）
      //以下五行是为了获取出生年月日，如果是从身份证上获取需要稍微改变一下
      var strBirthdayArr = strBirthday.split("-");
      var birthYear = strBirthdayArr[0];
      var birthMonth = strBirthdayArr[1];
      var birthDay = strBirthdayArr[2];

      var dnow = new Date();
      var nowYear = dnow.getFullYear();
      var nowMonth = dnow.getMonth() + 1;
      var nowDay = dnow.getDate();

      if (nowYear === birthYear) {
        returnAge = 0; //同年 则为0岁
      } else {
        var ageDiff = nowYear - birthYear; //年之差
        if (ageDiff > 0) {
          if (nowMonth === birthMonth) {
            var dayDiff = nowDay - birthDay; //日之差
            if (dayDiff < 0) {
              returnAge = ageDiff - 1;
            } else {
              returnAge = ageDiff;
            }
          } else {
            var monthDiff = nowMonth - birthMonth; //月之差
            if (monthDiff < 0) {
              returnAge = ageDiff - 1;
            } else {
              returnAge = ageDiff;
            }
          }
        } else {
          returnAge = -1; //返回-1 表示出生日期输入错误 晚于今天
        }
      }
      console.log(returnAge + "");
      return returnAge + ""; //返回周岁年龄
    },
    generateReport() {
      if (this.symptomForm.hasCT === false) {
        this.$message.error("请先上传CT！");
        return;
      }
      console.log("patient");
      console.log(this.patient);
      console.log("user");
      console.log(this.doctor);
      console.log(this.diagId);
      if (this.diagId === "" || this.diagId === undefined) {
        var diagParam = {
          symptom: this.symptomForm.symptom,
          diag_content: this.summaryForm.diagnosisResult,
          doc_id: this.doctor.id,
          patient_id: this.patient.id,
          ct_name: this.symptomForm.ct_name,
          ai_result: this.symptomForm.ct_name,
          diag_time: new Date(),
          diag_remark: this.summaryForm.img_list
        };
        allService.addDiagInfo(diagParam, (isOk, data) => {
          if (isOk) {
            console.log("add diagnosis success");
          }
        });
      } else {
        var diagParam = {
          diag_id: this.diagId,
          symptom: this.symptomForm.symptom,
          diag_content: this.summaryForm.diagnosisResult,
          doc_id: this.doctor.id,
          patient_id: this.patient.id,
          ct_name: this.symptomForm.ct_name,
          ai_result: this.symptomForm.ct_name,
          diag_time: new Date(),
          diag_remark: this.summaryForm.img_list
        };
        allService.updateDiagInfo(diagParam, (isOk, data) => {
          if (isOk) {
            console.log("upload diagnosis success");
          }
        });
      }

      var params = {
        patient_name: this.patient.patient_name,
        patient_sex: this.patient.patient_sex,
        patient_age: this.getAge(this.patient.patient_birth),
        diagnosis_time: this.formatDate(this.patient.patient_add_time),
        patient_tel: this.patient.patient_tel,
        patient_pasthistory: this.patient.patient_past_history,
        doctor_name: this.doctor.doc_name,
        symptom: this.symptomForm.symptom + " ",
        diagnosis_content: this.summaryForm.diagnosisResult + " ",
        export_time: this.formatNow(),
        img_list: this.summaryForm.img_list,
        ct_name: this.symptomForm.ct_name
      };

      allService.generateReport(params, (isOk, data) => {
        if (isOk) {
          this.$message.success("生成报告成功！");
        } else {
          this.$message.error("生成报告失败！");
        }
      });
    },
    gotoSelectPage() {
      if (this.symptomForm.hasCT === true) {
        var get_ct_param = {
          name: this.symptomForm.ct_name,
          ct_path: this.symptomForm.ct_path
        };
        sessionStorage.setItem("allPicParam", JSON.stringify(get_ct_param));
        this.$router.push({ name: "selectPage" });
      } else {
        this.$message.error("请先上传CT！");
      }
    }
  },
  mounted() {
    var user = sessionStorage.getItem("user");
    if (user) {
      user = JSON.parse(user);
      this.doctor = user;
    }
    var patient = sessionStorage.getItem("patient");
    if (patient) {
      patient = JSON.parse(patient);
      this.patient = patient;
    }
    this.$emit("showButton");

    //for modify
    var temp_vars = JSON.parse(sessionStorage.getItem("vars_from_modify"));
    this.symptomForm = {
      symptom: temp_vars.symptomForm.symptom,
      hasCT: temp_vars.symptomForm.hasCT,
      ct_id: "",
      ct_name: temp_vars.symptomForm.ct_name,
      ct_path: "",
      upload_time: ""
    };

    this.summaryForm = {
      diagnosisResult: temp_vars.summaryForm.diagnosisResult,
      hasNodule: temp_vars.summaryForm.hasNodule,
      img_list: temp_vars.summaryForm.img_list
    };

    this.getCTInfo();
  },
  activated() {
    this.lastRoute = sessionStorage.getItem("lastRoute");
    console.log(
      "in active this.lastRoute is ",
      sessionStorage.getItem("lastRoute")
    );
    if (this.lastRoute === "/doctor/index") {
      var user = sessionStorage.getItem("user");
      if (user) {
        user = JSON.parse(user);
        this.doctor = user;
      }
      var patient = sessionStorage.getItem("patient");
      console.log('last patient debug')
      console.log(JSON.parse(patient))
      if (patient) {
        patient = JSON.parse(patient);
        this.patient = patient;
      }
      //for modify
      var temp_vars = JSON.parse(sessionStorage.getItem("vars_from_modify"));
      // console.log('temp_vars', temp_vars)
      this.symptomForm = {
        symptom: temp_vars.symptomForm.symptom,
        hasCT: temp_vars.symptomForm.hasCT,
        ct_id: "",
        ct_name: temp_vars.symptomForm.ct_name,
        ct_path: "",
        upload_time: ""
      };
      this.summaryForm.diagnosisResult = temp_vars.summaryForm.diagnosisResult;

      this.diagId = temp_vars.diagId;
      this.getCTInfo();
      sessionStorage.removeItem("vars_from_modify");
    }

    this.$emit("showButton");
    console.log("<<---------------");
    console.log("imglist");

    console.log(JSON.parse(sessionStorage.getItem("img_list")));
    console.log("--------------->>");
    // if (sessionStorage.getItem('vars_from_modify') === null) {
    //   this.summaryForm.img_list = sessionStorage.getItem('img_list') === null ? [] : JSON.parse(sessionStorage.getItem('img_list'))
    //
    // }
    // if (sessionStorage.getItem('vars_from_modify') !== null) {
    //   sessionStorage.removeItem('vars_from_modify')
    // }
    this.summaryForm.img_list = JSON.parse(sessionStorage.getItem("img_list"));
    console.log(typeof this.summaryForm.img_list);
    if (typeof this.summaryForm.img_list === "string") {
      console.log("has step in this if");
      let img_arr = this.summaryForm.img_list
        .replace("[", "")
        .replace("]", "")
        .split(", ");
      if (img_arr[0] === "") {
        this.summaryForm.img_list = [];
      } else {
        this.summaryForm.img_list = img_arr;
      }
      if (this.summaryForm.img_list.length === 0) {
        this.summaryForm.hasNodule = 0;
      } else {
        this.summaryForm.hasNodule = 1;
      }
    }
    if (this.summaryForm.img_list.length !== 0) {
      let params = {
        ct_name: this.symptomForm.ct_name,
        img_list: this.summaryForm.img_list
      };
      console.log("before getImageIndexList");
      console.log(typeof this.summaryForm.img_list === "string");
      console.log(params);
      allService.getImageByIndexList(params, (isOk, data) => {
        if (isOk) {
          this.checkList_img = data.data;
          if (this.checkList_img.length === 0) {
            this.checkList_img = [];
          }
        }
      });
    }
  }
  // beforeRouteEnter(to, from, next) {
  //   next(vm => {
  //     console.log('last route', from.path)
  //     vm.lastRoute = from.path
  //   })
  // },
  // beforeRouteLeave(to, from, next) {
  //   console.log('in beforeRouteUpdate last route is', from.path)
  //   this.lastRoute = to.path
  //   next()
  // }
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

  padding-left: 20%;
  padding-right: 20%;
}

.main-container {
  margin-left: auto;
  margin-right: auto;
  margin-top: 10px;
  margin-bottom: 10px;
  border-radius: 10px;
  width: 1000px;
  background-color: #ffffff;
  padding-top: 5px;
  padding-bottom: 5px;
  border: 2px solid #f2f2f2;
}

.block {
  background-color: #f2f2f2;
  min-height: 50px;
  margin-top: 10px;

  margin-left: auto;
  margin-right: auto;
  width: 1000px;
  border-radius: 10px;
}

.mysidebar {
  transition: width 0.28s;
  width: 230px !important;
  height: 100%;
  position: fixed;
  font-size: 0px;
  top: 60px;
  bottom: 0;
  left: 0;
  z-index: 1001;
  overflow: hidden;
}

.steps {
  background-color: #c0ccda;
  position: fixed;
  top: 200px;
  height: 250px;
  left: 170px;
}
</style>
