from django.db.models.query_utils import Q
import boto3
from django.conf import settings
from datetime import timedelta, tzinfo
from typing import ContextManager
from django.db.models import fields
from django.db.models.query import NamedValuesListIterable, QuerySet
from django.http import response, HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse

from django.views import generic
from django.contrib import auth
from .models import *
from .forms import *


import bcrypt
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage, message
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages

import json

from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
# Create your views here.


def only_admin(request, option):
    if request.user.is_staff:

        if option == 'all':
            new_students = Student.objects.filter(
                deposit='1').exclude(user_id=0)
            students = Student.objects.all().exclude(
                deposit='1').order_by('-lesson_day').exclude(user_id=0)
            return render(request, 'study/admin.html', {'students': students, 'new_students': new_students})

        if option == 'today':
            lesson_students = Student.objects.filter(
                lesson_day__date=datetime.date.today(), check_in='2').exclude(user_id=0)
            new_students = Student.objects.filter(
                day1=datetime.date.today(), check_in='1'
            ).exclude(user_id=0)

            return render(request, 'study/admin.html', {'lesson_students': lesson_students, 'new_students': new_students})

        if option == 'name':
            if request.method == 'POST':
                students = Student.objects.filter(
                    name=request.POST['name']).exclude(user_id=0)
                return render(request, 'study/admin.html', {'students': students})

        if option == 'number':
            if request.method == 'POST':
                students = Student.objects.filter(
                    number=request.POST['number']).exclude(user_id=0)
                return render(request, 'study/admin.html', {'students': students})

        if option == 'new':
            new_students = Student.objects.filter(
                check_in="1").exclude(user_id=0)
            return render(request, 'study/admin.html', {'new_students': new_students})
    else:
        return redirect('index')


def check_deposit(request, option, user_id, way):
    if request.user.is_staff:
        student = Room.objects.get(pk=user_id)
        student.deposit = option
        student.pay_way = way
        student.save()
        return redirect('deposit_view', 'all')
    else:
        return redirect('index')


def deposit_view(request, option):
    if request.user.is_staff:
        if option == 'name':
            if request.method == 'POST':
                rooms = Room.objects.filter(
                    name=request.POST['name']).order_by('-day1')
                return render(request, 'study/depositview.html', {"rooms": rooms})
        if option == 'number':
            if request.method == 'POST':
                rooms = Room.objects.filter(
                    number=request.POST['number'])
                return render(request, 'study/depositview.html', {"rooms": rooms})
        if option == 'not':
            rooms = Room.objects.all().exclude(deposit="3")
            return render(request, 'study/depositview.html', {"rooms": rooms})
        if option == 'today':
            rooms = Room.objects.all().exclude(deposit='3')
            rooms = rooms.filter(day1__date=datetime.date.today())
            return render(request, 'study/depositview.html', {"rooms": rooms})

        if option == 'todayall':
            rooms = Room.objects.all().filter(day1__date=datetime.date.today())
            return render(request, 'study/depositview.html', {"rooms": rooms})

        rooms = Room.objects.all()
        return render(request, 'study/depositview.html', {"rooms": rooms})
    else:
        return redirect('index')


def check_in(request, user_id):
    if request.user.is_staff:
        room = Student.objects.get(pk=user_id)
        room.check_in = str(room.check_in) + \
            str(datetime.date.today())+'/'
        print()
        room.save()
        return redirect('adminpage', 'today')
    else:
        return redirect('index')

        # studetns =Student.objects.all()

    #         return render(request,'admin.html',{'students':studetns})
    #     elif option == 'today':
    #         if request.method
    # else:
    #     return redirect('index')


# @login_required(login_url='/login/')
# def change_day(request):  #????????????
#     try:
#         student = Student.objects.get(user_id = request.user.id)
#         if request.method == 'POST':
#             form = Select_day_form(request.POST)
#             if form.is_valid():
#                 # ?????? 2??? ??? ??????
#                 if (form.cleaned_data['changed_day'] - datetime.date.today()).days <2 :
#                     return HttpResponse('????????? ?????? ??????????????????')
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


# view??? ?????? ????????????


def get_basedates(student):  # ??? ?????? ?????????
    arr = []
    for i in range(0, 4):
        arr.append(str(student.base_date + timedelta(weeks=i)))
    return arr


def get_days(student):  # ????????? ??????
    arr = []
    arr.append(student.day1)
    arr.append(student.day2)
    arr.append(student.day3)
    arr.append(student.day4)
    return arr

############################


############### ??????????????? ????????? ???  ################

# function_view

def get_left_day(student):
    days = get_days(student)
    left_day = 4
    for i in days:
        if (i - datetime.date.today()).days >= 0:
            break
        left_day -= 1
    return left_day


