<template>
  <section style="padding-left: 0;padding-right: 0%">
    <el-header class="headerClass">
      <span>该病人患恶性肿瘤的总体概率是：{{prob_overall}}</span>
      <el-form :inline="true" style="float: right">
        <el-form-item>
          <el-button type="primary" v-on:click="cover()">病灶回溯</el-button>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" v-on:click="insertframe()">CT插帧</el-button>
        </el-form-item>
      </el-form>
    </el-header>
    <el-main class="mainClass">
      <el-row v-for="imagePair in pairSum" style="margin-top: 10px; min-height: 100px">
        <el-col :span="12">
          <el-col :span="16">
            <el-image
              v-image-preview
              :src="formatImgSrc(imagePair[0].imagecode)"
              fit="contain"
              class="imageClass"
            ></el-image>
          </el-col>
          <el-col :span="8">
            <el-form :ref="imagePair[0]">
              <el-form-item label="恶性可能性:">
                <span>{{imagePair[0].prob}}</span>
              </el-form-item>
              <el-form-item label="大小(mm):">
                <span>{{imagePair[0].size}}</span>
              </el-form-item>
              <el-form-item label="坐标:">
                <span>{{imagePair[0].originId}}</span>
              </el-form-item>
              <el-form-item label="操作:">
                <el-button @click="showCoverResult(imagePair[0].index)" :disabled="hasCoverResult">查看详情</el-button>
              </el-form-item>
            </el-form>
          </el-col>
        </el-col>
        <el-col :span="12" v-if="imagePair.length===2">
          <el-col :span="16">
            <el-image
              v-image-preview
              :src="formatImgSrc(imagePair[1].imagecode)"
              fit="contain"
              class="imageClass"
            ></el-image>
          </el-col>
          <el-col :span="8">
            <el-form :ref="imagePair[1]">
              <el-form-item label="恶性可能性:">
                <span>{{imagePair[1].prob}}</span>
              </el-form-item>
              <el-form-item label="大小(mm):">
                <span>{{imagePair[1].size}}</span>
              </el-form-item>
              <el-form-item label="坐标:">
                <span>{{imagePair[1].originId}}</span>
              </el-form-item>
              <el-form-item label="操作:">
                <el-button @click="showCoverResult(imagePair[1].index)" :disabled="hasCoverResult">查看详情</el-button>
              </el-form-item>
            </el-form>
          </el-col>
        </el-col>
      </el-row>
    </el-main>
    <el-dialog title="回溯结果" width="70%" :visible.sync="showCoverResultVis">
      <el-col span="18" style="min-height: 500px">
        <el-row style="text-align: center"><span class="demonstration">原图片</span></el-row>
        <el-row style="min-height: 400px;text-align: center">
          <el-image
            style="width: 400px; height: 400px;text-align: center"
            :src="formatImgSrc(coverImageOrigin)"
            :fit="fit"></el-image>
        </el-row>
      </el-col>
      <el-col span="6">
        <el-row style="text-align: center"><span class="demonstration">原结节</span></el-row>
        <el-row style="text-align: center">
          <el-image
            style="width: 150px; height: 150px; text-align: center"
            :src="formatImgSrc(coverImageNodule)"
            :fit="fit"></el-image>
        </el-row>
        <el-row style="text-align: center; margin-top: 30px"><span class="demonstration">overlay结果</span></el-row>
        <el-row style="text-align: center">
          <el-image
            style="width: 150px; height: 150px; text-align: center"
            :src="formatImgSrc(coverImageOverlay)"
            :fit="fit"></el-image>
        </el-row>
      </el-col>

    </el-dialog>

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

                prob_overall: 0,
                allAIImageList: [],
                allAIprob: [],
                allAIcoord: [],
                allAIsize: [],
                allAIImageList_length: 0,

                eachPair: 2,
                pairSum: [],
                pairLength: 0,

                hasCoverResult: true,
                fit: 'contain',
                showCoverResultVis: false,
                coverImageOrigin: '',
                coverImageNodule: '',
                coverImageOverlay: '',

            };
        },
        methods: {
            initVars() {
                this.allAIImageList = [];
            },
            formatImgSrc(base64code) {
                return "data:image/jpg;base64," + base64code;
            },
            getAllPic() {
                let params = {
                    "dirname": this.ctInfo.dirname
                };
                allService.getResultImg(params, (isok, data) => {
                    console.log("get all predict image");
                    if (isok) {
                        this.allAIImageList = data.data[0];
                        this.allAIprob = data.data[1];
                        this.allAIcoord = data.data[2];
                        this.allAIsize = data.data[3];
                        this.prob_overall = data.data[4]
                        this.allAIImageList_length = data.data[0].length;
                        this.getPaired()
                    }
                });
            },
            getPaired() {
                this.pairLength = Math.ceil(this.allAIImageList_length / this.eachPair)
                let templist = []
                for (let i = 0; i < this.pairLength; i++) {
                    templist = []
                    let imageObj0 = {
                        imagecode: this.allAIImageList[2 * i],
                        prob: this.allAIprob[2 * i],
                        size: this.allAIsize[2 * i],
                        originId: this.allAIcoord[2 * i],
                        index: 2 * i,
                    }
                    templist.push(imageObj0)
                    if (i !== this.pairLength - 1 || this.pairLength % 2 === 0) {
                        let imageObj1 = {
                            imagecode: this.allAIImageList[2 * i + 1],
                            prob: this.allAIprob[2 * i + 1],
                            size: this.allAIsize[2 * i + 1],
                            originId: this.allAIcoord[2 * i + 1],
                            index: 2 * i + 1,
                        }
                        templist.push(imageObj1)
                    }
                    this.pairSum.push(templist)
                }
            },
            cover() {
                let para = {
                    "patientname": this.ctInfo.dirname,
                }
                allService.coverCT(para, (isok, data) => {
                    if (isok) {
                        if (data.error_num === 0) {
                            this.hasCoverResult = false
                        } else {
                            this.$message.error('回溯出错!')
                        }
                    }
                })
            },
            insertframe() {

            },
            showCoverResult(index) {
                console.log('index is', index)
                let indexPara = {
                    "index": index,
                    "patientName": this.ctInfo.dirname
                }
                allService.getCoverResultById(indexPara, (isok, data) => {
                    if (isok) {
                        if (data.error_num === 0) {
                            this.showCoverResultVis = true;
                            this.coverImageOrigin = this.allAIImageList[index];
                            this.coverImageNodule = data.data[0];
                            this.coverImageOverlay = data.data[1];
                        }
                    }
                })
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

  }

  .imageClass {

  }
</style>
