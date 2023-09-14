from django.urls import path

from components_app.views import ListCreateStockComponentsView#, ListCreateStockFromExcelView

urlpatterns = [
    path("list_create_component/", ListCreateStockComponentsView.as_view(), name='list_create_component'),
    # path(
    #     "list_create_component_from_excel/",
    #     ListCreateStockFromExcelView.as_view(),
    #     name='list_create_component_from_excel'
    # ),

]