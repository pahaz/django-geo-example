from django.shortcuts import render, redirect


def home(request):
    if request.method == 'POST':
        return redirect('/')
    return render(request, 'home.html', {})
