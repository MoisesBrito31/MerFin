from rest_framework import serializers
from .models import OS, Estado

class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estado
        fields = '__all__'

class OsSerializer(serializers.ModelSerializer):

    def validate_state(self, value):
        try:
            print(f"valor e {0}",value)
            estado = Estado.objects.get(id=int(value))
            return estado
        except Exception as EX:
            raise serializers.ValidationError(f"erro de validacao - {0}",str(EX))

    class Meta:
        model = OS
        fields = '__all__'
        depth = 1
