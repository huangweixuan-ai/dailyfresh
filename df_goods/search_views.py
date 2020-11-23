from haystack.views import SearchView
from df_goods.models import *

class MySearchView(SearchView):
    def extra_context(self):
        context = super().extra_context()
        gnew = GoodsInfo.objects.order_by('-id')[0:2]
        context['gnew'] = gnew
        return context