def index(request):  # ?????? ??????
    imgs = Study_img.objects.all()
    try:
        student = Student.objects.get(user_id=request.user.pk)
        if student.check_in == '1':
            # ?????? ???????????? ???????????????
            is_enrolled = False
            day1 = student.day1
        else:
            is_enrolled = True
            day1 = student.lesson_day
        return render(request, 'study/main/index.html', {"enroll": "???????????????", "is_enrolled": is_enrolled, "day1": day1, "imgs": imgs})

    except:
        return render(request, 'study/main/index.html', {"enroll": "????????????", "no_enroll": True, "imgs": imgs})


@login_required(login_url='/user/login/')
def lesson_enroll(request):  # ?????? ?????? ??????
    try:
        student = Student.objects.get(user_id=request.user.id)

        if student.check_in == '1':
            # ?????? ???????????? ???????????????
            is_enrolled = False
            day1 = student.day1
        else:
            is_enrolled = True
            day1 = student.lesson_day

        if student.day1 > datetime.date.today() != 0:  # ?????? ????????????
            messages.error(request, "?????? ?????????????????????!")
            return render(request, 'study/function/lesson_enroll.html', {"error": "???????????? ?????? ?????????????????? ???????????????.", "is_enrolled": is_enrolled, "day1": day1})
        else:
            student.user_id = 0
            student.save()
            return render(request, 'study/function/lesson_enroll.html')
    except:
        if request.method == 'POST':
            form = Enroll_form(request.POST)
            day1 = datetime.date.fromisoformat(request.POST['day1'])

            if day1 < datetime.date.today():  # ?????? ??? ????????? ???
                messages.error(request, "?????? ??????!")
                return render(request, 'study/function/lesson_enroll.html', {"error": "???????????? ????????? ??? ????????????.", "no_enroll": True})

            if day1 == datetime.date.today() + timedelta(days=1) and datetime.datetime.today().hour >= 22:  # ?????? 10??? ????????? ????????? ????????? ???
                messages.error(request, "?????? ??????!")
                return render(request, 'study/function/lesson_enroll.html', {"error": "22??? ???????????? ????????? ????????? ???????????????.", "no_enroll": True})

            if form.is_valid():
                form = form.save(commit=False)
                form.user_id = request.user.id
                form.name = request.user.first_name
                form.save()

                return redirect('inquire')
            else:
                messages.error(request, '?????? ??????!')
                return render(request, 'study/function/lesson_enroll.html', {"no_enroll": True})
        return render(request, 'study/function/lesson_enroll.html', {"no_enroll": True})


@login_required(login_url='/user/login/')
def enroll(request):  # ???????????? ??????
    student = Student.objects.filter(user_id=request.user.id)
    if student.exists():
        no_enroll = False
        if student[0].check_in == '1':
            # ?????? ???????????? ???????????????
            is_enrolled = False
            day = student[0].day1
        else:
            is_enrolled = True
            day = student[0].lesson_day
    else:
        is_enrolled = False
        day = 1
        no_enroll = True

    try:
        room = Room.objects.get(user_id=request.user.id)
        if request.method == 'POST':
            if request.POST['date'] == '0':
                Room.objects.get(user_id=request.user.id).delete()
                return redirect('enroll')
        return render(request, 'study/function/enroll.html', {"error": "?????? ??? ?????? ?????? ???????????????.",
                                                              "is_enrolled": is_enrolled,
                                                              "day1": day,
                                                              "no_enroll": no_enroll,
                                                              "is_reserved": True,
                                                              "room": room,
                                                              "time_from": room.day1.time,
                                                              "time_to": (room.day1+datetime.timedelta(hours=2)).time})

    except:
        if request.method == 'POST':
            number = request.POST['number']
            day1 = datetime.datetime.fromisoformat(
                f"{request.POST['date']} {request.POST['time']}:00")
            if day1 < datetime.datetime.today():  # ?????? ??? ????????? ???
                messages.error(request, "?????? ??????!")
                return redirect('enroll')
            room = Room(
                number=number,
                day1=day1,
                user_id=request.user.id,
                name=request.user.first_name)
            room.save()
            return redirect('enroll')

        return render(request, 'study/function/enroll.html', {
            "is_enrolled": is_enrolled,
            "day1": day,
            "no_enroll": no_enroll,
            "is_reserved": False,
        })


