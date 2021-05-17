# Generated by Django 3.2.3 on 2021-05-15 14:46

import autoslug.fields
from django.db import migrations, models
import django.db.models.deletion
import products.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('slug', autoslug.fields.AutoSlugField(editable=False, populate_from='name')),
                ('img', models.ImageField(upload_to=products.models.directory_path)),
                ('dt', models.DateTimeField(auto_now_add=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='products.category')),
            ],
            options={
                'verbose_name_plural': 'categories',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('title', autoslug.fields.AutoSlugField(editable=False, populate_from='name')),
                ('price', models.PositiveIntegerField(verbose_name='Selling Price')),
                ('is_public', models.BooleanField(db_index=True, default=True, help_text='Show this product in search results and catalogue listings.', verbose_name='Is public')),
                ('upc', models.CharField(blank=True, help_text='Universal Product Code (UPC) is an identifier for a product which is not specific to a particular  supplier. Eg an ISBN for a book.', max_length=64, null=True, unique=True, verbose_name='UPC')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('mrp', models.FloatField(verbose_name='Product MRP')),
                ('rating', models.FloatField(editable=False, null=True, verbose_name='Rating')),
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Date created')),
                ('date_updated', models.DateTimeField(auto_now=True, db_index=True, verbose_name='Date updated')),
                ('is_discountable', models.BooleanField(default=True, help_text='This flag indicates if this product can be used in an offer or not', verbose_name='Is discountable?')),
                ('categories', models.ManyToManyField(to='products.Category', verbose_name='Categories')),
            ],
        ),
        migrations.CreateModel(
            name='StockRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num_in_stock', models.PositiveIntegerField(verbose_name='Number in stock')),
                ('num_allocated', models.IntegerField(default=0, verbose_name='Number allocated')),
                ('low_stock_threshold', models.PositiveIntegerField(blank=True, null=True, verbose_name='Low Stock Threshold')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date created')),
                ('date_updated', models.DateTimeField(auto_now=True, db_index=True, verbose_name='Date updated')),
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='products.product')),
            ],
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('img', models.ImageField(max_length=255, upload_to=products.models.directory_path)),
                ('caption', models.CharField(blank=True, max_length=200, verbose_name='Caption')),
                ('display_order', models.PositiveIntegerField(db_index=True, default=0, help_text='An image with a display order of zero will be the primary image for a product', verbose_name='Display order')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date created')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='products.product', verbose_name='Product')),
            ],
        ),
        migrations.AddConstraint(
            model_name='category',
            constraint=models.UniqueConstraint(fields=('slug', 'parent'), name="_(Can't create category same as parent)"),
        ),
    ]