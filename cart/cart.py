from decimal import Decimal
from django.conf import settings
from shop.models import Product


class Cart:
    def __init__(self, request):
        '''
        初始化购物车
        :param request: 从其获取当前session
        '''
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # 在session中存储一个空的cart
            cart = self.session[settings.CART_SESSION_ID]={}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        '''
        给购物车增加一件商品，或者更新其数量
        :param product:
        :param quantity:
        :param update_quantity:
        :return:
        '''
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0,
                                     'price': str(product.price)}
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        # 标记session为修改过了，会自动保存
        self.session.modified = True

    def remove(self, product):
        '''
        从购物车移除一件商品
        :param product:
        :return:
        '''
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        '''
        遍历购物车中的商品，并且从数据库提取
        :return: 可迭代对象
        '''
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)

        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product']=product

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['quantity'] * item['price']
            yield item

    def __len__(self):
        '''
        给出购物车中商品总数量
        :return:
        '''
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()