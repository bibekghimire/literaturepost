from django.shortcuts import render

# Create your views here.

def home_view(request):
    return render(request, "literature_home.html")
def home(request):
    context={}
    userprofile=getattr(request.user,'userprofile',None)
    if userprofile:
        context={
        'uuid':userprofile.public_id, 
    }
    context['user']=request.user
    print(request.user)
    return render(request, 'home.html')