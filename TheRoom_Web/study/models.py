from time import time
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core import validators
from django.db import models
from django.db.models.base import Model
from django.core.validators import *
from django.shortcuts import redirect, render
import datetime
from django.utils import timezone
from django.conf import settings
import os
# Create your models here.


class Student(models.Model): 
    name = models.CharField(max_length=10,validators=[MinLengthValidator(2)],verbose_name='이름')
   
    number = models.CharField(max_length=11, validators=[MinLengthValidator(10)],verbose_name='전화번호')
    
    level_status = (('1','상담'),('2','보컬'),('3','악기'),('4','축가'))
    level = models.CharField(max_length=1,choices=level_status,blank=True,verbose_name='클래스')
    
    day1 = models.DateField(default=datetime.date.today(),verbose_name='방문 날짜')
    lesson_day = models.DateTimeField(default=datetime.datetime.today(),verbose_name='상담/레슨 날짜')
    

    deposit_status = (("1","미입금"),("2","예약금"),("3","완납"),)
    deposit = models.CharField(max_length=1,default='1',choices=deposit_status,verbose_name='입금여부')

    pay_way_status = (("0","미납"),("1","계좌"),("2","카드"),("3","현금"))
    pay_way = models.CharField(max_length=1,default='0',choices=pay_way_status,verbose_name='입금방식')
    

    user_id = models.IntegerField(default=0)

    check_status = (('1','미확인'),('2','확인'))
    check_in = models.CharField(default='1',choices=check_status,max_length=1,verbose_name='확인여부')
    comment = models.TextField(blank=True, null=True, verbose_name="참고사항")

    is_mailed = models.IntegerField(default = 0)
    

    def __str__(self) -> str:
        return self.name + f'({self.number[3:]})'

    def get_absolute_url(self):
        return redirect('detail',pk = self.id)



class Room(models.Model): 
    name = models.CharField(max_length=10,validators=[MinLengthValidator(2)],verbose_name='이름')
   
    number = models.CharField(max_length=11, validators=[MinLengthValidator(10)],verbose_name='전화번호')

    day1 = models.DateTimeField(default=datetime.datetime.today(),verbose_name='대여 시각')
    

    deposit_status = (("1","미입금"),("2","예약금"),("3","완납"),)
    deposit = models.CharField(max_length=1,default='1',choices=deposit_status,verbose_name='입금여부')

    pay_way_status = (("0","미납"),("1","계좌"),("2","카드"),("3","현금"))
    pay_way = models.CharField(max_length=1,default='0',choices=pay_way_status,verbose_name='입금방식')
    
    
    user_id = models.IntegerField(default=0)

    comment = models.TextField(blank=True, null=True, verbose_name="참고사항")


    def __str__(self) -> str:
        return self.name + f'({self.number[3:]})'

    def get_absolute_url(self):
        return redirect('detail',pk = self.id)




class Qna(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    text = models.TextField(max_length=1000)
    date = models.DateField(auto_now=True)


    
    #Qna 남기고나서 다음 Qna 는 10분뒤에 남길 수 있도록
    next_qna = models.DateTimeField()



    answer = models.TextField(blank=True)

    def __str__(self) -> str:
        return "유저 : "+self.user.username +"/제목 :"+ self.title

class Review(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    text = models.TextField(max_length=1000)
    date = models.DateField(auto_now=True)





    answer = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.user.username
        

class Study_img(models.Model):
    pic = models.ImageField(upload_to = 'studypic/')

    # def delete(self, *args, **kwargs):
    #     if self.pic :
    #         os.remove(os.path.join(settings.MEDIA_ROOT,self.pic.path))
    #         super(Study_img, self).delete(*args,**kwargs)