# class Enroll(LoginRequiredMixin,generic.CreateView): #????????????
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
def inquire(request):  # ???????????? ??????
    try:
        student = Student.objects.get(user_id=request.user.id)
        if student.check_in == '1':
            # ?????? ???????????? ???????????????
            is_enrolled = False
            day = student.day1
        else:
            is_enrolled = True
            day = student.lesson_day
    except:
        return redirect('lesson')
    if request.method == 'POST':
        student = Student.objects.get(user_id=request.user.id)
        if request.POST['day1'] == '0':
            student.user_id = 0
            student.save()
            return redirect('lesson')
        day1 = datetime.date.fromisoformat(request.POST['day1'])
        if day1 < datetime.date.today():  # ????????????/?????? ??? ??????
            messages.error(request, "?????? ??????!")
            return redirect('inquire')
        else:
            student.day1 = day1
            student.save()
            return redirect('inquire')
    else:
        return render(request, 'study/function/inquire.html',
                      {'student': student, "is_enrolled": is_enrolled, "day1": day}
                      )


# @login_required(login_url='/login/')
# def my_study(request): #????????????

#     try:
#         student = Student.objects.get(user_id = request.user.id)
#         days =get_days(student)
#         for i in days :
#             if (i - datetime.date.today()).days>=0:
#                 next_day = i
#                 break
#         if next_day == None:
#             next_day = '??????????????? ???????????????'


#     except :
#         return render(request,'student/error.html',{'is_study':False})

#     return render(request,'student/detail.html',{'student':student,'days':days,'next_day':next_day})

@login_required(login_url='/user/login/')
def change(request):  # ???????????? ??????
    try:
        student = Student.objects.get(user_id=request.user.id)
    except:
        return redirect('enroll')
    if request.method == 'POST':
        student = Student.objects.get(user_id=request.user.id)
        try:
            i = int(request.POST['i'])  # ????????? ???????????????
            if getattr(student, f'day{i}') <= datetime.date.today():  # ???????????? ??????
                messages.error(request, "?????? ??????!")
                return render(request, 'study/function/change.html', {'student': student})
            date = datetime.date.fromisoformat(request.POST['day'])
            today = datetime.date.today()
        except:
            messages.error(request, "?????? ??????!")
            return render(request, 'study/function/change.html', {'student': student})

        base_date = student.base_date  # ?????? ?????? ??? ?????????
        first_date = base_date - \
            timedelta(weeks=1-i, days=base_date.isoweekday()-1)  # ?????? ????????? ?????????
        last_date = base_date - \
            timedelta(weeks=1-i, days=base_date.isoweekday()-7)

        if (date - today).days >= 2 and first_date <= date <= last_date:  # 2??? ????????? and ??? ?????? ????????? ???????????? ???????????????
            setattr(student, f'day{i}', request.POST['day'])
            setattr(student, f'time{i}', request.POST['time'])
            student.save()
            return redirect('inquire')
        else:
            messages.error(request, "?????? ??????!")
            return render(request, 'study/function/change.html', {'student': student})
    return render(request, 'study/function/change.html', {'student': student})


def faq_view(request):  # ?????????????????? ??????
    if request.method == 'POST':
        if request.user.is_authenticated == False:
            return redirect('login')
        else:
            if Faq.objects.filter(user_id=request.user.pk).count() >= 2:
                messages.error(request, "???????????? ????????? ?????? ??????????????????.")
                return render(request, 'study/function/faq.html')

            name = request.user.first_name
            answer_to = request.POST['answer_to']
            text = request.POST['text']

            faq = Faq(name=name, answer_to=answer_to, text=text)
            faq.user_id = request.user.pk
            faq.save()
            messages.success(request, "????????? ?????????????????????.")

    return render(request, 'study/function/faq.html')


@login_required(login_url='/user/login')
def qna_list(request):  # ????????????
    if request.user.is_staff:
        page = int(request.GET['page'])
        qnas = Qna.objects.all().order_by('-pk')
        page_len = qnas.count()//11 + 1

        qnas = qnas[10*(page-1):10*page]
        qnas = render_to_string(
            'study/function/qna_list_base.html', context={"qnas": qnas, "is_staff": True})
        context = {
            "qnas": qnas,
            "page_len": page_len
        }
        context = json.dumps(context)
        return HttpResponse(context)
    else:
        page = int(request.GET['page'])
        qnas = Qna.objects.filter(user=request.user).order_by('-pk')
        page_len = qnas.count()//11 + 1

        qnas = qnas[10*(page-1):10*page]
        qnas = render_to_string(
            'study/function/qna_list_base.html', context={"qnas": qnas})

        context = {
            "qnas": qnas,
            "page_len": page_len
        }
        context = json.dumps(context)
        return HttpResponse(context)


