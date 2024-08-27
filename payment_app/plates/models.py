from django.db import models

class Plate(models.Model):
    plate_code = models.CharField(max_length=10, unique=True)
    arrived_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.plate_code


class PlatePaid(models.Model):
    plate_code = models.CharField(max_length=10)
    arrived_at = models.DateTimeField()
    paid_at = models.DateTimeField(auto_now_add=True)
    cost = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.plate.plate_code