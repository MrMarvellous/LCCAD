<template>
  <section style="margin: auto;padding-left: 10%;padding-right: 10%">
    <template>
      <el-col :span="24" class="toolbar" style="padding-bottom: 0px;">
        <el-form :inline="true" :model="filters">
          <el-form-item>
            <el-input v-model="filters.name" placeholder="姓名"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" v-on:click="searchUser(1)">查询</el-button>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleAdd">新增</el-button>
          </el-form-item>
        </el-form>
      </el-col>

      <el-col :span="24">
        <el-table
          :data="users"
          highlight-current-row
          v-loading="listLoading"
          style="width: 100%"
          border
        >
          <el-table-column type="index" width="60"></el-table-column>
          <el-table-column prop="doc_name" label="姓名" width="120" sortable></el-table-column>
          <el-table-column
            prop="doc_sex"
            label="性别"
            width="100"
            :formatter="formatSex"
            sortable
          ></el-table-column>
          <el-table-column prop="doc_description" label="职称" width="150"></el-table-column>
          <el-table-column prop="doc_birth" label="出生日期" width="150" sortable></el-table-column>
          <el-table-column prop="doc_depart" label="部门" width="150" sortable></el-table-column>
          <el-table-column prop="doc_tel" label="联系方式" width="200"></el-table-column>

          <el-table-column label="操作">
            <template scope="scope">
              <el-button
                size="small"
                @click="modifyDoctor(scope.$index, scope.row)"
              >修改
              </el-button>
              <el-button
                size="small"
                @click="deleteDoctor(scope.$index, scope.row)"
                type="danger"
              >删除
              </el-button>
              <el-button
                size="small"
                @click="resetpassword(scope.$index, scope.row)"
                type="warning"
              >重置密码
              </el-button>

            </template>
          </el-table-column>
        </el-table>
      </el-col>
    </template>

    <el-col :span="24" class="toolbar">
      <el-pagination
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        :current-page="page"
        :page-sizes="[2, 4, 8, 12]"
        :page-size="pageSize"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        style="float:right"
      ></el-pagination>
    </el-col>

    <!--添加doctor-->
    <el-dialog title="添加医生" :visible.sync="addDialogVisible" width="50%">
      <el-form ref="addForm" :model="addForm" label-width="100px">
        <el-form-item label="姓名" prop="doc_name">
          <el-input v-model="addForm.doc_name"></el-input>
        </el-form-item>
        <el-form-item label="性别" prop="doc_sex">
          <el-radio-group v-model="addForm.doc_sex">
            <el-radio :label="1">男</el-radio>
            <el-radio :label="2">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="电话" prop="doc_tel">
          <el-input v-model="addForm.doc_tel"></el-input>
        </el-form-item>
        <el-form-item label="电子邮箱" prop="doc_email">
          <el-input v-model="addForm.doc_email"></el-input>
        </el-form-item>
        <el-form-item label="生日" prop="doc_birth">
          <el-date-picker v-model="addForm.doc_birth" type="date" placeholder="选择日期"></el-date-picker>
        </el-form-item>
        <!--<el-form-item label="医院" prop="doc_hospital">-->
        <!--<el-input v-model="addForm.doc_hospital" ></el-input>-->
        <!--</el-form-item>-->
        <el-form-item label="科室" prop="doc_depart">
          <el-input v-model="addForm.doc_depart"></el-input>
        </el-form-item>
        <el-form-item label="职称" prop="doc_description">
          <el-input v-model="addForm.doc_description"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="onSubmit">保存</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>

    <!--修改doctor-->
    <el-dialog title="修改医生" :visible.sync="modifyDialogVisible" width="50%">
      <el-form ref="modifyForm" :model="modifyForm" label-width="100px">
        <el-form-item label="姓名" prop="doc_name">
          <el-input v-model="modifyForm.doc_name"></el-input>
        </el-form-item>
        <el-form-item label="性别" prop="doc_sex">
          <el-radio-group v-model="modifyForm.doc_sex">
            <el-radio :label="1">男</el-radio>
            <el-radio :label="2">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="电话" prop="doc_tel">
          <el-input v-model="modifyForm.doc_tel"></el-input>
        </el-form-item>

        <el-form-item label="生日" prop="doc_birth">
          <el-date-picker v-model="modifyForm.doc_birth" type="date" placeholder="选择日期"></el-date-picker>
        </el-form-item>
        <!--<el-form-item label="医院" prop="doc_hospital">-->
        <!--<el-input v-model="addForm.doc_hospital" ></el-input>-->
        <!--</el-form-item>-->
        <el-form-item label="科室" prop="doc_depart">
          <el-input v-model="modifyForm.doc_depart"></el-input>
        </el-form-item>
        <el-form-item label="职称" prop="doc_description">
          <el-input v-model="modifyForm.doc_description"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="onSubmitModify">保存</el-button>
        </el-form-item>
      </el-form>
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
        users: [],
        total: 0,
        page: 1,
        pageSize: 8,
        listLoading: false,
        filters: {
          name: ""
        },
        addForm: {
          doc_name: '',
          doc_sex: '',
          doc_tel: '',
          doc_email: '',
          doc_birth: '',
          doc_depart: '',
          doc_description: ''
        },
        modifyForm: {
          doc_name: '',
          doc_sex: '',
          doc_tel: '',
          doc_birth: '',
          doc_depart: '',
          doc_description: ''
        },
        addDialogVisible: false,
        modifyDialogVisible: false,
        currentDocId: '',
      };
    },
    methods: {
      getAllUser() {
        let params = {
          page: this.page,
          pageSize: this.pageSize
        }
        allService.adminGetAllDoctor(params, (isOk, data) => {
          if (isOk) {
            this.users = data.data
            this.total = data.total
          }
        })
      },
      formatSex: function (row, column) {
        console.log(row);
        return row.doc_sex === 1
          ? "男"
          : row.doc_sex === 2
            ? "女"
            : "未知";
      },
      handleCurrentChange(val) {
        this.page = val;
        if (this.filters.name === "") {
          this.getAllUser();
        } else {
          this.searchUser(this.page);
        }
      },
      handleSizeChange(val) {
        this.pageSize = val;
        if (this.filters.name === "") {
          this.getAllUser();
        } else {
          this.searchUser(this.page);
        }
      },
      searchUser(curPage) {
        if (this.filters.name === "") {
          this.getAllUser()
          return
        }
        if (curPage !== undefined) {
          this.page = curPage;
        }
        let param = {
          page: this.page,
          pageSize: this.pageSize,
          docName: this.filters.name
        };
        this.listLoading = true; //need to be true
        //NProgress.start();
        allService.getDoctorByName(param, (isOk, data) => {
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

            }
          } else {
            this.$message.error("获取数据失败");
          }
        });
      },
      handleAdd() {
        this.addDialogVisible = true

      },
      onSubmit() {
        let params = this.addForm
        params.doc_birth = util.formatDate.format(this.addForm.doc_birth, "yyyy-MM-dd");
        allService.adminAddDoctor(params, (isOk, data) => {
          if (data.error_num === 0) {
            this.$message.success("添加成功");
            this.addDialogVisible = false
            this.getAllUser()
          } else {
            this.$message.error(data.msg)
          }
        })
      },
      modifyDoctor(index, row) {
        this.modifyDialogVisible = true
        // console.log('admin page modify row')
        // console.log(row)
        this.modifyForm.doc_name = row.doc_name
        this.modifyForm.doc_birth = row.doc_birth
        this.modifyForm.doc_sex = row.doc_sex
        this.modifyForm.doc_depart = row.doc_depart
        this.modifyForm.doc_tel = row.doc_tel
        this.modifyForm.doc_description = row.doc_description
        this.currentDocId = row.id
      },
      onSubmitModify() {
        let params = {
          id: this.currentDocId,
          docName: this.modifyForm.doc_name,
          docSex: this.modifyForm.doc_sex,
          docBirth: this.modifyForm.doc_birth,
          docTel: this.modifyForm.doc_tel,
          docDepart: this.modifyForm.doc_depart,
          docDescription: this.modifyForm.doc_description,
        }
        allService.updateDoctorInfo(params, (isOk, data) => {
          if (data.error_num === 0) {
            this.$message.success('修改成功')
            this.modifyDialogVisible = false
            this.getAllUser()
          } else {
            this.$message.error(data.msg)
          }
        })
      },
      deleteDoctor(index, row) {
        this.$confirm("确定删除吗?", "提示", {
          confirmButtonText: "确定",
          cancelButtonText: "取消",
          type: "warning"
        }).then(() => {
          let params = {
            id: row.id
          }
          console.log('params', params)
          allService.deleteDoctorById(params, (isOk, data) => {
            if (data.error_num === 0) {
              this.$message.success('删除成功')
              this.getAllUser()
            } else {
              this.$message.error(data.msg)
            }
          })
        })

      },
      resetpassword(index, row) {
        let params = {
          id: row.id
        }
        console.log('params', params)
        allService.resetDoctorPassword(params, (isOk, data) => {
          if (data.error_num === 0) {
            this.$message.success('重置成功')
            this.getAllUser()
          } else {
            this.$message.error(data.msg)
          }
        })
      }
    },
    mounted() {
      this.getAllUser()
    }
  }
</script>
