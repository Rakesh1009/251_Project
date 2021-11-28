from django.contrib.auth.views import PasswordChangeView
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from float_moodle.forms import *
from moodle.settings import EMAIL_HOST_USER
from .models import *
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.views.generic.base import TemplateView
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
import statistics
from matplotlib import pyplot as plt
import io,urllib,base64
# Create your views here.
def signup(request):
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			user = form.save()
			user.save()
			return redirect('/accounts/login')
	else:
		form = SignUpForm()
	return render(request, 'signup.html', {'form': form})

class passwordchange(PasswordChangeView):
	form_class = PasswordChangeForm
	success_url = reverse_lazy('home')

@login_required
def editprofile(request):
    if request.method == 'POST':
        form = UpdateUserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = UpdateUserForm(instance=request.user)
    return render(request, 'editprofile.html', {'user_form': form})

@login_required
def createcourse(request):
	email=request.user.email
	if request.method == "POST":
		form = coursecreateform(request.POST, instance = request.user)
		if form.is_valid():
			cur_user = request.user
			name = request.POST.get('name')
			code = request.POST.get('coursecode')
			if len(code) != 5 :
				return HttpResponse('Coursecode should be of length 5')
			allcourses = createdcourses.objects.all()
			for course in allcourses:
				if course.name == name:
					return HttpResponse('Course with same name already exists')
			course = createdcourses(user = cur_user,name = name,coursecode = code)
			course.save()
			send_mail('Created '+name,'You have created the course '+name+' whose course-code is "'+code+'"',EMAIL_HOST_USER,[email])
			return redirect('home')
	form = coursecreateform(instance=request.user)
	return render(request, 'createcourse.html', {'form':form})

@login_required
def joincourse(request):
	email=request.user.email
	if request.method == "POST":
		form = coursejoinform(request.POST, instance = request.user)
		if form.is_valid():
			name = request.POST.get('name')
			code = request.POST.get('coursecode')
			creator = createdcourses.objects.get(name = name)
			cur_user = request.user
			send_mail('Enrolled in '+name,'You have enrolled for the course '+name,EMAIL_HOST_USER,[email])
			if cur_user == creator.user:
				return HttpResponse('You are instructor for this Course')
			if code == creator.coursecode :
				student = undertakingcourses(user = cur_user,coursecode = code, name = name)
				student.save()
				return redirect('home')
	form = coursejoinform(instance=request.user)
	return render(request, 'coursejoin.html', {'form':form})

@login_required
def coursesasinstructor(request):
	courses = createdcourses.objects.filter(user = request.user)
	return render(request,'createdcourses.html',{'courses':courses})

@login_required
def coursesundertaken(request):
	courses = undertakingcourses.objects.filter(user = request.user)
	return render(request,'undertakencourses.html',{'courses':courses})

@login_required
def coursesasta(request):
    courses = moderator.objects.filter(user = request.user)
    return render(request,'coursesasta.html',{'courses':courses})

@login_required
def instructor(request,pk):
    name=pk
    course=createdcourses.objects.filter(name=name)
    assignments = assignment.objects.filter(course=course[0])
    assavglist = []
    for ass in assignments:
        submissions = submit_assignment.objects.filter(assignment=ass)
        marks = 0
        subcount=0
        for submission in submissions:
            if submission.status == "Graded":
                marks += (submission.obtainedmarks/ass.maxmarks)*(ass.weightage)
                subcount += 1
        if subcount==0:
            subcount=1
        assavglist += [marks/subcount]
    total = sum(assavglist)
    return render(request,'instructor.html',{'assignments':assignments,'name':name,'classavg':total})

@login_required
def student(request,pk):
    name = pk
    course = undertakingcourses.objects.filter(name=name)
    course = createdcourses.objects.filter(name=course[0])
    assignments = assignment.objects.filter(course=course[0])
    coursetotal = 0
    percentcompleted = 0
    if assignments.exists():
        for ass in assignments:
            submissions = submit_assignment.objects.filter(assignment=ass)
            for submission in submissions:
                if submission.student.username == request.user.username:
                    percentcompleted += ass.weightage
                    if submission.status == "Graded":
                        coursetotal += (submission.obtainedmarks/ass.maxmarks)*(ass.weightage)
    else:
        pass
    return render(request,'student.html',{'assignments': assignments,'pk':pk, 'coursetotal':coursetotal,'percentcompleted':percentcompleted})
	
