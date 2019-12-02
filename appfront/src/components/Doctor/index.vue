<template>
  <section style="margin: auto;padding-left: 2%; padding-right: 2%">
    <el-row class="toolbar" style="padding-bottom: 0px;">
      <el-col :span="2">
        <el-dropdown @command="handleCommand" style="margin-left: 5%;">
          <el-button type="info">
            {{this.viewType}}<i class="el-icon-arrow-down el-icon--right"></i>
          </el-button>
          <el-dropdown-menu slot="dropdown">
            <el-dropdown-item command="a">按病人</el-dropdown-item>
            <el-dropdown-item command="b">按CT</el-dropdown-item>
          </el-dropdown-menu>
        </el-dropdown>
      </el-col>
      <el-col :span="22">
        <el-form :inline="true" :model="filters">
          <el-form-item>
            <el-input placeholder="姓名" v-model="filters.name"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" v-on:click="searchUser(1)">查询</el-button>
          </el-form-item>
          <el-form-item>
            <el-button @click="handleAdd" type="primary" v-if="viewType==='按病人'">新增</el-button>
            <el-button @click="openUploadDiag" type="primary" v-else>上传</el-button>
          </el-form-item>
        </el-form>
      </el-col>
    </el-row>
    <!--列表-->
    <template>
      <el-col :span="24">
        <el-table
          :data="users"
          @selection-change="selsChange"
          border
          highlight-current-row
          style="width: 100%"
          v-if="this.viewType==='按病人'"
          v-loading="listLoading"
        >
          <el-table-column type="index" width="60"></el-table-column>
          <el-table-column label="姓名" min-width="12%" prop="patient_info.patient_name" sortable></el-table-column>
          <el-table-column
            :formatter="formatSex"
            label="性别"
            min-width="13%"
            prop="patient_info.patient_sex"
            sortable
          ></el-table-column>
          <el-table-column label="出生日期" min-width="12%" prop="patient_info.patient_birth" sortable></el-table-column>
          <el-table-column label="联系电话" min-width="12%" prop="patient_info.patient_tel" sortable></el-table-column>
          <el-table-column label="地址" min-width="12%" prop="patient_info.patient_address"></el-table-column>
          <el-table-column :formatter="formatDate" label="诊断时间" min-width="12%" prop="DiagTime"></el-table-column>
          <el-table-column label="操作" width="200">
            <template scope="scope">
              <el-button
                @click="gotoDiagnosis(scope.$index, scope.row)"
                size="small"
                v-if="!hasDiaged(scope.$index, scope.row)"
              >去诊断
              </el-button>
              <el-button
                @click="modifyDiagnosis(scope.$index, scope.row)"
                size="small"
                v-if="hasDiaged(scope.$index, scope.row)"
              >编辑诊断
              </el-button>
              <el-button @click="handleDel(scope.$index, scope.row)" size="small" type="danger">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-table
          :data="ct_info"
          :element-loading-text="listLoading_text"
          @selection-change="selsChange"
          border
          highlight-current-row
          style="width: 100%"
          v-if="this.viewType==='按CT'"
          v-loading="listLoading"
        >
          <el-table-column type="index" width="60"></el-table-column>
          <el-table-column label="病人名称" min-width="200" prop="patient_name"></el-table-column>
          <el-table-column :formatter="formatDate2" label="上传时间" min-width="200" prop="upload_time"></el-table-column>
          <el-table-column :formatter="formatDetect" label="检测状态" min-width="200" prop="has_detected"></el-table-column>
          <el-table-column :formatter="formatPET" label="是否是PETCT" min-width="200" prop="is_pet"></el-table-column>
          <el-table-column label="操作" min-width="200">
            <template scope="scope">
              <el-button

                @click="gotoDetect(scope.$index, scope.row)"
                v-if="getCTStatus(scope.$index, scope.row)===1"
              >开始检测
              </el-button>
              <el-button
                @click="gotoResult(scope.$index, scope.row)"
                v-if="getCTStatus(scope.$index, scope.row)===2"
              >查看详情
              </el-button>
              <el-button
                @click="gotoFull(scope.$index, scope.row)"
                v-if="getCTStatus(scope.$index, scope.row)===2"
              >查看所有
              </el-button>
              <el-button
                @click="gotoPredictPET(scope.$index, scope.row)"
                v-if="getCTStatus(scope.$index, scope.row)===3"
              >开始预测
              </el-button>
              <el-button
                @click="showLivePredictResult(scope.$index, scope.row)"
                v-if="getCTStatus(scope.$index, scope.row)===4"
              >查看结果
              </el-button>

              <!--              <el-button type="danger" size="small" @click="handleDel(scope.$index, scope.row)">删除</el-button>-->

            </template>
          </el-table-column>


        </el-table>
      </el-col>
    </template>

    <!--工具条-->
    <el-col :span="24" class="toolbar">
      <el-pagination
        :current-page="page"
        :page-size="pageSize"
        :page-sizes="[2, 4, 8, 12]"
        :total="total"
        @current-change="handleCurrentChange"
        @size-change="handleSizeChange"
        layout="total, sizes, prev, pager, next, jumper"
        style="float:right"
      ></el-pagination>
    </el-col>

    <el-dialog :visible.sync="uploadCTDiagVis" title="上传CT">
      <el-form :model="uploadCTForm" label-position="right" label-width="80px">
        <el-form-item label="病人姓名">
          <el-input style="width: 80%;" v-model="uploadCTForm.patient_name"></el-input>
        </el-form-item>
        <el-form-item label="是PET?">
          <el-radio-group v-model="uploadCTForm.is_pet">
            <el-radio :label="true">是</el-radio>
            <el-radio :label="false">否</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="指定ID" v-if="uploadCTForm.is_pet">
          <el-input style="width: 80%;" v-model="uploadCTForm.specify_id"></el-input>
        </el-form-item>
        <el-form-item label="上传CT">
          <el-upload
            :action="uploadURL()"
            :before-upload="beforeFileUpload"
            :file-list="uploadPETList"
            :limit="1"
            :on-exceed="handleExceed"
            :on-success="handleUploadSuccess"
            :show-file-list="true"
            multiple
          >
            <el-button type="primary">点击上传</el-button>
          </el-upload>
        </el-form-item>
      </el-form>
      <div class="dialog-footer" slot="footer">
        <el-button @click="cancelUploadCT">取 消</el-button>
        <el-button @click="confirmUploadCT" type="primary">确 定</el-button>
      </div>
    </el-dialog>
  </section>
