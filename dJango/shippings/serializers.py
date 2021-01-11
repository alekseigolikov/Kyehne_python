from rest_framework import serializers
from shippings.models import Shipping


class ShippingSerializer(serializers.ModelSerializer):
        class Meta:
            model = Shipping
            fields = ('id',
                      'creation_date',
                      'name',
                      'origin',
                      'destination',
                      'current_location',
                      'state')
            read_only_fields = ('id',)
