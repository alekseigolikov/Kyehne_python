from django.shortcuts import render
from rest_framework import status
from shippings.models import Shipping
from shippings.serializers import ShippingSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response

"""Shiping Listing(GET) and Shipping Creation(POST)"""
@api_view(['GET', 'POST'])
def shipping_list(request):
    if request.method == 'GET':
        shippings = Shipping.objects.all()
        shippings_serializer = ShippingSerializer(shippings, many=True)
        return Response(shippings_serializer.data)
    elif request.method == 'POST':
        shipping_serializer = ShippingSerializer(data=request.data)
        if shipping_serializer.is_valid():
            shipping_serializer.save()
            return Response(shipping_serializer.data,
                status=status.HTTP_201_CREATED)
        return Response(shipping_serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)


"""Shiping Details(GET), Shipping Update(PUT), Shipping Delete(DELETE)"""
@api_view(['GET', 'PUT', 'DELETE'])
def shipping_detail(request, pk):
    try:
        shipping = Shipping.objects.get(pk=pk)
    except Shipping.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        shipping_serializer = ShippingSerializer(shipping)
        return Response(shipping_serializer.data)
    elif request.method == 'PUT':
        shipping_serializer = ShippingSerializer(shipping, data=request.data)
        if shipping_serializer.is_valid():
            shipping_serializer.save()
            return Response(shipping_serializer.data)
        return Response(shipping_serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        shipping.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
