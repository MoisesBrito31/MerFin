from django.shortcuts import render
from django.views.generic import View
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from .serializer import OsSerializer, EstadoSerializer
from .models import OS, Estado
from time import sleep
import json


class indexView(View):
    def get(self,request):
        return render(request,"index.html")
    
def index404(request,erro):
    return render(request,"index.html")

def index500(request):
    return render(request,"index.html")

class OsList(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        queryset = OS.objects.all()
        serial = OsSerializer(queryset,many=True)
        return Response(serial.data)
    def post(self,request):
        try:
            nome = request.data['name']
            desc = request.data['description']
            st_id = int(request.data['state'])
            st = Estado.objects.get(id=st_id)
            OS.objects.create(name=nome,description=desc,state=st)
            return Response('ok', status=status.HTTP_201_CREATED)
        except Exception as EX:
            return Response(str(EX), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OsDetail(APIView):  
    permission_classes=[IsAuthenticated]
    def get(self,request,pk):
        try:
            obj = OS.objects.get(id=pk)
            serial = OsSerializer(obj)
            return Response(serial.data)
        except Exception as EX:
            return Response(str(EX),status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def post(self,request,pk):
        try:
            obj = OS.objects.get(id=pk)
            obj.name = request.data['name']
            obj.description = request.data['description']
            st_id = int(request.data['state'])
            obj.state = Estado.objects.get(id=st_id)
            obj.save()
            return Response('ok', status=status.HTTP_201_CREATED)
        except Exception as EX:        
            return Response(str(EX), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def delete(self, request, pk):
        try:
            obj = OS.objects.get(id=pk)
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as EX:
            return Response(str(EX),status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class EstadoList(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        queryset = Estado.objects.all()
        serial = EstadoSerializer(queryset,many=True)
        return Response(serial.data)
    def post(self,request):
        serial = EstadoSerializer(data=request.data)
        if serial.is_valid():
            serial.save()
            return Response(serial.data, status=status.HTTP_201_CREATED)
        return Response(serial.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EstadoDetail(APIView):  
    permission_classes=[IsAuthenticated]
    def get(self,request,pk):
        try:
            obj = Estado.objects.get(id=pk)
            serial = EstadoSerializer(obj)
            return Response(serial.data)
        except Exception as EX:
            return Response(str(EX),status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def post(self,request,pk):
        obj = Estado.objects.get(id=pk)
        serial = EstadoSerializer(obj,data=request.data)
        if serial.is_valid():
            serial.save()
            return Response(serial.data, status=status.HTTP_201_CREATED)
        return Response(serial.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def delete(self, request, pk):
        try:
            obj = Estado.objects.get(id=pk)
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as EX:
            return Response(str(EX),status=status.HTTP_500_INTERNAL_SERVER_ERROR)
