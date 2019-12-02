<template>
  <el-row class="container">
    <el-col :span="24" class="header">
      <el-col :sapn="4" class="logo">{{ sysName}}</el-col>
      <el-col :span="4" class="back-button">
        <el-button
          type="success"
          icon="el-icon-arrow-left"
          @click="gotoDocIndex"
          v-if="showBackButton"
        >返回首页
        </el-button>
        <el-button
          type="success"
          icon="el-icon-arrow-left"
          @click="gotoDiaIndex"
          v-if="showDiaButton"
        >返回诊断
        </el-button>

      </el-col>

      <el-col :span="4" class="userinfo">
        <el-dropdown trigger="hover">
          <span class="el-dropdown-link userinfo-inner">
            <img src="../assets/logo.png">
            {{ sysUserName }}
          </span>
          <el-dropdown-menu slot="dropdown">
            <el-dropdown-item @click.native="gotoDocInfo">完善信息</el-dropdown-item>
            <el-dropdown-item divided @click.native="logout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </el-dropdown>
      </el-col>
    </el-col>
    <el-col :span="24" class="main">
      <section class="content-container">
        <div class="grid-content bg-purple-light">
          <el-col :span="24" class="content-wrapper">
            <transition name="fade" mode="out-in">
              <router-view @showButton="showButton" @showBackDiaButton="showBackDiaButton"
                           ></router-view>
            </transition>
          </el-col>
        </div>
      </section>
    </el-col>
  </el-row>
</template>

<script>
  export default {
    data() {
      return {
        sysName: "xxx hospital",
        sysUserName: "", //temp root name
        sysUserId: "",
        sysUserAvatar: "", //:src="this.sysUserAvatar"
        doctorId: "",
        userId: "",
        showBackButton: false,
        showDiaButton: false,
        viewType: '按CT',
        hidedropdown: false,
      };
    },
    methods: {
      gotoDocIndex() {
        this.$router.push({name: "docIndex"});
        this.showBackButton = false;
      },
      gotoDiaIndex() {
        this.$router.push({name: "diagIndex"});
        this.showDiaButton = false;
      },
      gotoDocInfo() {
        this.$router.push({name: "docInfo"});
      },
      showButton() {
        this.showBackButton = true;
      },
      showBackDiaButton() {
        this.showDiaButton = true;

      },
      //退出登录
      logout: function () {
        var _this = this;
        this.$confirm("确认退出吗?", "提示", {
          //type: 'warning'
        })
          .then(() => {
            sessionStorage.removeItem("user");
            sessionStorage.clear();
            _this.$router.push({name: "userLogin"});
          })
          .catch(() => {
          });
      }
    },
    mounted() {
      var user = sessionStorage.getItem("user");
      if (user) {
        user = JSON.parse(user);
        console.log("home user:");
        console.log(user);
        this.sysUserName = user.user.username || "";
        this.doctorId = user.id || "";
        this.userId = user.user.id || "";
      }
    },
    updated() {
      if (this.$route.path == "/doctor/index") {
        console.log("route is doctor index now");
        this.showBackButton = false;
      }
    }
  };
</script>


<style scoped lang="scss">
  .container {
    position: absolute;
    top: 0px;
    bottom: 0px;
    width: 100%;

    .header {
      height: 60px;
      position: fixed;
      line-height: 60px;
      background: #20a0ff;
      color: #fff;

      .userinfo {
        text-align: right;
        padding-right: 35px;
        float: right;

        .userinfo-inner {
          cursor: pointer;
          color: #fff;

          img {
            width: 40px;
            height: 40px;
            border-radius: 20px;
            margin: 10px 0px 10px 10px;
            float: right;
          }
        }
      }

      .logo {
        width: 230px;
        height: 60px;
        font-size: 22px;
        padding-left: 20px;
        padding-right: 20px;
        border-color: rgba(238, 241, 146, 0.3);
        border-right-width: 1px;
        border-right-style: solid;

        img {
          width: 40px;
          float: left;
          margin: 10px 10px 10px 18px;
        }

        .txt {
          color: #fff;
        }
      }

      .back-button {
        padding-left: 20px;
      }

      .logo-width {
        width: 230px;
      }

      .logo-collapse-width {
        width: 60px;
      }

      .tools {
        padding: 0px 23px;
        width: 14px;
        height: 60px;
        line-height: 60px;
        cursor: pointer;
      }
    }

    .main {
      display: flex;
      // background: #324057;
      position: absolute;
      top: 60px;
      bottom: 0px;
      overflow: hidden;

      .content-container {
        flex: 1;
        overflow-y: scroll;
        padding: 20px;

        .content-wrapper {
          background-color: #fff;
          box-sizing: border-box;
        }
      }
    }
  }
</style>
