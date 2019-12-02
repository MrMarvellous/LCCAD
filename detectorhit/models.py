from django.db import models


# Create your models here.
class CT_info(models.Model):
    file_name = models.CharField("CT文件名(压缩)", max_length=256, null=False)
    upload_time = models.DateTimeField('CT文件上传时间')
    # patient_id = models.CharField('病人ID')
    doctor_id = models.IntegerField('医生ID', null=False, default=-1)
    patient_name = models.CharField('病人名', max_length=256)
    dirname = models.CharField('CT文件存储路径', max_length=256, null=True)
    has_detected = models.IntegerField('是否已经检查过', default=0)  # 0：未检查 1：已经检查
    has_intered = models.IntegerField('是否已经插值过', default=0)  # 0：未插值 1：已经插值

    is_pet = models.BooleanField("是否是PET图像", default=0)
    specify_id = models.CharField("specify_id",  max_length=256, null=True)

    def __unicode__(self):
        return str(self.file_name) + "-" + str(self.upload_time)
