<template>
  <section style="padding-left: 0;padding-right: 0;overflow: hidden">
    <el-header>
      <el-button class="interpolateButton" @click="showInterpolation" v-if="!showInterpolationVis">
        中间插值
      </el-button>
      <el-button class="interpolateButton" @click="showOnlyOrigin" v-if="showInterpolationVis">
        只看原图
      </el-button>
    </el-header>

    <el-main class="mainClass">
      <el-row>
        <el-col :span="12">
          <div class="block" @mousemove="updatexyleft">
            <span class="demonstration">index: {{this.imageIndex}}</span>
            <el-image
              style="width: 400px; height: 400px; text-align: center"
              :src="formatImgSrc(currentImage)"
              :fit="fit"></el-image>
          </div>
        </el-col>
        <el-col :span="12">
          <div class="block" @mousemove="updatexyright" v-if="showInterpolationVis">
            <span class="demonstration">index: {{this.interIndex / this.internum}}</span>
            <el-image
              style="width: 400px; height: 400px; text-align: center"
              :src="formatImgSrc(currentInterImage)"
              :fit="fit"></el-image>
          </div>
        </el-col>
      </el-row>
    </el-main>
    <!--    <el-dialog title="插值结果" width="70%" :visible.sync="showInterpolationVis" style="text-align: center; overflow: hidden">-->

    <!--    </el-dialog>-->

  </section>
</template>

<script>
  import AllService from "../../services/allservices.js";
  import util from "../../common/util";
  import login from "../User/login";

  var allService = new AllService();
  export default {
    data() {
      return {
        ctInfo: {},
        fit: 'cover',
        showInterpolationVis: false,
        timer: '',

        originArray: [],
        currentImage: '',
        imageIndex: 0,

        internum: 5,//需要视后端决定，目前是5

        interpolationArray: [],
        currentInterImage: '',
        interIndex: 0,

        scrollPart: 0,//0:init; -1:left; 1:right
      };
    },
    methods: {

      initVars() {
        this.originArray = [];
        this.interpolationArray = [];
      },
      formatImgSrc(base64code) {
        return "data:image/jpg;base64," + base64code;
      },
      ruleIndex1(index) {
        if (index < 0) {
          index = 0
        }
        if (index >= this.originArray.length) {
          index = this.originArray.length
        }
        return index
      },
      ruleIndex2(index) {
        if (index < 0) {
          index = 0
        }
        if (index >= this.interpolationArray.length) {
          index = this.interpolationArray.length
        }
        return index
      },
      handleScroll(e) {
        // let direction =e.deltaY>0?'down':'up'
        // console.log(e.deltaY)
        if (this.scrollPart === -1) {
          if (e.deltaY > 0) {
            this.imageIndex = this.ruleIndex1(this.imageIndex + 1)
            this.currentImage = this.originArray[this.imageIndex]
          } else {
            this.imageIndex = this.ruleIndex1(this.imageIndex - 1)
            this.currentImage = this.originArray[this.imageIndex]
          }
        } else if (this.scrollPart === 1) {
          if (e.deltaY > 0) {
            this.interIndex = this.ruleIndex2(this.interIndex + 1)
            this.currentInterImage = this.interpolationArray[this.interIndex]
          } else {
            this.interIndex = this.ruleIndex2(this.interIndex - 1)
            this.currentInterImage = this.interpolationArray[this.interIndex]
          }
        }

        // console.log(this.imageIndex)
      },
      queryStatus() {
        let params = {
          "ct_id": this.ctInfo.id
        }
        allService.queryInterStatus(params, (isok, data) => {
          if (isok) {
            if (data.data === 1) {
              this.timer = null
              this.getInterpolationImage()
            } else {
              this.timer = setTimeout(() => {
                this.queryStatus()
              }, 4000);
            }
          }
        })

      },
      getInterpolationImage() {
        let params = {
          "dirname": this.ctInfo.dirname
        }
        allService.getInterpolationImage(params, (isok, data) => {
          if (isok) {
            this.interpolationArray = data.data;
            this.currentInterImage = this.interpolationArray[0]
          }
        })
      },
      getAllPic() {
        let params = {
          "dirname": this.ctInfo.dirname
        };
        allService.getOriginImg(params, (isok, data) => {
          if (isok) {
            this.originArray = data.data;
            this.currentImage = this.originArray[0];
          }
        });
      },
      showInterpolation() {
        this.showInterpolationVis = true;
        this.$message({
          message: '开始插值'
        });
        let params = {
          "dirname": this.ctInfo.dirname,
          "ct_id": this.ctInfo.id
        };
        allService.interpolateCT(params, (isok, data) => {
          if (isok) {
            this.interpolationArray = data.data;
            console.log('inter array length:', this.interpolationArray.length)
            this.currentInterImage = this.interpolationArray[0];
            this.$message({
              message: '插值成功',
              type: 'success'
            });
          }
        })
        setTimeout(() => {
          this.queryStatus()
          console.log('set up a timer to query interpolation status')
        }, 1000)
      },
      showOnlyOrigin() {
        this.showInterpolationVis = false;
      },
      updatexyleft(event) {
        this.scrollPart = -1
      },
      updatexyright(event) {
        this.scrollPart = 1
      },


    },
    created() {
      var user = sessionStorage.getItem("user");
      if (user) {
        user = JSON.parse(user);
        this.doctorId = user.id || "";
      }
      if (sessionStorage.getItem("ctInfo")) {
        let ctInfo = JSON.parse(sessionStorage.getItem("ctInfo"));
        this.ctInfo = ctInfo
        console.log('in show images ct info is:')
        console.log(this.ctInfo)
      }
    },
    mounted() {
      this.initVars();
      this.getAllPic();
      window.addEventListener('mousewheel', this.handleScroll, false)
      this.$emit("showButton");
    }
  };
</script>

<style scoped>
  .headerClass {
    background: #f2f2f2;
    padding: 10px;
    border-radius: 10px;
    margin: 10px 0px;
  }

  .mainClass {
    text-align: center;
  }

  .interpolateButton {
    position: fixed;
    z-index: 5;
    top: 70px;
    right: 75px;
    margin-top: 10px;
    /*margin-left: 93%;*/
    /*margin-right: 75px;*/
  }

  .block {
    text-align: center;
  }

  .halfblock {
    width: 50%;
    text-align: center;
  }

  .demonstration {
    text-align: center;
    display: block;
    color: #8492a6;
    font-size: 14px;
    margin-bottom: 20px;

  }
</style>
