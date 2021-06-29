from django.conf import settings
from datetime import timedelta
from typing import ContextManager
from django.db.models import fields
from django.db.models.query import QuerySet
from django.http import response,HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views import generic
from django.contrib import auth
from .models import *
from .forms import *


import bcrypt
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage, message
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes,force_text
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages

import json

from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
# Create your views here.






def only_admin(request,option):
    if request.user.is_staff:

        if option == 'all':
            new_students = Student.objects.filter(deposit = '1')
            students = Student.objects.all().exclude(deposit= '1')
            return render(request,'study/admin.html',{'students':students, 'new_students':new_students})

        if option == 'today':
            new_students = Student.objects.filter(day1 = datetime.date.today())
            students = Student.objects.filter(day2 = datetime.date.today())
            students = students | Student.objects.filter(day3 = datetime.date.today())
            students = students | Student.objects.filter(day4 = datetime.date.today())
            students = students | Student.objects.filter(plus_day = datetime.date.today())
            return render(request,'study/admin.html',{'new_students': new_students,'students':students})
            

        if option == 'name':
            if request.method == 'POST' :
                students = Student.objects.filter(name = request.POST['name'])
                return render(request,'study/admin.html',{'students':students})

        if option == 'number':
            if request.method == 'POST' :
                students = Student.objects.filter(number = request.POST['number'])
                return render(request,'study/admin.html',{'students':students})
        if option == 'new':
            new_students = Student.objects.filter(day1 = datetime.date.today())
            return render(request,'study/admin.html',{'new_students':new_students})
    else:
        return redirect('index')


def check_deposit(request,option,user_id,way):
    if request.user.is_staff:
        student = Student.objects.get(pk = user_id)
        student.deposit = option
        student.pay_way = way
        student.save()
        return redirect('deposit_view','all')
    else:
        return redirect('index')

def deposit_view(request,option):
    if request.user.is_staff:
        if option == 'name':
            if request.method == 'POST':
                students = Student.objects.filter(name = request.POST['name'])
                return render(request,'study/depositview.html',{"students" : students})
        if option == 'number':
            if request.method == 'POST':
                students = Student.objects.filter(number = request.POST['number'])
                return render(request,'study/depositview.html',{"students" : students})
        if option == 'not':
            students = Student.objects.all().exclude(deposit = "3")
            return render(request,'study/depositview.html',{"students" : students})
        if option == 'today':
            students = Student.objects.all().exclude(deposit = '3')
            students = students.filter(day1 = datetime.date.today())
            return render(request,'study/depositview.html',{"students" : students})

        students = Student.objects.all()
        return render(request,'study/depositview.html',{"students" : students})
    else:
        return redirect('index')


def check_in(request,user_id):
    if request.user.is_staff:
        student = Student.objects.get(pk = user_id)
        student.check_in = str(student.check_in) + str(datetime.date.today())+'/'
        print()
        student.save()
        return redirect('adminpage','today')
    else:
        return redirect('index')



            # studetns =Student.objects.all()

    #         return render(request,'admin.html',{'students':studetns})
    #     elif option == 'today':
    #         if request.method 
    # else:
    #     return redirect('index')






# @login_required(login_url='/login/')
# def change_day(request):  #요일변경
#     try:
#         student = Student.objects.get(user_id = request.user.id)
#         if request.method == 'POST':
#             form = Select_day_form(request.POST)
#             if form.is_valid():
#                 # 최소 2일 전 신청
#                 if (form.cleaned_data['changed_day'] - datetime.date.today()).days <2 : 
#                     return HttpResponse('날짜를 다시 선택해주세요')
#                 student.changed_day = form.cleaned_data['changed_day']
#                 student.save()
#                 return redirect('detail')
#             else:
#                 return render(request,'student/change_day.html',{'form':form})
#         else:
#             form = Select_day_form()
#             return render(request,'student/change_day.html',{'form':form})
#     except :
#         return render(request,'student/error.html',{'is_study':False})




    

############################ view가 아닌 호출함수


def get_basedates(student): #첫 고정 참여일
    arr = []
    for i in range(0,4):
        arr.append(str(student.base_date + timedelta(weeks=i)))
    return arr

def get_days(student): #변경한 날짜
    arr = []
    arr.append(student.day1)
    arr.append(student.day2)
    arr.append(student.day3)
    arr.append(student.day4)
    return arr

############################  



############### 여기서부터 템플릿 뷰  ################

#function_view

def get_left_day(student):
    days = get_days(student)
    left_day = 4
    for i in days :
        if (i - datetime.date.today()).days>=0:
            break
        left_day -= 1
    return left_day


