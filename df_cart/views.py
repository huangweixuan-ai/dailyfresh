from django.shortcuts import render
from df_user.views import is_login
from df_user.models import UserInfo
from df_cart.models import CartInfo
from django.db.models import Sum
from django.http import JsonResponse


# Create your views here.
@is_login
def index(request):
    uid = request.session.get('user_id')
    cart_list = CartInfo.objects.filter(user_id=uid)
    return render(request, 'df_cart/cart.html', {'clist': cart_list, 'title': '购物车'})


@is_login
def add(request):
    uid = request.session.get('user_id')  # 用户的id
    dict1 = request.GET
    gid = dict1.get('gid')  # 商品的id
    count = int(dict1.get('count'))  # 数量
    # 判断当前商品是否已经在该用户购物车中
    carts = CartInfo.objects.filter(user_id=uid, goods_id=gid)
    if carts:
        cart = carts[0]
        cart.count += count
        cart.save()
    else:
        cart = CartInfo()
        cart.user_id = uid
        cart.goods_id = gid
        cart.count = count
        cart.save()
    # 统计当前用户购物车商品数量
    c = CartInfo.objects.filter(user_id=uid).aggregate(Sum('count'))
    return JsonResponse({'ok': 1, 'count': c.get('count__sum')})


def count1(request):
    # 单独负责统计数量
    c = CartInfo.objects.filter(user_id=request.session.get('user_id')).aggregate(Sum('count'))
    return JsonResponse({'count': c.get('count__sum')})


def edit(request):
    dict1 = request.GET
    cid = dict1.get('cid')
    count = dict1.get('count')
    cart = CartInfo.objects.get(id=cid)
    cart.count = count
    cart.save()
    return JsonResponse({'ok': 1})


def remove(request):
    dict1 = request.GET
    cid = dict1.get('cid')
    cart = CartInfo.objects.get(id=cid)
    cart.delete()
    return JsonResponse({'ok': 1})