@login_required(login_url='/user/login')
def qna_view(request, num):
    try:
        student = Student.objects.get(user_id=request.user.id)
        if student.check_in == '1':
            # ?????? ???????????? ???????????????
            is_enrolled = False
            day1 = student.day1
        else:
            is_enrolled = True
            day1 = student.lesson_day
    except:
        return render(request, 'study/function/qna_view.html', {"num": num, "no_enroll": True})

    return render(request, 'study/function/qna_view.html', {"num": num, "is_enrolled": is_enrolled, "day1": day1})


@login_required(login_url='/user/login')
def qna_enroll(request):
    if request.method == "POST":
        try:
            last = Qna.objects.filter(user=request.user).last()
            if last.next_qna > datetime.datetime.today():
                messages.error(request, "?????? ??? 10?????? ???????????? ???????????????.")
                return render(request, 'study/function/qna_enroll.html',{'need_to_delete' : True})
            else:
                raise Exception()
        except:
            qna = Qna(user=request.user)
            qna.title = request.POST["title"]
            qna.text = request.POST["text"]
            qna.date = datetime.date.today()
            qna.next_qna = datetime.datetime.now(
                tz=None) + datetime.timedelta(minutes=10)
            qna.save()
            return redirect('qna_view', 1)
    return render(request, 'study/function/qna_enroll.html',{'need_to_delete' : True})


@login_required(login_url='/user/login')
def qna_delete(request, pk):
    qna = Qna.objects.get(pk=pk)

    if qna.user == request.user or request.user.is_staff:
        qna.delete()
        return redirect('qna_view', 1)
    else:
        messages.error(request, '????????? ?????? ????????? ??????????????????.')
        return redirect('qna_view', 1)


@login_required(login_url='/user/login')
def qna_detail(request, pk):
    if request.user.is_staff:
        # ????????????
        qna = Qna.objects.get(pk=pk)
        if request.method == "POST":
            qna.answer = request.POST["answer"]
            qna.save()
        return render(request, 'study/function/qna_detail.html', context={"qna": qna,'need_to_delete' : True})
    else:
        qna = Qna.objects.filter(user=request.user, pk=pk).last()
        if request.method == "POST":
            if qna.answer:
                messages.error(request, "????????? ????????? ?????? ????????? ??????????????????.")
                return render(request, 'study/function/qna_detail.html', context={"qna": qna,'need_to_delete' : True})
            else:
                qna.title = request.POST["title"]
                qna.text = request.POST["text"]
                qna.next_qna = datetime.datetime.today() + datetime.timedelta(minutes=10)
                qna.save()
        return render(request, 'study/function/qna_detail.html', context={"qna": qna,'need_to_delete' : True})


def my_review(request):
    if not request.user.is_authenticated:
        return redirect('login')
    review = Review.objects.filter(user=request.user)
    if review.exists():
        return redirect('review_detail', review.last().pk)
    else:
        return redirect('review_enroll')



def review_list(request):  # ????????????
    page = int(request.GET['page'])
    reviews = Review.objects.all().order_by('-pk')
    page_len = reviews.count()//11 + 1

    reviews = reviews[10*(page-1):10*page]
    reviews = render_to_string(
        'study/function/review_list_base.html', context={"reviews": reviews})

    context = {
        "reviews": reviews,
        "page_len": page_len
    }
    context = json.dumps(context)
    return HttpResponse(context)


def review_view(request, num):
    if not request.user.is_authenticated :
        return render(request,'study/function/review_view.html', {"num": num,"need_to_delete" : True })
    else :
        review = Review.objects.filter(user = request.user)
        return render(request, 'study/function/review_view.html', {"num": num, "need_to_delete": True,'review':review})


@login_required(login_url='/user/login')
def review_enroll(request):
    if request.method == "POST":
        try:
            if not Student.objects.filter(user_id=request.user.id).exists() or Student.objects.filter(user_id=request.user.id)[0].check_in == '1':
                messages.error(request, "????????? ????????? ????????? ???????????? ???????????????")
                return redirect('review_view', 1)
            elif Review.objects.get(user=request.user):
                messages.error(request, "????????? ????????? ?????? ???????????????")
                return redirect('review_view', 1)
        except:
            review = Review(user=request.user)
            review.title = request.POST["title"]
            review.text = request.POST["text"]
            review.date = datetime.date.today()
            review.next_review = datetime.datetime.now(
                tz=None) + datetime.timedelta(minutes=10)
            review.save()
            return redirect('review_view', 1)
    return render(request, 'study/function/review_enroll.html',{'need_to_delete' : True})


@login_required(login_url='/user/login')
def review_delete(request, pk):
    review = Review.objects.get(pk=pk)

    if review.user == request.user or request.user.is_staff:
        review.delete()
        return redirect('review_view', 1)
    else:
        messages.error(request, '????????? ?????? ????????? ??????????????????.')
        return redirect('review_view', 1)


