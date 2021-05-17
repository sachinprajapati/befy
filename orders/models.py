from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator
from django.urls import reverse_lazy

from django.conf import settings
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import connection

from products.models import Product

ADDRESS_TYE = [
    (1, 'Home'),
    (2, 'Office')
]

def db_table_exists(table, cursor=None):
    try:
        table_names = connection.introspection.get_table_list(cursor)
    except Exception as e:
        print(e)
    else:
        return table._meta.db_table in [t.name for t in table_names]

class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, verbose_name=_("Full Name"))
    phone_regex = RegexValidator(regex=r'^(\+\d{1,3})?,?\s?\d{10}',
                                 message="Phone number must be entered in the format: '+999999999'. Up to 10 digits allowed.")
    phone = models.DecimalField(validators=[phone_regex], max_digits=10, decimal_places=0)
    pin_regex = RegexValidator(regex=r'^(\+\d{1,3})?,?\s?\d{6}', message="Pincode number must be 6 digits long.")
    pincode = models.PositiveIntegerField(validators=[pin_regex])
    house = models.CharField(max_length=255, verbose_name=_("Flat, House no., Building"))
    area = models.CharField(max_length=255, verbose_name=_("Area, Street, Village"))
    city = models.CharField(max_length=55)
    state = models.CharField(max_length=40)
    type = models.PositiveSmallIntegerField(choices=ADDRESS_TYE)
    desc = models.TextField(verbose_name=_("Address Description"), blank=True, null=True)

    def get_address(self):
        return "<p>phone\t:-\t%s<br/>%s, %s, %s, %s, %s<br/>Type\t:-\t%s<br/></p>" \
               % (self.phone, self.house, self.area, self.city, self.state, self.pincode, self.get_type_display())

ORDER_STATUS = [
    (0, 'Pending'),
    (1, 'Confirmed'),
    (2, 'Processing'),
    (3, 'Shipped'),
    (4, 'Delivered'),
    (5, 'Rejected'),
    (6, 'Canceled'),
]

def Order_ID():
    now = timezone.localtime()
    return now.strftime('%Y%m%d%H%M%S%f')

class Orders(models.Model):
    # order_id = models.CharField(max_length=20, unique=True, default=Order_ID)
    amount = models.IntegerField()
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    expected_dt = models.DateField(null=True, verbose_name="Expected Delivery Date")
    dt = models.DateTimeField(auto_now_add=True)

    @property
    def get_payment_type(self):
        return self.orderpayment.type

    def product_count(self):
        return self.orderitems_set.all().count()

    def order_id(self):
        return self.id

    def quantities(self):
        quantities = self.orderitems_set.all().values_list('quantity', flat=True)
        total = sum(quantities)
        return total

    @property
    def get_CurrentStatus(self):
        return self.orderstatus_set.all().order_by('-status')[0].get_status_display()

    def get_Status(self):
        return self.orderstatus_set.all().order_by('-status')[0].status

    def get_absolute_url(self):
        return reverse_lazy('detail_orders', kwargs={'pk': self.pk})

    @property
    def sorted_status(self):
        return self.orderstatus_set.all().order_by('status')

    def update_wallet(self):
        self.customer.make_commision(self.amount, self)

class OrderItems(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=1)
    price = models.PositiveSmallIntegerField()

@receiver(post_save, sender=Orders)
def place_order(sender, instance, created, **kwargs):
    if created:
        cart_item = instance.customer.cart.lines.all()
        l = []
        for i in cart_item:
            l.append(OrderItems(order=instance, product=i.product, quantity=i.quantity, price=i.price))
            i.product.stockrecord.num_allocated += 1
            i.product.stockrecord.save()
            os = OrderStatus(order=instance)
            os.save()
        OrderItems.objects.bulk_create(l)
        cart_item.delete()

PAYMENT_TYPE = [
    (1, 'COD'),
    (2, 'Online'),
]

class OrderPayment(models.Model):
    order = models.OneToOneField(Orders, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    type = models.PositiveIntegerField(choices=PAYMENT_TYPE)
    tid = models.CharField(max_length=255, null=True)
    dt = models.DateTimeField(auto_now_add=True)

class OrderStatus(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    status = models.IntegerField(choices=ORDER_STATUS, default=0, verbose_name=_("Order Status"))
    dt  = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('order', 'status',)

    def __str__(self):
        return 'order {} status {}'.format(self.order, self.get_status_display())

    def StatusWith(status):
        cursor = connection.cursor()
        if db_table_exists(OrderStatus, cursor):
            cursor.execute("""select order_id from orders_orderstatus group by order_id having max(status)=%s;""" % status)
            return cursor.fetchall()
        return []

@receiver(post_save, sender=OrderStatus)
def Commision(sender, instance, created, **kwargs):
    if created and instance.status == 4:
        for p in instance.order.orderitems_set.all():
            p.product.stockrecord.num_in_stock -= p.quantity
            p.product.stockrecord.save()
        instance.order.update_wallet()



