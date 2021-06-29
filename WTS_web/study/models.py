from time import time
from django.contrib.auth.backends import ModelBackend
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
    name = models.CharField(max_length=10,validators=[MinLengthValidator(2)])
   
    number = models.CharField(max_length=11, validators=[MinLengthValidator(10)])
    
    level_status = (('1','왕초급'),('2','초급'),('3','중급'))
    level = models.CharField(max_length=1,choices=level_status,blank=True)

    time_status = (('0','평일'),('1','주말1시'),('2','주말4시'))
    
    time1 = models.CharField(max_length=1,default='0',choices=time_status,blank=True, verbose_name='첫번째 참여시간')
    time2 = models.CharField(max_length=1,default='0',choices=time_status,blank=True, verbose_name='두번째 참여시간')
    time3 = models.CharField(max_length=1,default='0',choices=time_status,blank=True, verbose_name='세번째 참여시간')
    time4 = models.CharField(max_length=1,default='0',choices=time_status,blank=True, verbose_name='네번째 참여시간')
    
    base_date = models.DateField(default=datetime.date.today(),verbose_name='기준 주차')
    
    day1 = models.DateField(default=datetime.date.today(),verbose_name='첫번째 참여일')
    day2 = models.DateField(default=datetime.date.today(),verbose_name='두번째 참여일')
    day3 = models.DateField(default=datetime.date.today(),verbose_name='세번째 참여일')
    day4 = models.DateField(default=datetime.date.today(),verbose_name='네번째 참여일')
    plus_day = models.DateField(default=datetime.date.today() - datetime.timedelta(days=365),verbose_name='보너스 참여일')

    deposit_status = (("1","미입금"),("2","예약금"),("3","완납"),)
    deposit = models.CharField(max_length=1,default='1',choices=deposit_status)

    pay_way_status = (("0","미납"),("1","계좌"),("2","카드"),("3","현금"))
    pay_way = models.CharField(max_length=1,default='0',choices=pay_way_status)
    
    
    changed_day = models.DateField(default=datetime.date.today(),verbose_name='등록하기 한날')

    
    user_id = models.IntegerField(default=0)


    check_in = models.TextField(blank=True, null=True, verbose_name="출석체크")
    comment = models.TextField(blank=True, null=True, verbose_name="참고사항")

    is_mailed = models.IntegerField(default = 0)
    
    def __str__(self) -> str:
        return self.name + f'({self.number[3:]})'

    def get_absolute_url(self):
        return redirect('detail',pk = self.id)



class Faq(models.Model):
    name = models.CharField(max_length=10)
    answer_to = models.CharField(max_length=100)
    user_id = models.IntegerField(default=0)
    text = models.TextField()


    def __str__(self) -> str:
        return self.name + f'({self.answer_to})'
        

class Study_img(models.Model):
    pic = models.ImageField(upload_to = 'studypic/')

    # def delete(self, *args, **kwargs):
    #     if self.pic :
    #         os.remove(os.path.join(settings.MEDIA_ROOT,self.pic.path))
    #         super(Study_img, self).delete(*args,**kwargs)