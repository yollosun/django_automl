from rest_framework import serializers
from .models import File, GraphData, DataModel


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = "__all__"


class GraphDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = GraphData
        fields = "__all__"

class DataModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataModel
        fields = "__all__"
# class ProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Profile
#         fields = "__all__"