def index(request): # 메인 화면
    imgs = Study_img.objects.all()
    try:
        student = Student.objects.get(user_id = request.user.pk)
        left_day = get_left_day(student)
        if left_day == 0 :
            return render(request, 'study/main/index.html',{"enroll" : "재등록하기","is_zero" : True,"imgs":imgs})
        else:
            return render(request, 'study/main/index.html',{"enroll" : "재등록하기","is_zero" : False,"imgs":imgs})
    except:
        return render(request, 'study/main/index.html',{"enroll" : "등록하기","imgs":imgs})



@login_required(login_url='/user/login/')
def enroll(request): # 등록하기 화면
    try:
        student = Student.objects.get(user_id = request.user.id)
        left_day = get_left_day(student)
        if left_day != 0 : #아직 남았다면
            messages.error(request, "이미 등록하셨습니다!")
            return render(request, 'study/function/enroll.html',{"error" : "스터디 연장 신청은 마지막 스터디 참여 후 가능합니다."})
        else:
            student.user_id = 0
            student.save()
            return render(request, 'study/function/enroll.html')
    except:
        if request.method == 'POST':
            form = Enroll_form(request.POST)
            day1 = datetime.date.fromisoformat(request.POST['day1'])

            if  day1 < datetime.date.today(): #지난 날 신청할 때
                messages.error(request, "등록 실패!")
                return render(request,'study/function/enroll.html',{"error" : "지난날은 신청할 수 없습니다."})

            if day1 == datetime.date.today() + timedelta(days=1) and datetime.datetime.today().hour >=22: #당일 10시 넘어서 다음날 신청할 때
                messages.error(request, "등록 실패!")
                return render(request,'study/function/enroll.html',{"error" : "22시 이후에는 다음날 신청이 불가합니다."})

            if form.is_valid() :
                form = form.save(commit = False)
                for i in range(2,5):
                    setattr(form,f'day{i}',form.day1 + timedelta(weeks=i-1))
                for i in range(2,5):
                    setattr(form,f'time{i}',form.time1)
                form.base_date = form.day1
                form.user_id = request.user.id
                form.name = request.user.first_name
                form.save()

                return redirect('inquire')
            else:
                messages.error(request,'등록 실패!')
                return render(request,'study/function/enroll.html')
        return render(request, 'study/function/enroll.html')



# class Enroll(LoginRequiredMixin,generic.CreateView): #등록하기
#     model = Student
#     fields=['name','number','level','day1']
#     template_name = 'student/enroll.html'
#     login_url = '/login/'
    
#     def get(self, request, *args, **kwargs) :
#         try:
            
#             Student.objects.get(user_id = self.request.user.id)
#             return render(request,'student/error.html',{'is_enroll':True})
#         except:
#             return super().get(request,*args,**kwargs)

#     def form_valid(self, form):
        
#         form = form.save(commit = False)
#         for i in range(2,5):
#             setattr(form,f'day{i}',form.day1 + timedelta(weeks=i-1))
#         form.base_date = form.day1
#         form.user_id = self.request.user.id
#         form.save()

#         return redirect('main')

@login_required(login_url='/user/login/')
def inquire(request): # 조회하기 화면
    try:
        student = Student.objects.get(user_id = request.user.id)
        days =get_days(student)
        left_day = 4
        day = 1
        next_day = None
        for i in days :
            if (i - datetime.date.today()).days>=0:
                next_day = i
                next_time = getattr(student,f'time{day}')
                break
            day += 1
            left_day -= 1
        if next_day == None:
            next_time = '추가등록이 필요합니다'
            next_day = '추가등록이 필요합니다'
        else:
            times = ['평일','주말1시','주말4시']
            next_time = times[int(next_time)]
        base_dates = get_basedates(student)
    except Exception as e :
        print(e)
        return redirect('enroll')

    return render(request,'study/function/inquire.html',
    {'student' : student,
    'days' : days,
    'next_day': next_day,
    'left_day' : left_day,
    'base_dates' : base_dates,
    'next_time' : next_time}
    )   


# @login_required(login_url='/login/')
# def my_study(request): #조회하기

#     try:
#         student = Student.objects.get(user_id = request.user.id)
#         days =get_days(student)
#         for i in days :
#             if (i - datetime.date.today()).days>=0:
#                 next_day = i
#                 break
#         if next_day == None:
#             next_day = '추가등록이 필요합니다'
        

#     except :
#         return render(request,'student/error.html',{'is_study':False})

#     return render(request,'student/detail.html',{'student':student,'days':days,'next_day':next_day})
   
