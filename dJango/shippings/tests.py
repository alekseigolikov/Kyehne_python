from django.test import TestCase

# Create your tests here.
from shippingapi import settings
from django.utils.http import urlencode
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from shippings.models import Shipping
from shippings import views
import json
from django.utils.encoding import force_text
from datetime import datetime

class ShippingTests(APITestCase):
    data = {'creation_date':datetime.utcnow().__str__(),
                'name':'TestShipping',
                'origin':'Tallinn',
                'destination':'Moscau',
                'current_location':'Narva',
                'state':'InTransit'}
                
    def resp_to_dir(self, response):
        response_text=force_text(response.content)
        dir = json.loads(response_text)
        return dir
    
    def make_url(self, param = None):
        url = reverse(views.shipping_list)
        if param is not None:
            url = url + '{0}'.format(param) + '/'
        return url

    def shipping_list_get(self, param = None):
        url = self.make_url(param)
        response = self.client.get(url, format='json')
        return response
        
    def shipping_list_post(self, data, param = None):
        url = self.make_url(param)
        response = self.client.post(url, data, format='json')
        return response

    def shipping_list_put(self, data, param = None):
        url = self.make_url(param)
        response = self.client.put(url, data, format='json')
        return response

    def shipping_list_del(self, param = None):
        url = self.make_url(param)
        response = self.client.delete(url, format='json')
        return response

    def test_get_list_all(self):
        response = self.shipping_list_get()
        assert response.status_code == status.HTTP_200_OK
        
    def test_post_new(self):
        response = self.shipping_list_post(self.data)
        dir_response = self.resp_to_dir(response)
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_get_detail_of_shipping_existant(self):
        response = self.shipping_list_post(self.data)
        assert response.status_code == status.HTTP_201_CREATED
        dir_response = self.resp_to_dir(response)
        id_created = dir_response['id']
        response = self.shipping_list_get(param = id_created)
        assert response.status_code == status.HTTP_200_OK
        dir_response = self.resp_to_dir(response)
        id_requested = dir_response['id']
        assert id_created == id_requested
    
    def test_get_detail_of_shipping_non_existant(self):
        response = self.shipping_list_get(404)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_shipping_existant(self):
        response = self.shipping_list_post(self.data)
        assert response.status_code == status.HTTP_201_CREATED
        dir_response = self.resp_to_dir(response)
        id_created = dir_response['id']
        response = self.shipping_list_get(param = id_created)
        assert response.status_code == status.HTTP_200_OK
        dir_response = self.resp_to_dir(response)
        id_requested = dir_response['id']
        assert id_created == id_requested
        response = self.shipping_list_del(param = id_created)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        response = self.shipping_list_get(param = id_created)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_shipping_non_existant(self):
        response = self.shipping_list_del(param = 404)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_shipping_existant(self):
        response = self.shipping_list_post(self.data)
        assert response.status_code == status.HTTP_201_CREATED
        dir_response = self.resp_to_dir(response)
        id_created = dir_response['id']
        new_data = self.data
        new_data['state'] = 'Delivered';
        response = self.shipping_list_put(data = new_data, param = id_created)
        assert response.status_code == status.HTTP_200_OK
        dir_response = self.resp_to_dir(response)
        id_requested = dir_response['id']
        assert id_created == id_requested
        assert dir_response['state']=='Delivered'

    def test_update_shipping_non_existant(self):
        response = self.shipping_list_put(data=self.data, param = 404)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
