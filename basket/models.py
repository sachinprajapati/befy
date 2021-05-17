from django.db import models
from django.db.models import Model
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from products.models import Product

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

class CartLine(models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE, related_name='lines', verbose_name=_("Basket"))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_lines', verbose_name=_("Product"))
    quantity = models.PositiveIntegerField(_('Quantity'), default=1)
    price = models.FloatField(blank=True)
    discount = models.FloatField(default=0)
    date_created = models.DateTimeField(_("Date Created"), auto_now_add=True, db_index=True)
    date_updated = models.DateTimeField(_("Date Updated"), auto_now=True, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['cart', 'product'], name="_(This proudct already exists in cart)")
        ]

    def save(self, *args, **kwargs):
        self.price = self.product.price*self.quantity
        super(CartLine, self).save(*args, **kwargs)

class WishList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    dt = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']
