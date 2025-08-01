from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import generics


# Create your views here.
class TestAPIView(generics.GenericAPIView):
    def get(self, request):
        print(self.request.user)
        return JsonResponse({
            "code": 200,
            "msg": "success",
        })
