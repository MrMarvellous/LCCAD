<!-- 管理CT页面： 包括上传CT ， 管理CT， 显示CT-->
<template>
  <section style="padding-left: 0;padding-right: 0%">
    <div class="detectButton">
      <el-button type="primary" @click="showAIResult()">AI检测</el-button>
    </div>

    <div v-if="showAIResultBool">
      <el-dialog title="检测结果" :visible.sync="showAIResultBool" width="70%">
        <el-button class="mybutton__arrow mybutton__arrow-left" @click="minusImgIndex">
          <i class="el-icon-arrow-left"></i>
        </el-button>
        <el-button class="mybutton__arrow mybutton__arrow-right" @click="addImgIndex">
          <i class="el-icon-arrow-right"></i>
        </el-button>
        <el-image
          :src="formatImgSrc(current_img)"
          fit="contain"
          style="width:429px;height: 418px;margin-left: 270px"
        ></el-image>
        <el-row>
          <el-form ref="predictForm" :model="predictForm">
            <el-col :span="6">
              <el-form-item label="可能性：">
                <span>{{allAIpos[page-1]}}</span>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="预测框大小：">
                <span>{{allAIsize[page-1]}}mm</span>
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="原图编号:">
                <span>{{allAIz[page-1]}}</span>
              </el-form-item>
            </el-col>
          </el-form>
        </el-row>
        <el-pagination
          background
          @current-change="handleCurrentChange"
          :current-page="page"
          :page-size="1"
          layout="total, pager"
          :total="allAIImageList_length"
          style="text-align: center"
        ></el-pagination>
      </el-dialog>
    </div>

    <div>
      <el-row :gutter="20">
        <el-col :span="4" v-for="imageCode in allImageList" style="margin-top: 3em">
          <div style="padding: 4px;">
            <div class="demonstration">编号： {{allImageList.indexOf(imageCode)}}</div>
            <img
              v-image-preview
              :src="formatImgSrc(imageCode)"
              style="width: 15vw; height: 14vw;margin-left: auto;margin-right: auto;"
            >
          </div>
        </el-col>
      </el-row>
    </div>
  </section>
</template>

<script>
import AllService from "../../services/allservices.js";
import util from "../../common/util";

var allService = new AllService();
export default {
  data() {
    return {
      //for /display all image
      allPicParam: {},
      allImageList: [],
      number_start: 0,

      showAIResultBool: false,
      allAIImageList: [],
      allAIpos: [],
      allAIz: [],
      allAIx: [],
      allAIy: [],
      allAIsize: [],
      allAIImageList_length: 0,
      page: 1,

      current_img: "",

      predictForm: {
        img_src: "",
        p: 0,
        x: "samplex",
        y: "sampley",
        z: "samplez",
        rawz: 0
      }
    };
  },
  methods: {
    initVars() {
      this.allImageList = [];
      this.number_start = 0;
      this.showAIResultBool = false;
      this.allAIImageList = [];
    },
    clickButton() {
      console.log("has click button test");
    },
    getNumber() {
      this.number_start = this.number_start + 1;
      return this.number_start;
    },

    formatImgSrc(base64code) {
      return "data:image/jpg;base64," + base64code;
    },

    getAllPic() {
      //let allpicPath = ct.ct_path;
      console.log("start request for image");
      var params = this.allPicParam;
      allService.getAllImage(params, (isok, data) => {
        if (isok) {
          this.allImageList = data.data;
        }
      });
    },
    closeAIResult() {
      this.showAIResultBool = false;
    },
    showAIResult() {
      this.showAIResultBool = true;
      let params = this.allPicParam;
      allService.getAIPredict(params, (isok, data) => {
        console.log("in get all predict image");
        if (isok) {
          this.allAIImageList = data.data[0];
          this.allAIpos = data.data[1];
          this.allAIz = data.data[2];
          this.allAIx = data.data[3];
          this.allAIy = data.data[4];
          this.allAIsize = data.data[5];
          this.current_img = this.allAIImageList[0];
          this.allAIImageList_length = data.data[0].length;

          for (var i = 0; i < this.allAIz.length; i++) {
            this.allAIz[i] = Math.floor(this.allAIz[i]);
          }
        }
      });
    },
    handleCurrentChange(val) {
      this.page = val;
      console.log("now is page ", this.page);
      console.log(this.allAIImageList_length);
      this.current_img = this.allAIImageList[this.page - 1];
    },
    addImgIndex() {
      var newpage = this.page + 1;
      if (newpage >= this.allAIImageList_length) {
        newpage = this.allAIImageList_length;
      }
      console.log("newpage", newpage);
      this.handleCurrentChange(newpage);
      this.page = newpage;
    },
    minusImgIndex() {
      var newpage = this.page - 1;
      if (newpage <= 0) {
        newpage = 1;
      }
      console.log("newpage", newpage);
      this.handleCurrentChange(newpage);
      this.page = newpage;
    }
  },
  created() {
    var user = sessionStorage.getItem("user");
    if (user) {
      user = JSON.parse(user);
      this.doctorId = user.id || "";
    }
    var patient = sessionStorage.getItem("patient");
    if (patient) {
      patient = JSON.parse(patient);
      this.patient = patient;
    }
  },
  mounted() {
    this.initVars();
    var allPicParam = sessionStorage.getItem("allPicParam");
    if (allPicParam) {
      let param = JSON.parse(allPicParam);
      this.allPicParam = param;
    }
    this.getAllPic();
    this.$emit("showBackDiaButton");
  }
};
</script>

