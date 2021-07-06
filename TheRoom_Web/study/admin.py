from django.contrib import admin
from .models import *

# Register your models here.


@admin.register(Student)
class Student_Admin(admin.ModelAdmin):

    search_fields = ['name']



@admin.register(Qna)
class Faq_Admin(admin.ModelAdmin):
    pass


@admin.register(Study_img)
class Img_Admin(admin.ModelAdmin):
    pass