def review_detail(request, pk):
    
    review = Review.objects.get(pk=pk)
    if request.method == "POST":
        if review.answer:
            messages.error(request, "????????? ????????? ????????? ????????? ??????????????????.")
            return render(request, 'study/function/review_detail.html', context={"review": review,'need_to_delete' : True})
        elif review.user == request.user:
            review.title = request.POST["title"]
            review.text = request.POST["text"]
            review.save()
        else:
            messages.error(request, "????????? ????????? ????????? ??? ????????????")
            return render(request, 'study/function/review_detail.html', context={"review": review,'need_to_delete' : True})
    return render(request, 'study/function/review_detail.html', context={"review": review,'need_to_delete' : True})


# @login_required(login_url='/login/')
# def change_day(request,i): #????????????
#     if request.method == 'POST':
#         student = Student.objects.get(user_id = request.user.id)
#         date = datetime.date.fromisoformat(request.POST['day'])
#         today = datetime.date.today()
#         base_date = student.base_date #?????? ?????? ??? ?????????
#         first_date = base_date - timedelta(weeks=1-i,days=base_date.isoweekday()-1) #?????? ????????? ?????????
#         last_date = base_date - timedelta(weeks=1-i,days=base_date.isoweekday()-7)
#         if (date - today).days >= 2 and first_date <= date <= last_date: #2??? ????????? and ??? ?????? ????????? ???????????? ???????????????
#             setattr(student,f'day{i}',request.POST['day'])
#             student.save()
#             return redirect('detail')
#         else:
#             return render(request,'student/change_day.html',{'error':'????????? ?????? ??????????????????'})
#     return render(request,'student/change_day.html')


def test3(request):
    return HttpResponse("??????"+request.GET['val'])


# sign_view

def login_hw(request):  # ????????? ??????
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = Login_form(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)

            if user is not None:
                auth.login(request, user)
                return redirect('index')

            messages.error(request, "?????? ??????????????????!")
            return render(request, 'study/sign/login.html')

    else:
        return render(request, 'study/sign/login.html')


def find_id(request):  # id??????
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        user = User.objects.filter(first_name=name, email=email)
        if user.count() != 0:  # ==0 ?????? ?????? ????????? ??????
            return render(request, 'study/sign/find_id.html', {'username': 'ID : ' + user[0].username + '?????????'})
        else:
            return render(request, 'study/sign/find_id.html', {'error': '?????? ?????? ???????????? ?????? ??????????????????'})
    return render(request, 'study/sign/find_id.html')


def find_pw(request):  # password??????
    if request.method == 'POST':
        name = request.POST['username']
        email = request.POST['email']
        user = User.objects.filter(username=name, email=email)
        if user.count() != 0:  # ==0 ?????? ?????? ????????? ??????
            message = render_to_string('reset_pw_message.html', {
                "domain": get_current_site(request),
                "uid": urlsafe_base64_encode(force_bytes(user[0].pk)),
                "token": default_token_generator.make_token(user[0]),
            })

            email = EmailMessage('???????????? ???????????? ?????????', message, to=[email])
            try:
                if user.last_name == '2':
                    return render(request, 'study/error.html')
                else:
                    email.send()
                    user.last_name = 2
                    user.save()
            except:
                return render(request, 'study/error.html')
            return render(request, 'study/sign/find_pw.html', {'message': '???????????? ?????????????????????'})
        else:
            return render(request, 'study/sign/find_pw.html', {'error': '????????? ?????? ???????????? ?????? ??????????????????'})
    return render(request, 'study/sign/find_pw.html')


def reset_pw(request, uid64, token):  # password ?????????
    # uid64 ??? ?????? byte ??? ??? uid ?????? ????????? ????????????, ?????? ?????? ?????????
    # ????????? ????????? ??? ?????? ?????? str??? ????????????
    uid = force_text(urlsafe_base64_decode(uid64))
    try:
        user = User.objects.get(pk=uid)
        # ?????? pk ??? ?????? user??? ????????????, ????????? ????????? ???
        if user is not None and default_token_generator.check_token(user, token):
            if request.method == 'POST':
                user = User.objects.get(pk=uid)
                password = request.POST['password']
                password2 = request.POST['password2']
                if password == password2:
                    user.set_password(password)
                    user.last_name = 1
                    user.save()
                    return redirect('login')
                else:
                    return render(request, 'study/sign/reset_pw.html', {'error': "??????????????? ?????? ??????????????????"})
            else:
                return render(request, 'study/sign/reset_pw.html')
    except:
        return render(request, 'study/error.html')

