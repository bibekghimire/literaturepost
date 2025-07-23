from django.shortcuts import render

# Create your views here.

def home_view(request):
    return render(request, "literature_home.html")
def home(request):
    return render(request, 'home.html')