@login_required(login_url='/user/login/')
def change(request): # 변경하기 화면
    try:
        student = Student.objects.get(user_id = request.user.id)
    except:
        return redirect('enroll')
    if request.method == 'POST':
        student = Student.objects.get(user_id = request.user.id)

        try:
            i = int(request.POST['i']) #몇주차 변경하는지
            if  getattr(student,f'day{i}')<= datetime.date.today(): #당일변경 막기
                messages.error(request, "변경 실패!")
                return render(request, 'study/function/change.html', {'student': student})
            date = datetime.date.fromisoformat(request.POST['day'])
            today = datetime.date.today()
        except:
            messages.error(request, "변경 실패!")
            return render(request, 'study/function/change.html', {'student': student})

        base_date = student.base_date #기준 주차 첫 참여일
        first_date = base_date - timedelta(weeks=1-i,days=base_date.isoweekday()-1) #해당 주차의 첫째주
        last_date = base_date - timedelta(weeks=1-i,days=base_date.isoweekday()-7)
        

        if (date - today).days >= 2 and first_date <= date <= last_date: #2일 뒤부터 and 그 주의 첫날과 마지막날 사이여야함
            setattr(student,f'day{i}',request.POST['day'])
            setattr(student,f'time{i}',request.POST['time'])
            student.save()
            return redirect('inquire')
        else:
            messages.error(request, "변경 실패!")
            return render(request, 'study/function/change.html', {'student': student})
    return render(request,'study/function/change.html',{'student' : student})

    


def faq_view(request): # 자주묻는질문 화면
    if request.method == 'POST':
        if request.user.is_authenticated == False :
            return redirect('login')
        else:
            if Faq.objects.filter(user_id = request.user.pk).count() >= 2 :
                messages.error(request,"문의하신 내용이 답변 대기중입니다.")
                return render(request, 'study/function/faq.html')
                
            name = request.user.first_name
            answer_to = request.POST['answer_to']
            text = request.POST['text']
            

            faq = Faq(name = name, answer_to = answer_to, text = text)
            faq.user_id = request.user.pk
            faq.save()
            messages.success(request,"문의가 완료되었습니다.")

    return render(request, 'study/function/faq.html')



# @login_required(login_url='/login/')
# def change_day(request,i): #요일변경
#     if request.method == 'POST':
#         student = Student.objects.get(user_id = request.user.id)
#         date = datetime.date.fromisoformat(request.POST['day'])
#         today = datetime.date.today()
#         base_date = student.base_date #기준 주차 첫 참여일
#         first_date = base_date - timedelta(weeks=1-i,days=base_date.isoweekday()-1) #해당 주차의 첫째주
#         last_date = base_date - timedelta(weeks=1-i,days=base_date.isoweekday()-7)
#         if (date - today).days >= 2 and first_date <= date <= last_date: #2일 뒤부터 and 그 주의 첫날과 마지막날 사이여야함
#             setattr(student,f'day{i}',request.POST['day'])
#             student.save()
#             return redirect('detail')
#         else:
#             return render(request,'student/change_day.html',{'error':'날짜를 다시 입력해주세요'})
#     return render(request,'student/change_day.html')







#sign_view

def login_hw(request): # 로그인 화면
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = Login_form(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username = username , password = password)

            if user is not None :
                auth.login(request,user)
                return redirect('index')

            messages.error(request, "다시 입력해주세요!")
            return render(request,'study/sign/login.html')
       
    else:
        return render(request,'study/sign/login.html')




def find_id(request):  #id찾기
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        user = User.objects.filter(first_name = name, email = email)
        if user.count() != 0: # ==0 이면 해당 유저가 없음
            return render(request,'study/sign/find_id.html',{'username' : 'ID : ' + user[0].username + '입니다'}) 
        else :
            return render(request,'study/sign/find_id.html',{'error' : '이름 혹은 이메일을 다시 입력해주세요'})        
    return render(request,'study/sign/find_id.html')





def find_pw(request):  #password찾기
    if request.method == 'POST':
        name = request.POST['username']
        email = request.POST['email']
        user = User.objects.filter(username = name, email = email)
        if user.count() != 0: # ==0 이면 해당 유저가 없음
            message = render_to_string('reset_pw_message.html',{
                "domain" : get_current_site(request),
                "uid" : urlsafe_base64_encode(force_bytes(user[0].pk)),
                "token" : default_token_generator.make_token(user[0]),
            }) 
            
            email = EmailMessage('원투스픽 비밀번호 초기화',message,to=[email])
            try:
                if user.last_name == '2' :
                    return render(request,'study/error.html')    
                else:
                    email.send()
                    user.last_name = 2
                    user.save()
            except:
                return render(request,'study/error.html')
            return render(request,'study/sign/find_pw.html',{'message' : '이메일을 확인하여주세요'}) 
        else :
            return render(request,'study/sign/find_pw.html',{'error' : '아이디 혹은 이메일을 다시 입력해주세요'})        
    return render(request,'study/sign/find_pw.html')






