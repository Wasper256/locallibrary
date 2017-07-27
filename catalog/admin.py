# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import Author, Genre, Book, BookInstance
from django.contrib import admin

# Register your models here.

admin.site.register(Book)
admin.site.register(Author)
admin.site.register(Genre)
admin.site.register(BookInstance)
