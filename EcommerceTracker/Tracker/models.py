from django.db import models

# Create your models here.
class TrackData(models.Model):
    Id = models.AutoField(primary_key=True)
    Name_Url = models.CharField(max_length=50)
    Title = models.CharField(max_length=500)
    Item_Url = models.URLField(max_length=1000)
    Item_Price = models.CharField(max_length=50)
    Item_Image_url = models.URLField()
    Expected_Price = models.CharField(max_length=50)
    Email = models.EmailField()
    last_updated = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.Title
