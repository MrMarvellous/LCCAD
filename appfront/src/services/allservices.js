export default class AllService {
  constructor() {
    this.host = process.env.testHost
    this.fileHost = process.env.fileHost
    this.method = {
      adminGetAllDoctor: '/accounts/admin/getAllDoctor/',
      adminAddDoctor: '/accounts/admin/addDoctor/',
      getDoctorByName: '/accounts/admin/getDoctorByName/',
      deleteDoctorById: '/accounts/admin/deleteDoctor/',
      resetDoctorPassword: '/accounts/admin/resetDocPW/',

      signIn: '/accounts/user/login/',
      signUp: '/accounts/user/register/',

      addPatient: '/accounts/doctor/addPatient/',
      getPatientByDocId: '/accounts/doctor/getPatientByDocId/',
      updatePatientInfo: '/accounts/doctor/updatePatientInfo/',
      getPatientByName: '/accounts/doctor/getPatientByName/',
      checkDoctorInfo: '/accounts/doctor/checkDoctorInfo/',
      resetInformDate: '/accounts/doctor/resetInformDate/',
      updateDoctorInfo: '/accounts/doctor/updateDoctorInfo/',
      getDoctorInfo: '/accounts/doctor/getDoctorInfo/',
      generateReport: '/accounts/doctor/generateReport/',
      addDiagInfo: '/accounts/doctor/addDiagInfo/',
      delDiagInfo: '/accounts/doctor/delDiagInfo/',
      updateDiagInfo: '/accounts/doctor/updateDiagInfo/',
      getDocDiagList: '/accounts/doctor/getDocDiagList/',
      getSinglePatientDiag: '/accounts/doctor/getSinglePatientDiag/',

      // addCTInfo: '/detect/addCTInfo/',
      // deleteCTInfo: '/detect/deleteCTInfo/',
      // getCTByPatient: '/detect/getCTByPatient/',
      // startDetect: '/detect/detectPatientNodule/',
      // getAllImage: '/detect/image/getAllImage/',
      // getAIPredict: '/detect/image/getAIPredict/',
      // getImageByIndexList: '/detect/image/getImageByIndexList/',

      uploadCT: '/detecthit/uplaodCT/', //no need to use; see /Doctor/index.vue; used in el-upload::action
      extractCT: '/detecthit/extractCT/',
      getCTInfoList: '/detecthit/getCTList/',
      predictCT: '/detecthit/predCT/',
      getOriginImg: '/detecthit/getOriginImg/',
      getResultImg: '/detecthit/getResultImg/',

      coverCT: '/tracer/cover/',
      getCoverResultById: '/tracer/getCoverResultById/',

      interpolateCT: '/interpolation/interpolate/',
      getInterpolationImage: '/interpolation/getInterImgs/',
      queryInterStatus: '/interpolation/queryInterStatus/',

      predictPET: '/livePredict/predictPET/',
      uploadPET: '/livePredict/uploadPET/', //not used anymore
      extractPET: '/livePredict/extractPET/',
      getPETResultByPID: '/livePredict/getPETResultByPID/',


    }
  }

  ajaxRequest(url, sendData, type, callback, contentType) {
    var result
    $.ajax({
      url: url,
      type: type || 'GET',
      async : true,
      contentType: contentType === undefined ? 'application/x-www-form-urlencoded' : contentType,
      data: contentType == 'application/json' ? JSON.stringify(sendData) : sendData,
      timeout: 60000,
      complete: function () {
      },
      success: function (data, textStatus) {
        try {
          if (callback) {
            callback(null, data)
          }
          result = data
        } catch (e) {
          console.log(e)
        }
      },
      error: function (XMLHttpRequest, textStatus, errorThrown) {
        try {
          if (callback) {
            callback(textStatus || new Error("net error"), XMLHttpRequest)
          }
        } catch (e) {
          console.log(e)
        }
      }
    })
    return result
  }

  bizRequest(url, sendData, type, callback, contentType) {
    var result = null
    this.ajaxRequest(url, sendData, type, function (err, data) {
      if (!err) {
        if (data && contentType === 'application/json') {
          //成功，更新token
          if (data.error_num !== null || data.status === '200') {
            result = data
            data.status = true
          }
          if (data.error_num === null || data.status !== '200') {
            console.log(data && data.msg ? data.msg : "net no data")
          }
          if (callback) {
            callback(data.status, data)
          }
        }else if(data && contentType === 'image/jpeg'){
          callback(true, {data: data})
        } else {
          if (callback) {
            callback(false, {message: '服务器好像出现了点问题'})
          }
        }
      } else {
        console.log(data)
        console.log('bizRequest error : ' + err)
      }
    }, contentType)
    return result
  }
  adminGetAllDoctor(params, callback) {
    var url = this.host + this.method.adminGetAllDoctor;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }

  adminAddDoctor(params, callback) {
    var url = this.host + this.method.adminAddDoctor;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }
  getDoctorByName(params, callback) {
    var url = this.host + this.method.getDoctorByName;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }

  deleteDoctorById(params, callback) {
    var url = this.host + this.method.deleteDoctorById;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }
  resetDoctorPassword(params, callback) {
    var url = this.host + this.method.resetDoctorPassword;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }


  signIn(params, callback) {
    var url = this.host + this.method.signIn;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }

  signUp(params, callback) {
    var url = this.host + this.method.signUp;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }

  addPatient(params, callback) {
    var url = this.host + this.method.addPatient;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }

  getPatientByDocId(params, callback) {
    var url = this.host + this.method.getPatientByDocId;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }

  updatePatientInfo(params, callback) {
    var url = this.host + this.method.updatePatientInfo;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }
  getPatientByName(params, callback) {
    var url = this.host + this.method.getPatientByName;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }

  checkDoctorInfo(params, callback) {
    var url = this.host + this.method.checkDoctorInfo;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }

  resetInformDate(params, callback){
    var url = this.host + this.method.resetInformDate;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }
  updateDoctorInfo(params, callback){
    var url = this.host + this.method.updateDoctorInfo;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }
  getDoctorInfo(params, callback){
    var url = this.host + this.method.getDoctorInfo;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }
  addCTInfo(params, callback) {
    var url = this.host + this.method.addCTInfo;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }
  deleteCTInfo(params, callback) {
    var url = this.host + this.method.deleteCTInfo;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }
  getCTByPatient(params, callback) {
    var url = this.host + this.method.getCTByPatient;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }
  getAllImage(params, callback) {
    var url = this.host + this.method.getAllImage;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }
  getAIPredict(params, callback) {
    var url = this.host + this.method.getAIPredict;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }
  startDetect(params, callback) {
    var url = this.host + this.method.startDetect;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }
  generateReport(params, callback) {
    var url = this.host + this.method.generateReport;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }
  getImageByIndexList(params, callback) {
    var url = this.host + this.method.getImageByIndexList;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }
  addDiagInfo(params, callback) {
    var url = this.host + this.method.addDiagInfo;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }
  delDiagInfo(params, callback) {
    var url = this.host + this.method.delDiagInfo;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }
  updateDiagInfo(params, callback) {
    var url = this.host + this.method.updateDiagInfo;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }
  getDocDiagList(params, callback) {
    var url = this.host + this.method.getDocDiagList;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }
  getSinglePatientDiag(params, callback) {
    var url = this.host + this.method.getSinglePatientDiag;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }
  uploadCT(params, callback) {
    var url = this.host + this.method.uploadCT;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }
  extractCT(params, callback) {
    var url = this.host + this.method.extractCT;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }
  getCTInfoList(params, callback) {
    var url = this.host + this.method.getCTInfoList;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }
  predictCT(params, callback) {
    var url = this.host + this.method.predictCT;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }
  getOriginImg(params, callback) {
    var url = this.host + this.method.getOriginImg;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }
  getResultImg(params, callback) {
    var url = this.host + this.method.getResultImg;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }
  coverCT(params, callback) {
    var url = this.host + this.method.coverCT;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }
  getCoverResultById(params, callback) {
    var url = this.host + this.method.getCoverResultById;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }
  interpolateCT(params, callback) {
    var url = this.host + this.method.interpolateCT;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }
  getInterpolationImage(params, callback) {
    var url = this.host + this.method.getInterpolationImage;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }
  queryInterStatus(params, callback) {
    var url = this.host + this.method.queryInterStatus;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }

  predictPET(params, callback) {
    var url = this.host + this.method.predictPET;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }
  uploadPET(params, callback) {
    var url = this.host + this.method.uploadPET;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }
  extractPET(params, callback) {
    var url = this.host + this.method.extractPET;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }
  getPETResultByPID(params, callback) {
    var url = this.host + this.method.getPETResultByPID;
    var type = 'post';
    return this.bizRequest(url, params, type, function (isOk, data) {
      if (callback) {
        callback(isOk, data);
      }
    }, "application/json");
  }
}
