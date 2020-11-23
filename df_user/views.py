from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404

from df_order.models import OrderInfo
from df_user.forms import UserForm
from hashlib import sha1
from df_user.models import UserInfo, UserAddressInfo
from django.http import JsonResponse, HttpResponseRedirect
from df_goods.models import *


def is_login(func):
    # 判断是否登录状态的装饰器
    def inner(request, *args, **kwargs):
        if request.session.get('user_id'):
            # 如果用户已登录
            return func(request, *args, **kwargs)
        else:
            # 如果没有登录 重定向到登录页面
            if request.is_ajax():
                return JsonResponse({'isLogin': 0})
            return redirect('login')

    return inner


# Create your views here.
def register(request):
    form = UserForm()
    return render(request, 'df_user/register.html', {'form': form})


def check_register(request):
    dict1 = request.POST
    upwd = dict1.get('upwd')
    form = UserForm(request.POST)

    if form.is_valid():
        user = form.save(commit=False)
        s1 = sha1()
        s1.update(upwd.encode())
        upwd = s1.hexdigest()  # 获取到加密后的密码
        user.upwd = upwd
        user.save()  # 注册成功
        return redirect('login')
    return render(request, 'df_user/register.html', {'form': form})


def user_check(request):
    uname = request.GET.get('uname')
    xxx = UserInfo.objects.filter(uname=uname).count()  # 根据用户名查找用户 个数
    return JsonResponse({'num': xxx})


def login(request):
    uname = request.COOKIES.get('uname')
    return render(request, 'df_user/login.html', {'title': '登录', 'error_name': 0, 'error_pwd': 0, 'uname': uname})


def login_check(request):
    dict1 = request.POST
    uname = dict1.get('username')
    upwd = dict1.get('pwd')
    jizhu = dict1.get('jizhu', 0)
    users = UserInfo.objects.filter(uname=uname)  # 根据用户名查找用户
    if users:
        s1 = sha1()
        s1.update(upwd.encode())
        if s1.hexdigest() == users[0].upwd:
            # 登录成功
            res = redirect('info')  # 跳转到用户中心
            if jizhu:
                # 如果点了记住用户名
                res.set_cookie('uname', uname)
            else:
                res.set_cookie('uname', uname, max_age=-1)  # 到浏览器关闭
            request.session['user_id'] = users[0].id
            request.session['user_name'] = uname
            return res
        else:
            # 密码不对
            context = {'title': '登录', 'error_name': 0, 'error_pwd': 1, 'uname': uname}
            return render(request, 'df_user/login.html', context)
    else:
        # 没有找到用户
        context = {'title': '登录', 'error_name': 1, 'error_pwd': 0, 'uname': uname}
        return render(request, 'df_user/login.html', context)


@is_login
def info(request):
    id = request.session.get('user_id')
    user = UserInfo.objects.get(id=id)
    user_addr = UserAddressInfo.objects.filter(user=user)
    if  user_addr:
        user_addr=user_addr[0]
    # user_addr = get_object_or_404(UserAddressInfo, user_id=user.id)

    # 最近浏览
    jin = request.COOKIES.get('jin', '[]')
    jin_list = eval(jin)
    # [30, 29, 10]
    goods = [GoodsInfo.objects.get(pk=id) for id in jin_list]

    return render(request, 'df_user/user_center_info.html', {'title': '用户中心', 'goods': goods, 'user_addr': user_addr})


@is_login
def site(request):
    id = request.session.get('user_id')
    print('--------------------------------')
    print(id)
    user = UserInfo.objects.get(id=id)
    user_addr = user.useraddressinfo_set.all()
    str1 = ''
    if user_addr:
        user_addr = user_addr[0]
        print(user_addr)
        str1 = f'{user_addr.uaddress},({user_addr.uname})收,电话:{user_addr.uphone}'
    return render(request, 'df_user/user_center_site.html', {'str1': str1})

@is_login
def center(request):
    id = request.session.get('user_id')  #当前用户
    myorders = OrderInfo.objects.filter(user_id=id)

    p = Paginator(myorders, 10)  # 一页多少个
    page_num = request.GET.get('page', 1)
    now_page = int(page_num)  # 当前页
    page = p.page(now_page)  # 获取当前页
    page_range = list(range(max(now_page - 2, 1), now_page)) + list(range(now_page, min(p.num_pages, now_page + 2) + 1))
    # 当页码间隔大于2时 显示省略号
    if page_range[0] - 1 > 2:
        page_range.insert(0, '...')
    if p.num_pages - page_range[-1] > 2:
        page_range.append('...')
    # 显示第一页和最后一页
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != p.num_pages:
        page_range.append(p.num_pages)

    content = {'page': page, 'page_range': page_range, 'title': '全部订单'}

    # return render(request,'user/user_center_order.html',{'title':'全部订单','myorders':myorders})

    return render(request, 'df_user/user_center_order.html', content)

def shou_save(request):
    dict1 = request.POST
    ushou = dict1.get('shou')
    uaddr = dict1.get('addr')
    ucode = dict1.get('ucode')
    uphone = dict1.get('uphone')
    id = request.session.get('user_id')
    user = UserInfo.objects.get(id=id)
    u_addr = UserAddressInfo()
    u_addr.uname = ushou
    u_addr.uaddress = uaddr
    u_addr.uphone = uphone
    u_addr.user = user
    u_addr.save()
    return redirect('site')

def logout(request):
    request.session.flush() #清空seeion缓存
    return HttpResponseRedirect('/user/login')
