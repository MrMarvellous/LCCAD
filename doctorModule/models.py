from django.db import models
from django.contrib.auth.models import User


# Create your models here.
from django.utils import timezone
import datetime


class Doctor(models.Model):
    SEX_TYPE = (
        (1, "男"),
        (2, "女"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')  # 继承django 自带User类
    doc_name = models.CharField("医生姓名", max_length=64,null=True)
    doc_birth = models.DateField("医生生日",null=True)
    doc_sex = models.IntegerField("医生性别", choices=SEX_TYPE,null=True)
    doc_depart = models.CharField("医生部门", max_length=64,null=True)
    doc_hospital = models.CharField("所属医院", max_length=64,null=True)
    doc_tel = models.CharField("联系电话", max_length=32,null=True)
    doc_description = models.CharField("个人简介", max_length=256,null=True)
    inform_time = models.DateField("提醒时间", default=timezone.now)
    is_admin = models.BooleanField("是管理员", default=False)

    def __unicode__(self):
        return self.user.username


class Diagnosis(models.Model):
    doc_id = models.IntegerField("医生ID")
    patient_id = models.IntegerField("病人ID")
    patient_symptom = models.CharField("患者症状", max_length=256, null=True)
    CTURL = models.CharField("CT图像地址", max_length=256, null=True)
    AIResult = models.CharField("算法诊断图像地址", max_length=256, null=True)
    DiagResult = models.CharField("医生诊断结果", max_length=256, null=True)
    DiagTime = models.DateTimeField("医生诊断时间")
    DiagRemark = models.CharField("诊断的图片列表", max_length=256, null=True)

    def __unicode__(self):
        return str(self.doc_id)+"-"+str(self.patient_id)


class Patient(models.Model):
    SEX_TYPE = (
        (1, "男"),
        (2, "女"),
    )

    # user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')  # 继承django 自带User类
    patient_name = models.CharField("病人姓名", max_length=64)
    patient_doc = models.IntegerField(verbose_name="主治医师ID")
    patient_birth = models.DateField("病人生日", default="1970-01-01")
    patient_sex = models.IntegerField("病人性别", choices=SEX_TYPE)
    # patient_symptom = models.CharField("症状", max_length=256,null=True)
    patient_past_history = models.CharField("以往病史", max_length=256, null=True)
    patient_tel = models.CharField("联系电话", max_length=32, null=True)
    patient_address = models.CharField("病人住址", max_length=256, null=True)
    patient_remark = models.CharField("病人备注", max_length=256, null=True)
    patient_add_time = models.DateTimeField("添加病人时间",null=True)

    def __unicode__(self):
        return self.patient_name




