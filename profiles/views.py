from django.shortcuts import render

# Create your views here.
from .forms import ProfileModelForm
from .models import Profile


def my_profile_view(request):
    profile = Profile.objects.get(user=request.user)
    form = ProfileModelForm(request.POST or None, request.FILES or None, instance=profile)
    # obj = Profile.objects.first()
    confirm = False
    if request.method == "POST":
        if form.is_valid():
            form.save()
            confirm = True

    context = {
        'profile': profile,
        'form': form,
        'confirm': confirm,
    }

    return render(request, 'profiles/myprofile.html', context)
