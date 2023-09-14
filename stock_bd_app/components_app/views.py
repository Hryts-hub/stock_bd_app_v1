from django.shortcuts import render
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from components_app.models import StockComponents#, StockFromExcel
from components_app.serializers import StockComponentsSerializer#, StockFromExcelSerializer

from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import OrderingFilter, SearchFilter
from datetime import datetime


# Create your views here.

class MyPaginator(PageNumberPagination):
    page_size = 5


class ListCreateStockComponentsView(ListCreateAPIView):
    # authentication_classes = [TokenAuthentication]
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = StockComponentsSerializer

    # this code for testing with SessionAuthentication
    pagination_class = MyPaginator
    filter_backends = [OrderingFilter, SearchFilter]
    search_fields = ["art_number", "category", "type", "subtype", "component_stock_naming"]
    queryset = StockComponents.objects.all().order_by("art_number")

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            component = serializer.save(user=request.user)

            return Response(
                serializer.validated_data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.error_messages,
            status=status.HTTP_400_BAD_REQUEST
        )


# class ListCreateStockFromExcelView(ListCreateAPIView):
#     # authentication_classes = [TokenAuthentication]
#     authentication_classes = [SessionAuthentication]
#     permission_classes = [IsAuthenticated]
#     serializer_class = StockFromExcelSerializer
#
#     # this code for testing with SessionAuthentication
#     pagination_class = MyPaginator
#     filter_backends = [OrderingFilter, SearchFilter]
#     search_fields = ["art_number", "category", "type", "subtype", "component_stock_naming"]
#     queryset = StockComponents.objects.all().order_by("art_number")
#
#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             # component = serializer.save(user=request.user)
#
#             return Response(
#                 serializer.validated_data,
#                 status=status.HTTP_201_CREATED
#             )
#         return Response(
#             serializer.error_messages,
#             status=status.HTTP_400_BAD_REQUEST
#         )

