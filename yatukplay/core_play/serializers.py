from rest_framework import serializers
from .models import Author, Audio

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = "__all__"
        
class AudioSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    class Meta:
        model = Audio
        fields = "__all__"
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['audio'] = "https://cms.yatuk.am"+instance.audio.url
        data['thumbnail'] = "https://cms.yatuk.am"+instance.thumbnail.url
        data['middle_optimized'] = "https://cms.yatuk.am"+instance.middle_optimized.url
        data['optimized'] = "https://cms.yatuk.am"+instance.optimized.url
        return data