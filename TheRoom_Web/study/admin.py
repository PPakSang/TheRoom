from django.contrib import admin
from .models import *

# Register your models here.


@admin.register(Student)
class Student_Admin(admin.ModelAdmin):

    search_fields = ['name']
    list_filter = ['lesson_day']
    list_display = ['name','number','lesson_day']



@admin.register(Qna)
class Faq_Admin(admin.ModelAdmin):
    pass


@admin.register(Study_img)
class Img_Admin(admin.ModelAdmin):
    pass



@admin.register(Room)
class Room_Admin(admin.ModelAdmin):
    pass