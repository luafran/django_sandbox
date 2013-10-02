from django.db import models

class ExternalStore(object):
    def __init__(self, store):
        self.raw_obj = store
        self.pk = str(store.get('_id'))
        self.name = store.get('name')
        self.address = store.get('address')

class Store(models.Model):
    name = models.CharField(max_length=150)
    address = models.CharField(max_length=150)

class Product(models.Model):
    name = models.CharField(max_length=150)

class Checkin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    store = models.ForeignKey(Store)
    product = models.ForeignKey(Product)
    price = models.CharField(max_length=50)
    owner = models.ForeignKey('auth.User', related_name='checkins')

    class Meta:
        ordering = ('created',)