# def login(request): #?????????
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
def logout(request):  # ????????????
    auth.logout(request)
    return redirect('index')


def validate_password(password):  # password ???????????????
    validate_list = [
        lambda p: len(p) >= 4,
        lambda p: len(p) <= 20,
        lambda p: all(x.islower() or x.isupper() or (
            x in ['!', '@', '#', '$', '%', '^', '&', '*', '_']) or x.isdigit() for x in p),
        lambda p: any(x.islower() for x in p)
    ]
    for validator in validate_list:
        if not validator(password):
            return True


def signup_hw(request):  # ???????????? ??????
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

            if User.objects.filter(username=username).count() != 0:  # ID ?????????
                return render(request, 'study/sign/signup.html', {'form_error': '????????? ????????? ?????? ??????????????????'})

            if User.objects.filter(email=email).count() != 0:  # ????????? ?????? ???
                return render(request, 'study/sign/signup.html', {
                    'email_error': '????????? ??????????????????',
                    'username': username,
                    'email': email,
                    'name': name,
                    're': True}
                )
            if validate_password(password):
                return render(request, 'study/sign/signup.html', {
                    'password_error': '4?????????, ???????????????, ??????, ???????????? ??????????????? ???????????????',
                    'username': username,
                    'email': email,
                    'name': name,
                    're': True}
                )
            if password == password2:
                user = User(first_name=name, email=email, username=username)
                user.set_password(password)
                user.is_active = False
                user.save()

                current_site = get_current_site(request)
                # localhost:8000
                message = render_to_string('study/sign/activate.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user)
                })

                act_email = EmailMessage(
                    '[??????] ????????? ?????? ???????????????', message, to=[email])
                # try:
                #     act_email.send()

                # except:
                #     return render(request, 'study/error.html')
                act_email.send()
                # user = authenticate(username = username , password = password)
                # auth.login(request,user)

                return render(request, 'study/sign/checkemail.html', {"email": email})
            else:
                return render(request, 'study/sign/signup.html', {
                    'password_error': '??????????????? ?????? ?????????????????? ',
                    'username': username,
                    'email': email,
                    'name': name,
                    're': True}
                )
        else:
            return render(request, 'study/sign/signup.html', {'form_error': '????????? ????????? ?????? ??????????????????'})
    else:
        return render(request, 'study/sign/signup.html')


def re_send(request, email):  # ????????? ?????????
    try:
        user = User.objects.filter(email=email)[0]
        if(user.last_name == '1'):
            return HttpResponse('?????? ????????? ????????? ??????????????????.')
        user.last_name = 1
        user.save()
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        current_site = get_current_site(request)
        message = render_to_string('study/sign/activate.html', {
            "user": user,
            "uid": uid,
            "domain": current_site.domain,
            "token": token,
        })
        re_email = EmailMessage('[??????] ???????????? ??????????????????', message, to=[email])
        re_email.send()
        return HttpResponse('success')
    except Exception as e:
        print(e)
        return render(request, 'study/error.html')


def validate_username(username):  # ID ???????????????
    validate_list = [
        lambda u: len(u) >= 5,
        lambda u: len(u) < 20,
        lambda u: any(l.islower() for l in u),  # ????????? ??????
        lambda u: all(l.islower() or l.isdigit() or l == '_' for l in u)]  # ????????????, ??????, ???????????? ???????????? ????????????

    for validator in validate_list:
        if not validator(username):
            return True


def is_duplicated(request):  # ID ????????????
    username = request.GET['username']
    if User.objects.filter(username=username).count() != 0:
        data = {
            "is_dp": False,
            "message": "?????? ???????????? ID ?????????"
        }
        return HttpResponse(json.dumps(data))
    elif validate_username(username):
        data = {
            "is_dp": False,
            "message": "5??? ??????, ????????????, ??????, '_' ??????????????? ???????????????"
        }
        return HttpResponse(json.dumps(data))
    else:
        data = {
            "is_dp": True,
            "message": "??????????????? ID ?????????"
        }
        return HttpResponse(json.dumps(data))


def activate(request, uid64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uid64))
        user = User.objects.get(pk=uid)

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            auth.login(request, user)
            return redirect('index')
        return redirect('index')
    except Exception as e:
        print(e)
        return render(request, 'study/error.html')




import requests


#######?????? ?????????#######

