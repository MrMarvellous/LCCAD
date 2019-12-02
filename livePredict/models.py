from django.db import models

# Create your models here.


# class pet_ct(models.Model):
#     patient_id = models.IntegerField("病人ID")
#     pet_path = models.CharField("pet ct路径",max_length=256)
#     location_id = models.CharField("location id",  max_length=256, null=True)
#     upload_time = models.DateTimeField("上传时间")
#
#     def __unicode__(self):
#         return self.pet_path


class pet_result(models.Model):

    pet_id = models.IntegerField("pet ct id")
    date = models.FloatField("date result")
    live = models.FloatField("live result")

    def __unicode__(self):
        return