</template>

<script>
    import util from "../../common/util";
    //import NProgress from 'nprogress'
    import AllService from "../../services/allservices";

    var allService = new AllService();

    export default {
        data() {
            return {
                viewType: '按CT',

                doctorId: "",
                filters: {
                    name: ""
                },
                users: [],
                ct_info: [],

                total: 0,
                page: 1,
                pageSize: 8,
                listLoading: false,
                listLoading_text: '加载中',
                sels: [], //列表选中列

                //for diagnosis button change
                diagList: [1],
                //for upload ct dialog
                uploadCTDiagVis: false,
                // uploadSuccess: false,
                uploadCTForm: {
                    patient_name: '',
                    is_pet: false,
                    specify_id: '',
                },
                uploadFileList: [],
                uploadPETList: [],
                uploadCTName: '',

                predictLoading: false,
            };
        },
        methods: {
            getHasDiagInfo() {
                let params = {
                    doc_id: this.doctorId
                };
                allService.getDocDiagList(params, (isOk, data) => {
                    if (isOk) {
                        let diagInfo = data.data;
                        this.diagList = [];
                        for (let info in diagInfo) {
                            if (this.diagList.indexOf(diagInfo[info].id) === -1) {
                                this.diagList.push(diagInfo[info].id);
                            }
                        }
                    }
                });
            },

            hasDiaged(index, row) {
                // console.log(row)
                return this.diagList.indexOf(row.id) !== -1;
            },

            getCTStatus(index, row) {
                //status 1: not detect normal ct
                //status 2: detected normal ct
                //status 3: not predict PET ct
                //status 4: predicted PET ct
                if (!row.is_pet) {
                    return row.has_detected === 0 ? 1 : 2
                } else {
                    return row.has_detected === 0 ? 3 : 4
                }
            },

            uploadURL() {
                if (this.uploadCTForm.is_pet) {
                    return "http://127.0.0.1:8000/livePredict/uploadPET/"
                }
                return "http://127.0.0.1:8000/detecthit/uploadCT/"
            },
            gotoPredictPET(index, row) {
                let params={
                    pet_id: row.id,
                    specify_id: row.specify_id
                }
                allService.predictPET(params,(isok,data)=>{
                    if(isok){
                        let date =data.data[0]
                        let live =data.data[1]
                        this.$alert("date:"+date.toString()+"- live:"+live.toString())
                    }
                })
            },
            showLivePredictResult(index, row) {
                let params={
                    pet_id: row.id
                }
                allService.getPETResultByPID(params, (isOk, data) => {
                    if (isOk) {
                        let resp = data.data
                        if(resp!==null){
                            let alertString = "date:"+resp[0].toString()+"- live:"+resp[1].toString()
                            this.$alert(alertString, '预测结果', {
                                confirmButtonText: '确定',
                            });
                        }else{
                            this.$alert("error", '预测结果', {
                                confirmButtonText: '确定',
                            });
                        }

                    }
                })
            },

            modifyDiagnosis(index, row) {
                console.log("in modifyDiagnosis");
                console.log(row);
                let params = {
                    id: row.id
                };
                allService.getSinglePatientDiag(params, (isOk, data) => {
                    if (isOk) {
                        let temp = data.data[0];
                        console.log(temp);
                        console.log(
                            temp.DiagRemark.toString()
                                .substr(1, temp.DiagRemark.length - 2)
                                .split(",")
                        );
                        var trans_vars = {
                            doctorId: temp.doc_id,
                            diagId: row.id,
                            symptomForm: {
                                symptom: temp.patient_symptom,
                                hasCT: !(temp.CTURL === "" || temp.CTURL === undefined),
                                ct_name: temp.CTURL
                            },
                            summaryForm: {
                                diagnosisResult: temp.DiagResult
                            }
                        };
                        console.log('trans_vars:');
                        console.log(trans_vars);
                        sessionStorage.setItem(
                            "vars_from_modify",
                            JSON.stringify(trans_vars)
                        );
                        sessionStorage.setItem("patient", JSON.stringify(row.patient_info));
                        // let img_list = temp.DiagRemark.toString().substr(1, temp.DiagRemark.length - 2).split(", ")
                        let img_list = temp.DiagRemark;
                        let img_arr = img_list
                            .replace("[", "")
                            .replace("]", "")
                            .split(", ");
                        if (img_arr[0] === "") {
                            img_arr = [];
                        }
                        console.log(JSON.stringify(img_arr));

                        console.log("in diag index img list>>>>>>>>>");

                        sessionStorage.setItem("img_list", JSON.stringify(img_list));

                        this.$router.push({name: "diagIndex"});
                    }
                });
            },

            formatDate(row, column) {
                let date = new Date(row.DiagTime);
                return util.formatDate.format(date, "yyyy-MM-dd");
            },
            formatDate2(row, column) {
                let date = new Date(row.upload_time);
                return util.formatDate.format(date, "yyyy-MM-dd hh:mm:ss");
            },
            //性别显示转换
            formatSex(row) {
                console.log('in format sex');
                console.log(row);
                return row.patient_info.patient_sex === 1 ? "男" : row.patient_info.patient_sex === 2 ? "女" : "未知";
                // return "未知";
            },

            formatDetect(row) {
                return row.has_detected === 0 ? "未检测" : row.has_detected === 1 ? "已检测" : "错误"
            },

            formatPET(row) {
                return row.is_pet === false ? "否" : row.is_pet === true ? "是" : "错误"
            },

            handleCurrentChange(val) {
                this.page = val;
                if (this.filters.name === "") {
                    this.getUsers();
                } else {
                    this.searchUser();
                }
            },

            handleSizeChange(val) {
                this.pageSize = val;
                if (this.filters.name === "") {
                    this.getUsers();
                } else {
                    this.searchUser();
                }
            },
            //获取用户列表
            getUsers() {
                let para = {
                    page: this.page,
                    pageSize: this.pageSize,
                    doctorId: this.doctorId
                };
                this.listLoading = this.ct_info.length !== 0; //need to be true
                //NProgress.start();
                allService.getPatientByDocId(para, (isOk, data) => {
                    if (isOk) {
                        if (data.error_num === 0) {
                            this.users = data.data;
                            this.total = data.total;
                            this.listLoading = false;
                        } else {
                            this.$message.error("获取数据出错");
                        }
                    } else {
                        this.$message.error("网络错误");
                    }
                });
            },
            //获取CT列表
            getCTs() {
                let para = {
                    page: this.page,
                    pageSize: this.pageSize,
                    doctorId: this.doctorId
                };
                this.listLoading = this.ct_info.length !== 0; //need to be true
                //NProgress.start();
                allService.getCTInfoList(para, (isOk, data) => {
                    if (isOk) {
                        if (data.error_num === 0) {
                            this.ct_info = data.data;
                            this.total = data.total;
                            this.listLoading = false;
                        } else {
                            this.$message.error("获取数据失败");
                        }
                    } else {
                        this.$message.error("网络错误");
                    }
                });
            },

            //query
            searchUser(curPage) {
                if (curPage !== undefined) {
                    this.page = curPage;
                }
                let param = {
                    page: this.page,
                    pageSize: this.pageSize,
                    doctorId: this.doctorId,
                    patientName: this.filters.name
                };
                this.listLoading = true; //need to be true
                //NProgress.start();
                allService.getPatientByName(param, (isOk, data) => {
                    if (isOk) {
                        if (data.error_num === 0) {
                            this.users = data.data;
                            this.total = data.total;
                            this.listLoading = false;
                        }
                        if (data.error_num === 1) {
                            this.users = data.data;
                            this.total = data.total;
                            this.listLoading = false;
                            this.$message.warning("该病人并不属于该医生");
                        }
                    } else {
                        this.$message.error("获取数据失败");
                    }
                });
            },

            checkDocInfo() {
                let params = {
                    doctorId: this.doctorId
                };
                allService.checkDoctorInfo(params, (isOk, data) => {
                    if (isOk) {
                        if (!data.data) {
                            this.$confirm("你的信息未完善，是否完善?", "提示", {
                                confirmButtonText: "确定",
                                cancelButtonText: "以后提醒我",
                                type: "warning"
                            })
                                .then(() => {
                                    this.$router.push({name: "docInfo"});
                                })
                                .catch(() => {
                                    this.delayReminder();
                                });
                        }
                    } else {
                        this.$message.error("网络错误");
                    }
                });
            },

            delayReminder() {
                let params = {
                    doctorId: this.doctorId
                };
                allService.resetInformDate(params, (isOk, data) => {
                    if (isOk) {
                        console.log("delay success");
                    } else {
                        this.$message.error("网络错误");
                    }
                });
            },

            gotoDiagnosis(index, row) {
                this.$emit("showButton");
                this.$emit("hidedropdown");
                var trans_vars = {
                    diagId: row.id,
                    symptomForm: {
                        symptom: "",
                        hasCT: false,
                        ct_name: ""
                    },
                    summaryForm: {
                        diagnosisResult: "",
                        hasNodule: 0
                    }
                };
                sessionStorage.setItem("vars_from_modify", JSON.stringify(trans_vars));
                sessionStorage.setItem("patient", JSON.stringify(row.patient_info));
                sessionStorage.setItem("img_list", JSON.stringify([]));
                this.$router.push({name: "diagIndex"});
            },

            gotoDetect(index, row) {
                // this.$message.success('success go to detect page!')
                let para = {
                    'dirname': row.dirname,
                    'ctId': row.id
                };
                this.listLoading_text = '预测中';
                this.listLoading = true;
                allService.predictCT(para, (isOk, data) => {
                    if (isOk) {
                        if (data.error_num === 0) {
                            this.$notify({
                                title: '提示',
                                message: '检测完成',
                                duration: 4500
                            });

                            this.listLoading_text = '加载中';
                            setTimeout(this.getCTs(), 3000)
                        } else {
                            this.$message.error(data.msg)
                        }
                    }
                    this.listLoading = false;
                })
            },

            gotoResult(index, row) {
                console.log(row);
                sessionStorage.setItem('ctInfo', JSON.stringify(row));
                this.$router.push({name: "ctResult"})
            },
            gotoFull(index, row) {
                console.log(row);
                sessionStorage.setItem('ctInfo', JSON.stringify(row));
                this.$router.push({name: "ctFull"})
            },
            //删除
            handleDel: function (index, row) {
                this.$confirm("确认删除该记录吗?", "提示", {
                    type: "warning"
                })
                    .then(() => {
                        this.listLoading = true;
                        //NProgress.start();
                        let para = {id: row.id};
                        allService.delDiagInfo(para, (isOk, data) => {
                            if (isOk) {
                                this.listLoading = false;
                                this.$message({
                                    message: "删除成功",
                                    type: "success"
                                });
                                this.getUsers();
                            }
                        })

                    })
                    .catch(() => {
                    });
            },

            handleAdd: function () {
                this.$router.push({name: "addPatient"});
            },

            selsChange: function (sels) {
                this.sels = sels;
            },

            handleCommand(command) {
                if (command === 'a') {
                    //goto patient page
                    this.viewType = '按病人'
                }
                if (command === 'b') {
                    this.viewType = '按CT'
                }
            },

            openUploadDiag() {
                this.uploadCTDiagVis = true
            },

            confirmUploadCT() {
                this.uploadCTDiagVis = false;
                // unzip the uploaded zip CT file
                this.listLoading = true;
                if (this.uploadCTForm.is_pet) {
                    let pet_params = {
                        'filename': this.uploadCTName,
                        'patient_name': this.uploadCTForm.patient_name,
                        'doctorId': this.doctorId,
                        'specify_id': this.uploadCTForm.specify_id
                    };
                    allService.extractPET(pet_params, (isOk, data) => {
                        if (isOk) {
                            if (data.error_num === 0) {
                                this.uploadCTDiagVis = false;
                                this.uploadCTName = '';
                                this.uploadFileList = [];
                                this.uploadCTForm.patient_name = '';
                                this.getCTs();
                                this.listLoading = false
                            } else {
                                this.$message.error(data.msg)
                            }
                        } else {
                            this.$message.error("获取数据失败");
                        }
                    })
                } else {
                    let params = {
                        'filename': this.uploadCTName,
                        'patient_name': this.uploadCTForm.patient_name,
                        'doctorId': this.doctorId,
                    };
                    allService.extractCT(params, (isOk, data) => {
                        if (isOk) {
                            if (data.error_num === 0) {
                                this.uploadCTDiagVis = false;
                                this.uploadCTName = '';
                                this.uploadFileList = [];
                                this.uploadCTForm.patient_name = '';
                                this.getCTs();
                                this.listLoading = false
                            } else {
                                this.$message.error(data.msg)
                            }
                        } else {
                            this.$message.error("获取数据失败");
                        }
                    })
                }

            },

            cancelUploadCT() {
                this.uploadCTDiagVis = false
                //delete the uploaded zip file?
            },

            handleExceed(files, fileList) {
                this.$message.warning(
                    `当前限制选择 1 个文件，本次选择了 ${
                        files.length
                    } 个文件，共选择了 ${files.length + fileList.length} 个文件`
                );
            },

            handleUploadSuccess(res, file) {
                this.uploadCTName = res.data;
                this.$alert(this.uploadURL())
            },
            handleUploadPETSuccess(res, file) {
                this.$message.success("上传文件成功！")
            },

            beforeFileUpload(file) {
                // const isZip = file.type === "application/x-zip-compressed";
                const isZip = (file.type.indexOf("zip") !== -1)
                console.log(file.type.indexOf("zip"));
                if (!isZip) {
                    this.$message.error("上传文件只能是zip格式!");
                }
                return isZip;
            },
        },
        mounted() {
            var user = sessionStorage.getItem("user");
            if (user) {
                user = JSON.parse(user);
                this.doctorId = user.id || "";
            }
            this.getUsers(); //查询获取所有patient列表
            this.getCTs();
            this.checkDocInfo();
            this.getHasDiagInfo(); //查询获取每个patient的是否已诊断情况
        }
    };
</script>

<style scoped>
  body .el-table th.gutter {
    display: table-cell !important;
  }

</style>
