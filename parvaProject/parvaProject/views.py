# Create your views here.

from django.shortcuts import render

def index(self, *args, **kwargs):
    return render(self, 'index.html')
