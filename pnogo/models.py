from django.db import models


class Cndr(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = "cndr"

    def __str__(self):
        return self.name


class Picture(models.Model):
    file = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    points = models.IntegerField(default=0)
    sent = models.IntegerField(default=0)
    daily_date = models.DateField(null=True, blank=True)
    cndr = models.ForeignKey(Cndr, on_delete=models.PROTECT, related_name="pictures")

    class Meta:
        db_table = "pictures"

    def __str__(self):
        return f"#{self.pk} — {self.file}"
