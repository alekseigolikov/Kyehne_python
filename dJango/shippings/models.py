from django.db import models

# Create your models here.
class Shipping(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50, blank=False)
    origin = models.CharField(max_length=50, blank=False)
    destination = models.CharField(max_length=50, blank=False)
    current_location = models.CharField(max_length=50, blank=False)
    state = models.CharField(max_length=50, blank=False)
    
    class Meta:
        ordering = ('creation_date','name')
