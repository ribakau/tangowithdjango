from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("Rango says 'Hello World!'<br/> <a href='/rango/about'>About</a>")


def about(request):
    return HttpResponse("This tutorial has been created by Mindaugas Ribakauskas, 2093693.</br><a href='/rango/'>Index</a>")
