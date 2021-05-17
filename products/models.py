from django.db import models
from autoslug import AutoSlugField
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy

from django.utils.safestring import mark_safe
from django.utils.html import escape

def directory_path(instance, filename):
    return '{0}/{1}/{2}'.format(instance._meta.db_table.split('_')[1], instance.get_slug(), filename)

class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='name')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True ,related_name='children')
    img = models.ImageField(upload_to=directory_path)
    dt = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
	        models.UniqueConstraint(fields=['slug', 'parent'], name="_(Can't create category same as parent)")
	    ]
        verbose_name_plural = "categories"

    def get_slug(self):
        return self.slug

    def __str__(self):
        return self.name

    def get_update_url(self):
        return reverse_lazy('update_category', kwargs={'pk': self.pk})

    def get_delete_url(self):
        return reverse_lazy('delete_categories"', kwargs={'pk': self.pk})

class Product(models.Model):
    name = models.CharField(max_length=255)
    title = AutoSlugField(populate_from='name')
    price = models.PositiveIntegerField(verbose_name=_("Selling Price"))
    is_public = models.BooleanField(_('Is public'), default=True, db_index=True, help_text=_("Show this product in search results and catalogue listings."))
    upc = models.CharField(verbose_name=_("UPC"), max_length=64, blank=True, null=True, unique=True, help_text=_("Universal Product Code (UPC) is an identifier for "
                    "a product which is not specific to a particular "
                    " supplier. Eg an ISBN for a book."))
    description = models.TextField(_('Description'), blank=True)
    categories = models.ManyToManyField('Category', verbose_name=_("Categories"))
    mrp = models.FloatField(verbose_name=_("Product MRP"))
    rating = models.FloatField(_('Rating'), null=True, editable=False)
    date_created = models.DateTimeField(
        _("Date created"), auto_now_add=True, db_index=True)
    date_updated = models.DateTimeField(
        _("Date updated"), auto_now=True, db_index=True)
    is_discountable = models.BooleanField(
        _("Is discountable?"), default=True, help_text=_(
            "This flag indicates if this product can be used in an offer "
            "or not"))

    def __str__(self):
        return '%s' % self.title

    @property
    def first_image(self):
        if self.images.all():
            return self.images.first().img.url

    def get_discount_url(self):
        return reverse_lazy('create_discount', kwargs={'pk': self.pk})

    def get_update_url(self):
        return reverse_lazy('update_products', kwargs={'pk': self.pk})

    def get_stock_url(self):
        if not hasattr(self, 'stockrecord'):
            return mark_safe('<a href="%s"><button class="btn btn-info btn-sm shadow-sm" style="background:#41cef1;border:none;"><span class="fa fa-plus"></span></button></a>' % escape(reverse_lazy('product_stock', kwargs={'pk': self.pk})))
        else:
            return mark_safe('<a href="%s"><button class="btn btn-light btn-sm shadow-sm"><span class="fa fa-pencil-alt"></span></button></a>' % escape(reverse_lazy('update_stock', kwargs={'pk': self.stockrecord.pk})))

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name=_("Product"))
    img = models.ImageField(upload_to=directory_path, max_length=255)
    caption = models.CharField(_("Caption"), max_length=200, blank=True)

    #: Use display_order to determine which is the "primary" image
    display_order = models.PositiveIntegerField(
        _("Display order"), default=0, db_index=True,
        help_text=_("An image with a display order of zero will be the primary"
                    " image for a product"))
    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)

    def get_slug(self):
        return self.product.title

    # def save(self, *args, **kwargs):
    #     instance = super(ProductImage, self).save(*args, **kwargs)
    #     image = Image.open(instance.img.path)
    #     image.save(instance.img.path, quality=20, optimize=True)
    #     return instance

class StockRecord(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    num_in_stock = models.PositiveIntegerField(
        _("Number in stock"))
    num_allocated = models.IntegerField(
        _("Number allocated"), default=0)
    low_stock_threshold = models.PositiveIntegerField(
        _("Low Stock Threshold"), blank=True, null=True)
    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)
    date_updated = models.DateTimeField(_("Date updated"), auto_now=True,
                                        db_index=True)

    def get_available(self, n):
        return (self.num_in_stock-self.num_allocated)>=n