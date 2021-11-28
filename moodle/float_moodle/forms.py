from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms.widgets import TimeInput
from .models import *

class DateInput(forms.DateInput):
    input_type = 'date'
    
class TimeInput(forms.TimeInput):
    input_type = 'time'

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2','first_name', 'last_name', 'email')

class UpdateUserForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class coursecreateform(forms.ModelForm):
    class Meta:
        model = createdcourses
        fields = ('name','coursecode')

class coursejoinform(forms.ModelForm):
    class Meta:
        model = undertakingcourses
        fields = ('name', 'coursecode')

class assignmentuploadform(forms.ModelForm):
    class Meta:
        model = assignment
        fields = ('file', 'description', 'title','weightage','maxmarks','end_date','end_time')
        widgets={'end_date': DateInput(),'end_time': TimeInput()}
        # fields = ('file','description',)

class submissionform(forms.ModelForm):
    class Meta:
        model=submit_assignment
        fields=('file',)

class feedbackform(forms.ModelForm):
    class Meta:
        model= submit_assignment
        fields=('feedback','obtainedmarks')
        
class marksuploadform(forms.ModelForm):
    class Meta:
        model = assignment
        fields = ('marksfile',)

class postannouncementform(forms.ModelForm):
    class Meta:
        model = announcements
        fields = ('announcement','title',)

class addtasform(forms.ModelForm):
    class Meta:
        model = moderatorrelated
        fields = ('power','tacode',)

class joinasmoderator(forms.ModelForm):
    class Meta:
        model = moderator
        fields = ('name','coursecode','tacode',)