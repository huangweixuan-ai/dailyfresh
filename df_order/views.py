import time
from django.shortcuts import render, redirect
from df_cart.models import CartInfo
from df_user.models import UserInfo, UserAddressInfo
from django.http import JsonResponse
from df_order.models import OrderInfo, OrderDetailInfo
import os
from alipay import AliPay
from django.conf import settings

from django.db import transaction

alipay = AliPay(
    appid=settings.ALIPAY_APPID,
    app_notify_url=None,
    app_private_key_path=os.path.join(settings.STATICFILES_DIRS[0], 'app_private_key.pem'),
    alipay_public_key_path=os.path.join(settings.STATICFILES_DIRS[0], 'alipay_public_key.pem'),
    sign_type='RSA',
    debug=True,
)


# Create your views here.
def index(request):
    cids = request.GET.getlist('cid')  # 得到购物车 页面提交的购物车 的id
    cart_list = CartInfo.objects.filter(id__in=cids)  # 找到所有的购物车对象
    uid = request.session.get('user_id')  # 当前登录的用户
    user = UserInfo.objects.get(id=uid)
    user_addr = user.useraddressinfo_set.all()
    print(user_addr)
    str1 = ''
    if user_addr:
        user_addr = user_addr[0]
        str1 = f'{user_addr.uaddress},({user_addr.uname})收,电话:{user_addr.uphone}'
    return render(request, 'df_order/place_order.html', {'title': '订单', 'clist': cart_list, 'info': str1})


@transaction.atomic
def do_order(request):
    # {'cid': cids,'pay_style': pay_style},
    pay_style = request.GET.get('pay_style')  # cash  zfb
    cids = request.GET.getlist('cid')  # 购物车的id
    uid = request.session.get('user_id')  # 用户id
    user = UserInfo.objects.get(id=uid)  # 用户

    # 开启事务
    sid = transaction.savepoint()  #
    # 创建订单
    order = OrderInfo()
    order.oid = str(int(time.time() * 1000)) + str(uid)  # 订单编号
    order.user_id = uid
    order.ototal = 0  # 订单金额

    order.oaddr = UserAddressInfo.objects.get(user=user).uaddress  # 订单地址
    #address = order.oaddr.objects.get("uaddress")
    order.save()
    cart_list = CartInfo.objects.filter(id__in=cids)  # 查找到所有购物车对象
    total_price = 0
    total_count = 0
    isOk = True
    for cart in cart_list:
        #
        if cart.count <= cart.goods.gkucun:
            # 库存充足
            detail = OrderDetailInfo()
            detail.order = order
            detail.goods = cart.goods
            detail.price = cart.goods.gprice
            detail.count = cart.count
            detail.save()

            # 更改库存
            cart.goods.gkucun -= cart.count
            cart.goods.save()

            # 计算总价
            total_price += detail.count * detail.price
            total_count += detail.count


            # 删除购物车对象
            cart.delete()
        else:
            # 库存不够
            isOk = False
            break



    if isOk:
        # 最终提交订单
        order.ototal = total_price
        # 订单成功
        if pay_style == 'cash':
            order.oIsPay = 1
            order.save()
            transaction.savepoint_commit(sid)  # 提交事务
            return JsonResponse({'res': 1})

        else:
            order_id = order.oid  # 订单编号
            # total_pay = order.ototal
            total_pay = order.ototal
            order_string = alipay.api_alipay_trade_page_pay(
                out_trade_no=order_id,
                total_amount=str(total_pay),
                subject=f'粤嵌科技{order_id}',
                return_url='http://127.0.0.1:8000/order/check_pay/?order_id=' + order_id,
                notify_url='http://127.0.0.1:8000/order/check_pay/?order_id=' + order_id,
            )
            alipay_url = settings.ALIPAY_URL + '?' + order_string
            return JsonResponse({'res': 3, 'pay_url': alipay_url})
    else:
        # 订单失败
        transaction.savepoint_rollback(sid)
        return JsonResponse({'res': 0})

def check_pay(request):
    order_id = request.GET.get('order_id')
    order = OrderInfo.objects.get(oid=order_id)
    while True:
        time.sleep(1)
        response = alipay.api_alipay_trade_query(order_id)  # 验证支付状态  response 是一个字典
        print(response)
        code = response.get('code')  # 支付宝调用成功或失败的标志
        trade_status = response.get('trade_status')  # 用户的支付情况
        if code == '10000' and trade_status == 'TRADE_SUCCESS':
            # 表示支付成功
            order.oIsPay = 1
            order.save()
            return redirect('info')
        elif code == '40004' or (code == '10000' and trade_status == 'WAIT_BUYER_PAY'):
            continue
        else:
            return JsonResponse({'code': '0', 'message': '支付失败'})
