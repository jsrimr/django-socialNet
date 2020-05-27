from django.shortcuts import render
from .models import Profile
# Create your views here.

def my_profile_view(request):
    # obj = Profile.objects.get(user=request.user)

    obj = Profile.objects.first()
    context = {
        'obj' : obj
    }

    return render(request, 'profiles/myprofile.html', context)