@login_required
def ta(request,pk):
    name=pk
    course=createdcourses.objects.filter(name=name)
    tapower = course[0].moderatorrelated.power
    assignments = assignment.objects.filter(course=course[0])
    return render(request,'moderator.html',{'assignments':assignments,'name':name,'power':tapower})

@login_required
def createtas(request,pk):
    name=pk
    course = createdcourses.objects.filter(name=name)
    course = course[0]
    if request.method == "POST":
        form = addtasform(request.POST)
        if form.is_valid():
            power = request.POST.get('power')
            tacode = request.POST.get('tacode')
            parameters = moderatorrelated(course=course,power=power,tacode=tacode)
            parameters.save()
            return redirect('instructor',pk)
        else:
            form = addtasform(instance=request.user)
    else:
        form = addtasform()
    return render(request,'addta.html',{'form':form,'course':course})

@login_required
def joinasta(request):
    if request.method == "POST":
        form = joinasmoderator(request.POST, instance = request.user)
        if form.is_valid():
            name = request.POST.get('name')
            code = request.POST.get('coursecode')
            tacode = request.POST.get('tacode')
            creator = createdcourses.objects.get(name = name)
            cur_user = request.user
            if cur_user == creator.user:
                return HttpResponse('You are creator for this Course')
            if code == creator.coursecode and tacode == creator.moderatorrelated.tacode:
                ta = moderator(user = cur_user,coursecode = code, name = name,tacode=tacode)
                ta.save()
                return redirect('home')
    form = joinasmoderator(instance=request.user)
    return render(request, 'tajoin.html', {'form':form})

@login_required
def uploadass(request, pk):
	course = createdcourses.objects.filter(name=pk)
	course = course[0]
	if request.method == "POST":
		form = assignmentuploadform(request.POST, request.FILES)
		if form.is_valid():
			title = request.POST.get('title')
			file=request.FILES.get('file')
			description=request.POST.get('description')
			weightage = request.POST.get('weightage')
			maxmarks=request.POST.get('maxmarks')
			end_date=request.POST.get('end_date')
			end_time=request.POST.get('end_time')
			ass = assignment(course=course,title=title,file=file,description=description,maxmarks = maxmarks,end_date=end_date,end_time=end_time,weightage=weightage)
			email=request.user.email
			send_mail('Assignment posted','Your assignment in course:'+title+' has been posted which is due '+end_date+' at '+ end_time ,EMAIL_HOST_USER,[email])
			ass.save()
			return redirect('instructor',pk)
		else:
        		form = assignmentuploadform(instance=request.user)
	else:
		form = assignmentuploadform()
	return render(request, 'assignmentupload.html', {'form':form, 'course':course})

@login_required
def postannouncement(request,pk):
    course = createdcourses.objects.filter(name=pk)
    course = course[0]
    if request.method == "POST":
        form = postannouncementform(request.POST)
        if form.is_valid():
            title = request.POST.get('title')
            announcement=request.POST.get('announcement')
            announced = announcements(course=course,title= title,announcement=announcement)
            announced.save()
            return redirect('instructor',pk)
        else:
            form = postannouncementform(instance=request.user)
    else:
        form = postannouncementform()
    return render(request, 'postannouncement.html', {'form':form, 'course':course})

@login_required
def allannouncements(request,pk):
    course = createdcourses.objects.filter(name=pk)
    course = course[0]
    announcementsmade = announcements.objects.filter(course=course)
    return render(request,'announcementstillnow.html',{'name':course,'allannouncements':announcementsmade})
	
@login_required
def viewass(request,pk,ak):
	course=createdcourses.objects.filter(name=pk)
	course=course[0]
	ass=assignment.objects.filter(course=course,title=ak)
	ass=ass[0]
	submissions=submit_assignment.objects.filter(assignment=ass)
	submitted=0
	email=request.user.email
	for submission in submissions:
		if submission.student.username == request.user.username:
			submitted=True
			mysubmission=submission
	if submitted:
		return render(request,'viewsubass.html',{'assignment':ass,'mysubmission':mysubmission})
	else:
		if request.method=="POST":
			send_mail('Assignment submitted','Your submission for this assignment has been recorded.',EMAIL_HOST_USER,[email])
			submittedfile=request.FILES.get('file')
			submission=submit_assignment(assignment=ass,student=request.user,file=submittedfile)
			submission.save()
			return render(request,'viewsubass.html',{'assignment':ass,'mysubmission':submission})
		form=submissionform(instance=request.user)
		return render(request,'viewass.html',{'assignment':ass,'form':form})	

