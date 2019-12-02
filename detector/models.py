from django.db import models

# Create your models here.
class CT(models.Model):
    patient_id = models.IntegerField("病人ID")
    ct_name = models.CharField("ct文件名", max_length=256, null=False)
    ct_path = models.CharField("ct文件路径", max_length=256, null=False)
    upload_time = models.DateTimeField("上传时间")

    def __unicode__(self):
        return self.ct_path