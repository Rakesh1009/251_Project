"""moodle URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView
from django.conf.urls import url
from float_moodle import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', views.signup, name='signup'),
    path('password/', views.passwordchange.as_view(template_name = 'registration/change-password.html'), name = 'change_password'),
    path('editprofile/', views.editprofile, name = 'editprofile'),
    path('', views.home, name='home'),
    path('upload/<str:pk>/',views.uploadass,name = 'uploadassignment'),
    path('assignment/<str:pk>/<str:ak>/',views.viewass, name = 'viewassignment'),
    path('createcourse/',views.createcourse, name = 'createcourse'),
    path('joincourse/',views.joincourse, name = 'joincourse'),
    path('asinstructor/', views.coursesasinstructor, name='coursesasinstructor'),
    path('coursesundertaken/', views.coursesundertaken, name='coursesundertaken'),
    path('instructor/<str:pk>/',views.instructor,name='instructor'),
    path('student/<str:pk>/',views.student,name='student'),
    path('viewsubmissions/<str:pk>/<str:ak>/',views.viewsubmissions,name="viewsubmissions"),
    path('feedback/<str:pk>/<str:ak>/<str:sk>/',views.feedback,name="feedback"),
    path('postannouncement/<str:pk>/',views.postannouncement,name = 'postannouncement'),
    path('allannouncements/<str:pk>/',views.allannouncements,name='allannouncements'),
    path('joincourseasta/',views.joinasta, name = 'joinasta'),
    path('coursesasta/', views.coursesasta, name='coursesasta'),
    path('instructor/<str:pk>/createtas',views.createtas,name='createtas'),
    path('moderator/<str:pk>/',views.ta,name='moderator'),
    path('instructor/<str:pk>/<str:ak>/', views.uploadmarks, name = 'uploadmarks'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