def reset_pw(request,uid64,token): #password 초기화
    #uid64 는 이미 byte 화 및 uid 해시 되어서 날라갔음, 그걸 다시 받는것
    #받은걸 복호화 및 그걸 다시 str로 바꿔야함
    uid = force_text(urlsafe_base64_decode(uid64))
    try :
        user = User.objects.get(pk = uid)
        if user is not None and default_token_generator.check_token(user,token): #해당 pk 에 따른 user가 존재하고, 토큰이 유효할 시
            if request.method == 'POST':
                user = User.objects.get(pk = uid)
                password = request.POST['password']
                password2 = request.POST['password2']
                if password == password2:
                    user.set_password(password)
                    user.last_name = 1
                    user.save()
                    return redirect('login')
                else:
                    return render(request,'study/sign/reset_pw.html',{'error' : "비밀번호를 다시 확인해주세요"})
            else:
                return render(request,'study/sign/reset_pw.html')
    except:
        return render(request, 'study/error.html')

# def login(request): #로그인
#     if request.method == 'POST':
#         form = Login_form(request.POST)

#         if form.is_valid():
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']
#             user = authenticate(username = username , password = password)

#             if user is not None :
#                 auth.login(request,user)
#                 return redirect('main')
           
#             return render(request,'student/login.html',{'form':form})    
       
#     else:
#         form = Login_form()
#         return render(request,'student/login.html',{'form':form})  

@login_required(login_url='/user/login/')
def logout(request): #로그아웃
    auth.logout(request)
    return redirect('index')

def validate_password(password): #password 유효성검사
    validate_list = [
        lambda p : len(p)>= 4,
        lambda p : len(p)<=20,
        lambda p : all(x.islower() or x.isupper() or (x in ['!', '@', '#', '$', '%', '^', '&', '*', '_']) or x.isdigit() for x in p),
        lambda p : any(x.islower() for x in p)
    ]
    for validator in validate_list:
        if not validator(password):
            return True