<style>
.avatar-uploader .el-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.avatar-uploader .el-upload:hover {
  border-color: #409eff;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  line-height: 178px;
  text-align: center;
}

.avatar {
  width: 178px;
  height: 178px;
  display: block;
}

.fix-button {
  /*background-color: #3a8ee6;*/
  position: absolute;
  right: 100px;
  bottom: 70px;
  width: 80px;
  height: 80px;
  size: 80px;
  z-index: 5;
}
</style>

<style scoped>
.icon {
  width: 150px;
  height: 150px;
  vertical-align: -0.15em;
  fill: currentColor;
  overflow: hidden;
}

.form_class {
  margin-top: 20px;
  margin-left: auto;
  margin-right: auto;
  margin-bottom: 50px;
  width: 60%;
  min-width: 600px;
}

.time {
  font-size: 13px;
  color: #999;
}

.bottom {
  margin-top: 13px;
  line-height: 12px;
}

.button {
  padding: 0;
  float: right;
}

.image {
  width: 100%;
  display: block;
}

.clearfix:before,
.clearfix:after {
  display: table;
  content: "";
}

.clearfix:after {
  clear: both;
}

.demonstration {
  text-align: center;
  display: block;
  color: #8492a6;
  font-size: 14px;
  margin-bottom: 20px;
  width: 15vw;
}

.detectButton {
  /*position: fixed;*/
  /*z-index: 5;*/
  /*top: 70px;*/
  /*right: 75px;*/
  margin-top: 10px;
  margin-left: 93%;
  /*margin-right: 75px;*/
}

.form_half {
  width: 50%;
  padding-left: 1rem;
  padding-right: 1rem;
  padding-top: 1rem;
}

.mybutton__arrow {
  border: none;
  outline: 0;
  padding: 0;
  margin: 0;
  height: 36px;
  width: 36px;
  cursor: pointer;
  -webkit-transition: 0.3s;
  transition: 0.3s;
  border-radius: 50%;
  background-color: rgba(31, 45, 61, 0.11);
  color: #fff;
  position: absolute;
  top: 50%;
  z-index: 10;
  -webkit-transform: translateY(-50%);
  transform: translateY(-50%);
  text-align: center;
  font-size: 12px;
}

.mybutton__arrow-left {
  left: 16px;
}

.mybutton__arrow-right {
  right: 16px;
}
</style>
