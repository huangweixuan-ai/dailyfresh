from django.shortcuts import render, get_object_or_404
from df_goods.models import *


# Create your views here.
def index(request):
    type_list = TypeInfo.objects.all()
    list1 = []
    for type_info in type_list:
        new = type_info.goodsinfo_set.order_by('-id')[0:4]
        fire = type_info.goodsinfo_set.order_by('-gclick')[0:3]
        list1.append({'type': type_info, 'new': new, 'fire': fire})
    return render(request, 'index.html', {'title': '首页', 'isCart': 1, 'list1': list1})


from django.core.paginator import Paginator


def goods_list(request, id, page_num, ord):
    # goods = GoodsInfo.objects.filter(gtype_id=id)  # 查找当前分类中所有商品
    type_info = TypeInfo.objects.get(id=id)  # 当前分类
    gnew = type_info.goodsinfo_set.order_by('-id')[0:2]  # 新品推荐
    # 按照规则排序
    order = '-id'
    if ord == '1':
        order = '-gprice'
    elif ord == '2':
        order = '-gclick'
    goods = type_info.goodsinfo_set.order_by(order)  # 按照对应的方式获取商品并按照传入的参数排序
    p = Paginator(goods, 10)
    page = p.page(int(page_num))

    context = {'title': '列表', 'isCart': 1, 'goods': goods, 'type': type_info, 'gnew': gnew, 'page': page, 'ord': ord}
    return render(request, 'df_goods/list.html', context)


def goods_detail(request, id):
    g = get_object_or_404(GoodsInfo, id=id)
    gnew = g.gtype.goodsinfo_set.order_by('-id')[0:2]
    g.gclick += 1
    g.save()  # 商品点击量+1
    res = render(request, 'df_goods/detail.html', {'title': '商品详情', 'isCart': 1, 'g': g, 'gnew': gnew})
    jin = request.COOKIES.get('jin', '[]')
    jin_list = eval(jin)
    if jin:
        jin_list.insert(0, id)
        if len(jin_list) > 5:
            jin_list.pop()
    res.set_cookie('jin', str(jin_list))
    return res
