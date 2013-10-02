from rest_framework import serializers
from rest_framework import pagination
from restapp.models import Store, Product, Checkin
from restapp.models import ExternalStore
from django.contrib.auth.models import User
import storerepository
import sandboxsite

class StoreSerializer(serializers.Serializer):
    #pk = serializers.Field()  # Note: `Field` is an untyped read-only field.
    url = serializers.HyperlinkedIdentityField(view_name = 'store-detail')
    name = serializers.CharField(required=False, max_length=100)
    address = serializers.CharField(required=False, max_length=100)
    
    def restore_object(self, attrs, instance=None):
        instance = ExternalStore(attrs)
        instance.name = attrs.get('name', instance.name)
        instance.address = attrs.get('address', instance.address)
        return instance

    def save_object(self, obj, **kwargs):
        store_repository = storerepository.StoreRepository(sandboxsite.settings.MONGO_DB)
        new_id = store_repository.add_store(obj)
        obj.pk = new_id
        pass

class StoreSerializer2(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Store
        #fields = ('id', 'name', 'address')


class ProductSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Product
        #fields = ('id', 'name')

class CheckinSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Checkin
        #fields = ('created', 'store', 'product', 'price')

class UserSerializer(serializers.ModelSerializer):
    #checkins = serializers.PrimaryKeyRelatedField(many=True)
    checkins = CheckinSerializer(many=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'checkins')

# Custom serializer that implements partial response and change response format
class CustomCheckinSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Checkin


    def to_native(self, obj):
        """
        Serialize objects -> primitives.
        """
        ret = self._dict_class()
        ret.fields = {}

        query_fields = self.context['request'].QUERY_PARAMS.get('fields')
        if query_fields:
            desired_fields = query_fields.split(',')
        else:
            desired_fields = []

        for field_name, field in self.fields.items():
            if query_fields != None and field_name not in desired_fields:
                continue
            field.initialize(parent=self, field_name=field_name)
            key = self.get_field_key(field_name)
            value = field.field_to_native(obj, field_name)
            ret[key] = value
            ret.fields[key] = field
        return ret

    @property
    def data(self):

        obj2 = super(serializers.ModelSerializer, self).data
        obj = {'checkins': obj2}
        return obj

# Custom pagination serializer that changes count by total an result_field name
class CustomCheckinPaginationSerializer(pagination.BasePaginationSerializer):
    total = serializers.Field(source='paginator.count')
    next = pagination.NextPageField(source='*')
    previous = pagination.PreviousPageField(source='*')
    results_field = 'checkins'
