from django.http import HttpResponse
from django.shortcuts import render, redirect

from . import redis
from .tasks import increase
from .models import Item


def home(request):
    if request.method == 'POST':
        Item.objects.create(text=request.POST['item_text'])
        return redirect('/')
    items = Item.objects.all()
    counter = redis.incr('counter')
    return render(request, 'home.html', {'items': items, 'counter': counter})


def async_incr_couter(request):
    value = int(request.GET.get('value', '3'))
    res = increase.delay(value)
    return HttpResponse(str(res.id))
