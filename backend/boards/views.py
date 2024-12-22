from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
# Create your views here.

@csrf_exempt
@api_view(['GET'])
def index(request):
    return Response("Hello World")