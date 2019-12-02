<!-- 管理CT页面： 包括上传CT ， 管理CT， 显示CT-->
<template>
  <section style="padding-left: 0;padding-right: 20%">
    <el-row :gutter="20" >
      <!--<el-col :span="6" style="margin-top: 3em">-->
      <!--&lt;!&ndash; 上传用户ct区域&ndash;&gt;-->
      <!--<el-upload-->
      <!--class="avatar-uploader"-->
      <!--action="http://127.0.0.1:8000/detect/addPatientFile/"-->
      <!--multiple-->
      <!--:limit="2"-->
      <!--:on-exceed="handleExceed"-->
      <!--:on-success="handleUploadSuccess"-->
      <!--:before-upload="beforeFileUpload">-->
      <!--<img v-if="imageUrl" src="../../../assets/zip-file.png" class="avatar">-->
      <!--<i v-else class="el-icon-plus avatar-uploader-icon"></i>-->
      <!--</el-upload>-->

      <!--</el-col>-->
      <el-col :span="6" v-for="ct in cts" style="margin-top: 3em">
        <el-card :body-style="{ padding: '0px'}">
          <div style="text-align: center">
            <svg class="icon" aria-hidden="true">
              <use xlink:href="#my-icon-folder"></use>
            </svg>
          </div>

          <div style="padding: 14px;">
            <div class="bottom clearfix">
              <span>upload time: </span>
              <span>{{ formatDate(ct.upload_time, 'yyyy-MM-dd hh:mm:ss') }}</span>
              <el-button type="text" class="button" @click="gotoAllPic(ct)">查看全部</el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>



    <div>
      <el-upload
        class="fix-button"
        action="http://127.0.0.1:8000/detect/addPatientFile/"
        :limit="2"
        multiple
        :on-exceed="handleExceed"
        :on-success="handleUploadSuccess"
        :before-upload="beforeFileUpload"
        :show-file-list="false"
      >
        <!--<i class="el-icon-plus avatar-uploader-icon"></i>-->
        <el-button type="primary"  circle icon="el-icon-upload2" style="width: 80px;height: 80px;"></el-button>

      </el-upload>

      <!--<el-button @click="clickAddButton" type="primary" class="fix-button" circle icon="el-icon-upload2"></el-button>-->
    </div>

  </section>
</template>

<script>
  import AllService from "../../../services/allservices.js";
  import util from "../../../common/util";

  var allService = new AllService();
  export default {
    data() {
      return {
        //for upload component
        fileList: [],
        imageUrl: '',
        //for display the file folder
        CT_nums: 6,
        cts: [],
        patient: {},


        //for /display all image
        allImageList: [],
        // ct_height: 0,

      };
    },
    methods: {
      formatDate(date, pattern) {
        date = new Date(date)
        return util.formatDate.format(date, pattern)
      },
      formatImgSrc(base64code) {
        return 'data:image/jpg;base64,' + base64code
      },
      getctnums() {
        let params = {
          patient_id: this.patient.id
        }
        allService.getCTByPatient(params, (isok, data) => {
          if (isok) {
            if (data.error_num === 0) {
              this.cts = data.data
              this.CT_nums = data.total
              console.log('ct_nums: ', data.total)
            }
          }
        })
      },
      gotoAllPic(ct) {
        //let allpicPath = ct.ct_path;

        console.log('start request for image')
        var params = {
          name: ct.ct_name,
          path: ct.ct_path
        }
        sessionStorage.setItem('allPicParam', JSON.stringify(params))
        this.$emit('showAllImages')



      },
      // under is upload file function

      handleExceed(files, fileList) {
        this.$message.warning(
          `当前限制选择 2 个文件，本次选择了 ${
            files.length
            } 个文件，共选择了 ${files.length + fileList.length} 个文件`
        );
      },
      handleUploadSuccess(res, file) {
        console.log(file)
        var filename = file.name
        var lastindex = filename.lastIndexOf('.')
        var purename = filename.slice(0, lastindex)
        console.log(purename)
        var params = {
          patient_id: this.patient.id,
          filename: purename
        }

        allService.addCTInfo(params, (isOk, data) => {
          if (isOk) {
            if (data.error_num === 0) {
              this.$message.success("add success")
              this.imageUrl = '../../../assets/zip-file.png'
              this.getctnums()
            } else {
              this.$message.error(data.msg)
            }
          }
          else {
            this.$message.error('网络错误')
          }
        })

      },
      beforeFileUpload(file) {
        const isZip = file.type === "application/x-zip-compressed";
        console.log(file.type);
        if (!isZip) {
          this.$message.error("上传文件只能是zip格式!");
        }
        return isZip;
      },
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
      this.getctnums()
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
    border-color: #409EFF;
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
    clear: both
  }


</style>
