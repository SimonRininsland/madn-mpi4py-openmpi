# Create your views here.

from django.shortcuts import render
from mpi4py import MPI

def index(self, *args, **kwargs):
    return render(self, 'index.html')