def signup_sns(request):  # sns????????????
    encoded_em = str(request.GET['email']).encode('utf-8')
    #??????????????? ???????????? ?????? ????????????
    if not bcrypt.checkpw(encoded_em,request.GET['hashed'].encode('utf-8')):
        return redirect('index')

    if request.user.is_authenticated:
        return redirect('index')

    email = request.GET['email']

    if request.method == 'POST':
        form = Signup_sns_form(request.POST)
        

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            password2 = form.cleaned_data['password2']
            email = email
            name = form.cleaned_data['name']

            if User.objects.filter(username=username).count() != 0:  # ID ?????????
                return render(request, 'study/sign/signup_sns.html', {'form_error': '????????? ????????? ?????? ??????????????????'})
            if validate_password(password):
                return render(request, 'study/sign/signup_sns.html', {
                    'password_error': '4?????????, ???????????????, ??????, ???????????? ??????????????? ???????????????',
                    'username': username,
                    'email': email,
                    'name': name,
                    're': True}
                )
            if password == password2:
                user = User(first_name=name, email=email, username=username)
                user.set_password(password)
                user.save()
                return redirect('index')
            else:
                return render(request, 'study/sign/signup_sns.html', {
                    'password_error': '??????????????? ?????? ?????????????????? ',
                    'username': username,
                    'email': email,
                    'name': name,
                    're': True}
                )
        else:
            return render(request, 'study/sign/signup_sns.html', 
            {'form_error': '????????? ????????? ?????? ??????????????????',
            'email' : email})
    return render(request, 'study/sign/signup_sns.html',{
            'email' : email
        })
        


# BASE_DIR ?????? + secret.json
secret_file = os.path.join(settings.BASE_DIR, "secret.json")

with open(secret_file) as f:
    secret = json.load(f)


# ???????????? ?????? ???????????? -> callback_url return
def kakao_login(request):
    REST_API_KEY = secret['KAKAO_API_KEY']
    domain = str(get_current_site(request))
    REDIRECT_URI = "http://" + domain + "/kakao/callback"
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={REST_API_KEY}&redirect_uri={REDIRECT_URI}&response_type=code"
    )

def naver_login(request):
    REST_API_KEY = secret['NAVER_API_KEY']
    domain = str(get_current_site(request))
    REDIRECT_URI = "http://" + domain + "/naver/callback"
    return redirect(
        f"https://nid.naver.com/oauth2.0/authorize?client_id={REST_API_KEY}&redirect_uri={REDIRECT_URI}&response_type=code&state=ready"
    )


# callback ??? error ????????? ???????????? ?????? ?????????


def kakao_callback(request):
    try:
        request.GET['error']
        return redirect('index')
    except:
        # ?????? ????????????
        code = request.GET['code']
        REST_API_KEY = secret['KAKAO_API_KEY']
        domain = str(get_current_site(request))
        REDIRECT_URI = "http://" + domain + "/kakao/callback"

        data = {
            "grant_type": "authorization_code",
            "client_id": REST_API_KEY,
            "redirect_uri": REDIRECT_URI,
            "code": code,
        }

        token_request = requests.post(
            f"https://kauth.kakao.com/oauth/token",
            data=data
        )
        token_json = token_request.json()
        access_token = token_json.get("access_token")

        # ????????? ????????????

        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        data = {
            "property_keys": '["kakao_account.email"]'
        }

        email_response = requests.post(
            "https://kapi.kakao.com/v2/user/me",
            headers=headers,
            data=data
        )

        email_response_json = email_response.json()

    #     requests.post(
    #     f"https://kapi.kakao.com/v1/user/unlink",
    #     headers=headers
    # )

        email = email_response_json.get('kakao_account').get('email')
        
        user = User.objects.filter(email = email)

        #??????????????? ????????? ???????????? ????????? ???????????? ????????? ????????? ??? ????????? ?????????
        if user.exists() :
           
            login(request,user[0])
            return redirect('index')
        #????????? ??????
        else:
            hashed = bcrypt.hashpw(str(email).encode('utf-8'),bcrypt.gensalt()).decode('utf-8')
            
            return redirect(reverse('signup_sns') + f"?email={email}&hashed={hashed}")



def naver_callback(request):
    try:
        request.GET['error']
        return redirect('index')
    except:
        # ?????? ????????????
        code = request.GET['code']
        REST_API_KEY = secret['NAVER_API_KEY']
        SECRET_KEY = secret['NAVER_SECRET_KEY']
        domain = str(get_current_site(request))
        REDIRECT_URI = "http://" + domain + "/naver/callback"

        data = {
            "grant_type": "authorization_code",
            "client_id": REST_API_KEY,
            "code": code,
            "state":"ready",
            "client_secret": SECRET_KEY
        }

        token_request = requests.post(
            f"https://nid.naver.com/oauth2.0/token",
            data=data
        )
        token_json = token_request.json()
        access_token = token_json.get("access_token")


        # ????????? ????????????

        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        email_response = requests.post(
            "https://openapi.naver.com/v1/nid/me",
            headers=headers,
        )

        email_response_json = email_response.json()


    #     requests.post(
    #     f"https://kapi.kakao.com/v1/user/unlink",
    #     headers=headers
    # )

        email = email_response_json.get('response').get('email')
        
        user = User.objects.filter(email = email)

        #??????????????? ????????? ???????????? ????????? ???????????? ????????? ????????? ??? ????????? ?????????
        if user.exists() :
           
            login(request,user[0])
            return redirect('index')
        #????????? ??????
        else:
            hashed = bcrypt.hashpw(str(email).encode('utf-8'),bcrypt.gensalt()).decode('utf-8')
            
            return redirect(reverse('signup_sns') + f"?email={email}&hashed={hashed}")
        
            















