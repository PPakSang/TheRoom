from django.contrib import admin
from .models import *

# Register your models here.


@admin.register(Student)
class Student_Admin(admin.ModelAdmin):
    list_display = ['__str__','day1','day2','day3','day4']
    list_filter = ['day1','day2']
    search_fields = ['name']



@admin.register(Faq)
class Faq_Admin(admin.ModelAdmin):
    pass


@admin.register(Study_img)
class Img_Admin(admin.ModelAdmin):
    pass