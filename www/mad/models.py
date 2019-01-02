from django.db import models


# Create your models here.
class Mad_Report(models.Model):
    name = models.CharField(max_length=255)
    is_malicious = models.BooleanField()
    ua = models.TextField()
    url = models.TextField()
    srcip = models.CharField(max_length=255)
    srcport = models.IntegerField()
    dstip = models.CharField(max_length=255)
    dstport = models.IntegerField()
    time = models.DateTimeField()
    detected_by_cnn = models.BooleanField()
    device = models.CharField(max_length=255)
    os = models.CharField(max_length=255)
    browser = models.CharField(max_length=255)
    type = models.CharField(max_length=255)

    class Meta:
        db_table = 'mad_report'


class Mad_Loss(models.Model):
    time = models.DateTimeField()
    loss = models.FloatField()

    class Meta:
        db_table = 'mad_loss'


class Mad_ProcessedFile(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'mad_processedfile'