# def signup(request): #????????????
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

#                 email = EmailMessage('????????? ?????? ???????????????',message,to=['ppm5377@naver.com'])
#                 email.send()
#                 # user = authenticate(username = username , password = password)
#                 # auth.login(request,user)
#                 return redirect('main')
#             else:
#                 form = Signup_form(initial ={'username':username}) #???????????? ??????????????????

#                 return render(request,'student/signup.html',{'form' : form})


#         else:
#             return render(request,'student/signup.html',{'form' : form})
#     else:
#         form = Signup_form()
#         return render(request,'student/signup.html',{'form' : form})


def checkemail(request):  # ???????????? ?????? ?????? ?????????
    return render(request, 'study/sign/checkemail.html')


def testError(request):  # ?????? ????????? ?????????
    return render(request, 'study/error.html')


# ????????? ??????????????? ?????? ???????????? ?????? dispatch ??? ????????? ?????? ??????
# name ??? ???????????? ???????????? ???????????? ???????????? ?????????????????? ??????????????????
# https://ssungkang.tistory.com/entry/Django-FBV-%EC%99%80-CBV-%EC%9D%98-decorators-%EC%82%AC%EC%9A%A9%EB%B2%95
@method_decorator(staff_member_required, name="dispatch")
class Img_update_view(generic.CreateView):
    model = Study_img
    fields = '__all__'
    template_name = 'study/uploadimg.html'
    success_url = "/uploadimg/"

    def get_context_data(self, **kwargs):
        kwargs["imgs"] = Study_img.objects.all()
        return super().get_context_data(**kwargs)


@staff_member_required(login_url='/')
def deleteimg(request, pk):
    img = Study_img.objects.get(pk=pk)
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )
    key = img.pic.name
    # ?????? ???????????? ????????? ???????????? ??????
    s3_client.delete_object(
        Bucket='elasticbeanstalk-ap-northeast-2-926096212919', Key='media/'+key)
    img.delete()
    return HttpResponse('????????????')


# Qna
@login_required(login_url="/user/login")
def test(request):
    if request.method == "POST":
        # ?????? ??????
        text = request.POST["text"]
        title = request.POST["title"]
        post = Qna(user=request.user, text=text, title=title)
        post.save()
    else:
        return render(request, "test/test.html")



def notice_list(request):
    page = int(request.GET['page'])
    notice = Notice.objects.all().order_by('-pk')
    page_len = notice.count()//11 + 1

    notice = notice[10*(page-1):10*page]
    num = [i+1 for i in range(10*(page-1),10*page)]
    notice = zip(notice,num)
    
    notice = render_to_string(
        'study/function/notice_list_base.html', context={"notices": notice})

    context = {
        "notice": notice,
        "page_len": page_len
    }
    context = json.dumps(context)
    return HttpResponse(context)


def notice_view(request,num):
    #????????? ?????????
    if not request.user.is_authenticated :
        return render(request,'study/function/notice_view.html', {"num": num})
    else :
        notice = Notice.objects.all()
        return render(request, 'study/function/notice_view.html', {"num": num,'notice' : notice})


@staff_member_required(login_url='/')
def notice_enroll(request):
    if request.method == 'POST':
        title = request.POST['title']
        content = request.POST['content']
        
        new_notice = Notice(title=title, content=content)
        new_notice.save()

        return redirect('notice_view',1)
    return render(request, 'study/function/notice_enroll.html')

@login_required(login_url='/user/login/')
def notice_detail(request,num):
    notice = Notice.objects.get(pk=num)

    if request.method == 'POST':
        notice.title = request.POST['title']
        notice.content = request.POST['content']
        notice.save()
    return render(request, 'study/function/notice_detail.html',{"notice" : notice})

@staff_member_required(login_url='/')
def notice_delete(request,pk):
    notice = Notice.objects.get(pk=pk)
    notice.delete()
    return redirect('notice_view', 1)