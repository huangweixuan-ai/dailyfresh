from django.db import models

# Create your models here.
from django.db import models


# Create your models here.
class OrderInfo(models.Model):
    oid = models.CharField(max_length=20, primary_key=True)  # 订单编号 主键
    user = models.ForeignKey('df_user.UserInfo',on_delete=models.CASCADE)  # 所属用户
    odate = models.DateTimeField(auto_now_add=True)  # 订单时间
    oIsPay = models.BooleanField(default=0)  # 订单支付状态
    ototal = models.DecimalField(max_digits=6, decimal_places=2)  # 金额
    oaddr = models.CharField(max_length=150)


class OrderDetailInfo(models.Model):
    goods = models.ForeignKey('df_goods.GoodsInfo',on_delete=models.CASCADE)  # 订单详情 订单商品
    order = models.ForeignKey(OrderInfo,on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    count = models.IntegerField()
