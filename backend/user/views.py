from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializer import UsuarioSerializer

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getUserData(request):
    try:
        user = request.user
        serial =UsuarioSerializer(user)
        data = {
            'name':serial.data['username'],
            'avatar':serial.data['avatar'],
            'alertas':str(serial.data['alertasNovos']),
        }
    except Exception as EX:
        data = {
            'valor': '',
            'erro': str(EX)
        }
    return Response(data)
