from rest_framework.serializers import ModelSerializer
from auth_app.models import CustomUser
from components_app.models import StockComponents, StockFromExcel


class UserSerializer(ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['username']
        # fields = '__all__'


class StockComponentsSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = StockComponents
        fields = '__all__'


# class StockFromExcelSerializer(ModelSerializer):
#     # user = UserSerializer(read_only=True)
#
#     class Meta:
#         model = StockFromExcel
#         fields = '__all__'

