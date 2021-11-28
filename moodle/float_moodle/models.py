import django
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils import timezone
from datetime import date, datetime, time
# Create your models here.

ta_choices = [('1','one'),('2','two')]

class createdcourses(models.Model):
  	user = models.ForeignKey(User, on_delete = models.CASCADE)
  	name = models.CharField(max_length = 50)
  	coursecode = models.CharField(max_length = 5,validators = [RegexValidator(regex='^\w{5}$', message='Length has to be 5')])
  	def __str__(self):
  		return self.name

class undertakingcourses(models.Model):
	user = models.ForeignKey(User, on_delete = models.CASCADE)
	name = models.CharField(max_length = 50)
	coursecode = models.CharField(max_length = 5)
	def __str__(self):
		return self.name

class assignment(models.Model):
   course = models.ForeignKey(createdcourses, on_delete = models.CASCADE)
   file = models.FileField(upload_to ='documents/', null=True)
   title = models.CharField(max_length = 50)
   description = models.TextField(max_length = 150)
   maxmarks = models.PositiveIntegerField()
   end_date=models.DateField(auto_now_add=False,default=date.today)
   end_time = models.TimeField(auto_now_add=False)
   is_deadline_not_over=models.BooleanField(max_length=10,default=True)
   marksfile = models.FileField(upload_to ='csvfile/', null=True, blank=True)
   weightage = models.PositiveIntegerField()

   def is_end_date(self):
      return timezone.localdate()<=self.end_date

   def is_today(self):
      return timezone.localdate()==self.end_date

   def is_time(self):
      return timezone.localtime().time() < self.end_time

   def __str__(self):
  		return self.title

class submit_assignment(models.Model): 
   assignment = models.ForeignKey(assignment, on_delete = models.CASCADE)
   student = models.ForeignKey(User, on_delete=models.CASCADE)
   file = models.FileField(upload_to ='submissions/', null=True)
   status = models.CharField(max_length=100,default = "Not Evaluated")
   feedback = models.TextField(null = True, blank = True)
   obtainedmarks = models.IntegerField(null=True, default=0)
   def __str__(self):
  		return self.student.username

class announcements(models.Model):
   course = models.ForeignKey(createdcourses, on_delete = models.CASCADE)
   title = models.CharField(max_length = 50)
   announcement  = models.TextField(max_length = 150)
   def __str__(self):
       return self.title

class moderatorrelated(models.Model):
   course = models.OneToOneField(createdcourses,on_delete=models.CASCADE)
   tacode = models.CharField(max_length = 5,validators = [RegexValidator(regex='^\w{5}$', message='Length has to be 5')])
   power = models.CharField(max_length=3, choices=ta_choices)
   def __str__(self):
       return self.course.name

class moderator(models.Model):
   user = models.ForeignKey(User, on_delete = models.CASCADE)
   name = models.CharField(max_length = 50)
   coursecode = models.CharField(max_length = 5)
   tacode = models.CharField(max_length = 5)
   def __str__(self):
       return self.name