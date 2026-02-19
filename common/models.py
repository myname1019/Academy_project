from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Student(models.Model):
  title = models.CharField(max_length=30)
  content = models.TextField()
  file_upload = models.FileField(upload_to='board/data/%Y/%m/%d/', blank=True)
  author = models.ForeignKey(User, on_delete=models.CASCADE)
  create_date = models.DateTimeField(auto_now_add=True)
  modify_date = models.DateTimeField(auto_now=True, null=True, blank=True)

  def __str__(self):
    return f'[PK:{self.pk}]-{self.title} :: {self.author}'


class Teacher(models.Model):
  title = models.CharField(max_length=30)
  content = models.TextField()
  file_upload = models.FileField(upload_to='board/data/%Y/%m/%d/', blank=True)
  author = models.ForeignKey(User, on_delete=models.CASCADE)
  create_date = models.DateTimeField(auto_now_add=True)
  modify_date = models.DateTimeField(auto_now=True, null=True, blank=True)

  def __str__(self):
    return f'[PK:{self.pk}]-{self.title} :: {self.author}'