@login_required
def viewsubmissions(request,pk,ak):
    course = createdcourses.objects.filter(name=pk)
    course = course[0]
    ass = assignment.objects.filter(course=course,title=ak)
    ass = ass[0]
    submissions = submit_assignment.objects.filter(assignment = ass)
    marks = []
    mean = 0
    variance = 0
    for submission in submissions:
        if submission.status == "Graded":
            marks += [submission.obtainedmarks]
    if len(marks) == 0:
        mean = 0
        variance = 0
    elif len(marks)==1:
        mean=marks[0]
        variance=0
        plt.hist(marks)
        fig = plt.gcf()
        buf = io.BytesIO()
        fig.savefig(buf,format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri =  urllib.parse.quote(string)
        return render(request,'viewsubmissions.html',{'submissions':submissions,'pk':course.name,'ak':ass.title, 'mean':mean,
        'variance':variance,'data':uri})
    else:
        mean = statistics.mean(marks)
        variance = statistics.variance(marks,xbar=mean)
        plt.hist(marks)
        fig = plt.gcf()
        buf = io.BytesIO()
        fig.savefig(buf,format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri =  urllib.parse.quote(string)
        return render(request,'viewsubmissions.html',{'submissions':submissions,'pk':course.name,'ak':ass.title, 'mean':mean,'variance':variance,'data':uri})
    return render(request,'viewsubmissions.html',{'submissions':submissions,'pk':course.name,'ak':ass.title, 'mean':mean,'variance':variance})

@login_required
def feedback(request, pk, ak, sk):
	course=createdcourses.objects.filter(name=pk)
	course=course[0]
	ass = assignment.objects.filter(course=course,title=ak)
	student = User.objects.filter(username=sk)
	student_id=User.objects.get(username=sk)
	sass = submit_assignment.objects.get(assignment=ass[0],student=student[0])
	email=student_id.email
	if request.method=="POST":
		feedback=request.POST.get('feedback')
		obtainedmarks = request.POST.get('obtainedmarks')
		sass.obtainedmarks = obtainedmarks
		sass.feedback=feedback
		sass.status="Graded"
		sass.save()
		send_mail('Assignment Graded','Your submission for this assignment has been graded by '+request.user.username,EMAIL_HOST_USER,[email])
		redirectpath='http://127.0.0.1:8000/viewsubmissions/'+pk+'/'+ak+'/'
		return redirect(redirectpath)
	form=feedbackform()
	return render(request,'feedback.html', {'form':form})

@login_required
def home(request):
	user_courses = undertakingcourses.objects.filter(user = request.user)
	assign_list=assignment.objects.none()
	for courses in user_courses:
		name=courses.name
		course=createdcourses.objects.filter(name=name)
		course=course[0]
		ass=assignment.objects.filter(course=course)
		for assign in ass:
			if assign.is_end_date():
				if assign.is_today():
					if assign.is_time():
						assign.is_deadline_not_over=True
						assign.save()
					else:
						assign.is_deadline_not_over=False
						assign.save()
				else:
					assign.is_deadline_not_over=True
					assign.save()
			else:
				assign.is_deadline_not_over=False
				assign.save()
		assign_list=assignment.objects.filter(course=course,is_deadline_not_over=True)

	return render(request,'home.html',{'assign_list':assign_list} )

@login_required
def uploadmarks(request, pk, ak):
    course = createdcourses.objects.filter(name=pk)
    course = course[0]
    ass = assignment.objects.filter(course=course,title=ak)
    ass = ass[0]
    if request.method =="POST":
        form = marksuploadform(request.POST, request.FILES)
        if form.is_valid():
            csvfile = request.FILES.get('marksfile')
            data = request.FILES['marksfile'].read()
            data = data.decode()
            if "\r\n" in data:
                datalist = data.split("\r\n")
            elif "\r\n" and "\n" not in data:
                pass
            else:
                datalist = data.split("\n")
            ass.marksfile = csvfile
            for datarow in datalist:
                row = datarow.split(",")
                student = User.objects.filter(username=row[0])
                sass = submit_assignment.objects.get(assignment=ass,student=student[0])
                sass.obtainedmarks = row[1]
                sass.feedback =  row[2]
                sass.status="Graded"
                sass.save()
            ass.save()
            redirectpath='http://127.0.0.1:8000/instructor/%27+pk+%27/'
            return redirect(redirectpath)
        else:
            form = marksuploadform(instance=request.user)
            return render(request, 'uploadmarksfile.html',{'ass':ass,'form':form})
    form = marksuploadform(instance=request.user)
    return render(request, 'uploadmarksfile.html',{'ass':ass,'form':form})