def signup_hw(request): # 회원가입 화면
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = Signup_form(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            password2 = form.cleaned_data['password2']
            email = form.cleaned_data['email']
            name = form.cleaned_data['name']

            if User.objects.filter(username = username).count() != 0 : #ID 중복시
                return render(request,'study/sign/signup.html',{'form_error' : '양식을 정확히 다시 작성해주세요'})
           
            if User.objects.filter(email = email).count() != 0 : #이메일 중복 시
                return render(request,'study/sign/signup.html',{
                    'email_error' : '중복된 이메일입니다', 
                    'username' : username,
                    'email' : email,
                    'name' : name,
                    're' : True}
                    )
            if validate_password(password):
                return render(request,'study/sign/signup.html',{
                    'password_error' : '4자이상, 영문자포함, 숫자, 특수문자 조합으로만 가능합니다', 
                    'username' : username,
                    'email' : email,
                    'name' : name,
                    're' : True}
                    )
            if password == password2 :
                user = User(first_name = name,email = email, username = username)
                user.set_password(password)
                user.is_active = False
                user.save()
                
                
                current_site = get_current_site(request) 
                # localhost:8000
                message = render_to_string('study/sign/activate.html',{
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token' : default_token_generator.make_token(user)
                })
                
                act_email = EmailMessage('[원투스픽] 인증을 위한 메일입니다',message,to=[email])
                # try:
                #     act_email.send()
                    
                # except:
                #     return render(request, 'study/error.html')
                act_email.send()
                # user = authenticate(username = username , password = password)
                # auth.login(request,user)
                
                return render(request,'study/sign/checkemail.html',{"email" : email})
            else:
                return render(request,'study/sign/signup.html',{
                    'password_error' : '비밀번호를 다시 확인해주세요 ', 
                    'username' : username,
                    'email' : email,
                    'name' : name,
                    're' : True}
                    )
        else:
            return render(request,'study/sign/signup.html',{'form_error' : '양식을 정확히 다시 작성해주세요'})
    else:
        return render(request,'study/sign/signup.html')


def re_send(request,email): #이메일 재전송
    try:
        user = User.objects.filter(email = email)[0]
        if(user.last_name == '1'):
            return HttpResponse('그런 행동이 저희를 힘들게합니다.')
        user.last_name = 1
        user.save()
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        current_site = get_current_site(request)
        message =render_to_string('study/sign/activate.html',{
            "user" : user,
            "uid" : uid,
            "domain" : current_site.domain,
            "token" : token,
        })
        re_email = EmailMessage('[원투스픽] 인증메일 재발송입니다',message,to=[email])
        re_email.send()
        return HttpResponse('success')
    except Exception as e:
        print(e)
        return render(request,'study/error.html')



def validate_username(username): #ID 유효성검사
    validate_list = [
        lambda u : len(u)>=5,
        lambda u : len(u)<20,
        lambda u : any(l.islower() for l in u), #소문자 필수
        lambda u : all(l.islower() or l.isdigit() or l =='_' for l in u)] #영소문자, 숫자, 언더바만 아이디로 사용가능
    
    for validator in validate_list :
        if not validator(username):
            return True



def is_duplicated(request): #ID 중복검사
    username = request.GET['username']
    if User.objects.filter(username = username).count() != 0 :
        data ={
            "is_dp" : False,
            "message" : "이미 존재하는 ID 입니다"
        }
        return HttpResponse(json.dumps(data))
    elif validate_username(username) :
        data ={
            "is_dp" : False,
            "message" : "5자 이상, 영소문자, 숫자, '_' 조합으로만 가능합니다"
        }
        return HttpResponse(json.dumps(data))
    else:
        data ={
            "is_dp" : True,
            "message" : "사용가능한 ID 입니다"
        }
        return HttpResponse(json.dumps(data))


def activate(request,uid64,token):
    try:
        uid = force_text(urlsafe_base64_decode(uid64))
        user = User.objects.get(pk = uid)
        
        if user is not None and default_token_generator.check_token(user,token):
            user.is_active = True
            user.save()
            auth.login(request,user)
            return redirect('index')
        return redirect('index')
    except Exception as e:
        print(e)
        return render(request,'study/error.html')

    

# def signup(request): #회원가입
#     if request.method == 'POST':
#         form = Signup_form(request.POST)

#         if form.is_valid():
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']
#             password2 = form.cleaned_data['password2']
#             if password == password2:
#                 user = User.objects.create_user(username = username,password = password)
#                 user.is_active = False
#                 user.save()
                
#                 current_site = get_current_site(request) 
#                 # localhost:8000
#                 message = render_to_string('activate.html',{
#                     'user': user,
#                     'domain': current_site.domain,
#                     'uid': urlsafe_base64_encode(force_bytes(user.pk)),
#                     'token' : default_token_generator.make_token(user)
#                 })

#                 email = EmailMessage('인증을 위한 메일입니다',message,to=['ppm5377@naver.com'])
#                 email.send()
#                 # user = authenticate(username = username , password = password)
#                 # auth.login(request,user)
#                 return redirect('main')
#             else:
#                 form = Signup_form(initial ={'username':username}) #비밀번호 새로입력받기
                
#                 return render(request,'student/signup.html',{'form' : form})

            
            
           
#         else:
#             return render(request,'student/signup.html',{'form' : form})
#     else:
#         form = Signup_form()
#         return render(request,'student/signup.html',{'form' : form})


def checkemail(request): #인증메일 확인 부탁 페이지
    return render(request, 'study/sign/checkemail.html')

def testError(request): # 에러 페이지 테스트
    return render(request, 'study/error.html')


#함수가 만들어질때 항상 실행되는 함수 dispatch 를 재정의 하는 방법
#name 과 일치하는 클래스의 메소드에 대해서만 데코레이터를 적용하는방법
#https://ssungkang.tistory.com/entry/Django-FBV-%EC%99%80-CBV-%EC%9D%98-decorators-%EC%82%AC%EC%9A%A9%EB%B2%95
@method_decorator(staff_member_required,name="dispatch")
class Img_update_view(generic.CreateView):
    model = Study_img
    fields = '__all__'
    template_name = 'study/uploadimg.html'
    success_url = "/uploadimg/"

    def get_context_data(self, **kwargs):
        kwargs["imgs"] = Study_img.objects.all()
        return super().get_context_data(**kwargs)
    

import boto3

@staff_member_required(login_url='/')
def deleteimg(request,pk):
    img = Study_img.objects.get(pk = pk)
    s3_client = boto3.client(
        's3',
        aws_access_key_id = settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY,
        region_name = settings.AWS_REGION,
    )
    key = img.pic.name
    #키는 버킷이름 다음에 위치하는 경로
    s3_client.delete_object(Bucket='elasticbeanstalk-ap-northeast-2-293437042513',Key='media/'+key)
    img.delete()
    return HttpResponse('삭제완료')