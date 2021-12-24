from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import User


# class Profile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     image = models.TextField()
#
#     def __str__(self):
#         return self.user.username


class GraphData(models.Model):
    type = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    data = models.TextField()


class File(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    published_date = models.DateTimeField(blank=True, null=True)
    path = models.TextField()
    # path = models.CharField(max_length=255)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.name
    # file = models.FileField(upload_to=f'{id}/', validators=[FileExtensionValidator(['xlsx', 'csv'])])

class DataModel(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    path = models.TextField(default="empty")

