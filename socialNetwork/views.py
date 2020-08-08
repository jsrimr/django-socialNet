from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect


def home_view(request):
    user = request.user
    hello = 'Hello world'

    context = {
        'user': user,
        'hello': hello
    }

    return render(request, 'main/home.html', context)


def login_view(request):
    form = AuthenticationForm()
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            if request.GET.get('next'):
                return redirect(request.GET.get(('next')))
            else:
                return redirect('home-view')

    return render(request, 'main/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home-view')
