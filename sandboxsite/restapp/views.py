from django.contrib.auth.models import User
#from django.views.decorators.http import condition
from rest_framework.decorators import api_view
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import permissions
from rest_framework.exceptions import ConfigurationError
import warnings
#from restapp.models import Store
from restapp.models import Product, Checkin
from restapp.serializers import UserSerializer, StoreSerializer, ProductSerializer, CheckinSerializer
from restapp.serializers import CustomCheckinSerializer, CustomCheckinPaginationSerializer
from restapp.permissions import IsOwnerOrReadOnly
import storerepository
import sandboxsite

@api_view(('GET',))
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'stores': reverse('store-list', request=request, format=format),
        'products': reverse('product-list', request=request, format=format),
        'checkin': reverse('checkin-list', request=request, format=format)
    })


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# change by generic
class StoreList(generics.ListCreateAPIView):
    #queryset = Store.objects.all()
    serializer_class = StoreSerializer
    paginate_by = None

    def get_queryset(self):
        store_repository = storerepository.StoreRepository(sandboxsite.settings.MONGO_DB)
        criteria = {}
        stores = store_repository.find_stores_by_criteria(criteria)
        return stores

class StoreDetail(generics.RetrieveUpdateDestroyAPIView):
    #queryset = Store.objects.all()
    serializer_class = StoreSerializer

    def get_queryset(self):
        store_repository = storerepository.StoreRepository(sandboxsite.settings.MONGO_DB)
        storeid = self.kwargs.get(self.lookup_field,'')
        store = store_repository.find_store_by_id(storeid)
        return store

    def get_object(self, queryset=None):
        """
        Returns the object the view is displaying.

        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        # Determine the base queryset to use.
        if queryset is None:
            queryset = self.filter_queryset(self.get_queryset())
        else:
            pass  # Deprecation warning

        # Perform the lookup filtering.
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        slug = self.kwargs.get(self.slug_url_kwarg, None)
        lookup = self.kwargs.get(self.lookup_field, None)

        if lookup is not None:
            filter_kwargs = {self.lookup_field: lookup}
        elif pk is not None and self.lookup_field == 'pk':
            warnings.warn(
                'The `pk_url_kwarg` attribute is due to be deprecated. '
                'Use the `lookup_field` attribute instead',
                PendingDeprecationWarning
            )
            filter_kwargs = {'pk': pk}
        elif slug is not None and self.lookup_field == 'pk':
            warnings.warn(
                'The `slug_url_kwarg` attribute is due to be deprecated. '
                'Use the `lookup_field` attribute instead',
                PendingDeprecationWarning
            )
            filter_kwargs = {self.slug_field: slug}
        else:
            raise ConfigurationError(
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, self.lookup_field)
            )

        # This is used to get object using django models
        #obj = get_object_or_404(queryset, **filter_kwargs)

        #store_repository = storerepository.StoreRepository(sandboxsite.settings.MONGO_DB)
        # We may use a generic function building filter-kwargs
        #tmp_obj = store_repository.find_store_by_id(lookup)
        #obj = Store(id=tmp_obj['_id'], name=tmp_obj['name'], address=tmp_obj['address'])
        obj = queryset

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def save_object(self, obj, **kwargs):
        pass

class ProductList(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    # pasted here to debug
    def retrieve(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(self.object)
        data = serializer.data
        return Response(data)


class CheckinList(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Checkin.objects.all()
    #serializer_class = CheckinSerializer
    serializer_class = CustomCheckinSerializer
    # pagination serializer is used when pagination is enabled globally or per view
    #paginate_by = None
    pagination_serializer_class = CustomCheckinPaginationSerializer
    filter_fields = ('store', 'product')

    def pre_save(self, obj):
        obj.owner = self.request.user

def calc_etag():
    return 'luciano'

#@condition(etag_func=calc_etag, last_modified_func=None)
class CheckinDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsOwnerOrReadOnly,)
    queryset = Checkin.objects.all()
    serializer_class = CheckinSerializer

    def pre_save(self, obj):
        obj.owner = self.request.user
