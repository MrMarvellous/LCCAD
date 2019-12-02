from django.conf.urls import url, include

from doctorModule import views

urlpatterns = [
    url(r'^admin/getAllDoctor/$', views.get_all_doctor, name='ADMgetAllDoctor'),
    url(r'^admin/addDoctor/$', views.add_doctor_by_admin, name='ADMaddDoctor'),
    url(r'^admin/getDoctorByName/$', views.get_doctor_by_name, name='ADMgetDoctorByName'),
    url(r'^admin/deleteDoctor/$', views.delete_doctor_by_admin, name='ADMdeleteDoctor'),
    url(r'^admin/resetDocPW/$', views.reset_doctor_password, name='ADMresetDocPW'),


    url(r'^user/register/$', views.register, name='register'),
    url(r'^user/login/$', views.login, name='login'),
    url(r'^doctor/addPatient/$', views.add_patient, name='addPatient'),
    url(r'^doctor/getPatientByDocId/$', views.query_patient_by_docId, name='getPatientByDocId'),
    url(r'^doctor/updatePatientInfo/$', views.update_patient_info, name='updatePatientInfo'),
    url(r'^doctor/getPatientByName/$', views.query_patient_by_patientName, name='getPatientByName'),
    url(r'^doctor/checkDoctorInfo/$', views.check_doctor_info, name='checkDoctorInfo'),
    url(r'^doctor/checkDoctorInfo/$', views.check_doctor_info, name='checkDoctorInfo'),
    url(r'^doctor/updateDoctorInfo/$', views.update_doctor_info, name='updateDoctorInfo'),
    url(r'^doctor/getDoctorInfo/$', views.query_doctor_by_id, name='getDoctorInfo'),
    url(r'^doctor/generateReport/$', views.generateReport, name='generateReport'),
    url(r'^doctor/addDiagInfo/$', views.add_diag_info, name='addDiagInfo'),
    url(r'^doctor/delDiagInfo/$', views.del_diag_info, name='delDiagInfo'),
    url(r'^doctor/updateDiagInfo/$', views.update_diag_info, name='updateDiagInfo'),
    url(r'^doctor/getSinglePatientDiag/$', views.get_diag_info, name='getSinglePatientDiag'),
    url(r'^doctor/getDocDiagList/$', views.get_doc_diag_list, name='getDocDiagList'),

]