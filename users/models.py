from django.db import models

from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser, PermissionsMixin)
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse_lazy
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from decimal import Decimal as dc

from basket.models import Cart
from orders.models import Orders

class MyUserManager(BaseUserManager):
    def create_user(self, phone, name, password=None):
        if not phone:
            raise ValueError('Users must have an Phone')

        user = self.model(
            phone=phone,
            name=name
        )

        user.set_password(password)
        user.is_staff = False
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, name, password=None):
        user = self.create_user(
            phone=phone,
            name=name
        )
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=255)
    email = models.EmailField(_('email address'), unique=True, null=True, blank=True)
    phone_regex = RegexValidator(regex=r'^(\+\d{1,3})?,?\s?\d{10}', message="Phone number must be entered in the format: '+999999999'. Up to 10 digits allowed.")
    phone = models.DecimalField(validators=[phone_regex], max_digits=10, decimal_places=0, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, related_name='children')
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = MyUserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return '%s' % self.phone

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    def get_absolute_url(self):
        return reverse_lazy('detail_customer', kwargs={'pk': self.pk})

    def balance(self):
        return self.wallet.bal if hasattr(self, 'wallet') else 0

def create_cart(sender, instance, created, **kwargs):
    if created:
        c = Cart(user=instance)
        w = Wallet(user=instance)
        c.save()
        w.save()

post_save.connect(create_cart, sender=User)

def directory_path(instance, filename):
    return '{0}/{1}/{2}'.format(instance._meta.db_table.split('_')[1], instance.get_slug(), filename)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pic = models.ImageField(upload_to=directory_path)
    pan = models.CharField()
    adhar = models.CharField()

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bal = models.DecimalField(max_digits=12, decimal_places=4, verbose_name=_("Wallet Balance"), default=0)

    def __str__(self):
        return '{} -> {}'.format(self.user, self.bal)


# class WalletHistory(models.Model):
#     wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
#     order = models.ForeignKey(Orders, on_delete=models.CASCADE, null=True)
#     prev_bal = models.DecimalField(max_digits=12, decimal_places=4, verbose_name=_("Previous Balace"))
#     amount = models.DecimalField(max_digits=10, decimal_places=4, verbose_name=_("Amount Added"))
#     dt = models.DateTimeField(auto_now_add=True)
# 
#     unique_together = ['wallet', 'order']