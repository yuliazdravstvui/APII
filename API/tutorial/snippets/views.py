from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, renderers

from .models import Snippet
from .serializers import SnippetSerializer, UserSerializer
from rest_framework import mixins
from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework import permissions
from .permissions import IsOwnerOrReadOnly
from rest_framework.decorators import api_view, action
from rest_framework.reverse import reverse
from django.shortcuts import render

class SnippetList(APIView):
   """
   List all snippets, or create a new snippet.
   """

   def get(self, request, format=None):
       snippets = Snippet.objects.all()
       serializer = SnippetSerializer(snippets, many=True)
       return Response(serializer.data)

   def post(self, request, format=None):
       serializer = SnippetSerializer(data=request.data)
       if serializer.is_valid():
           serializer.save()
           return Response(serializer.data, status=status.HTTP_201_CREATED)
       return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SnippetDetail(APIView):
   """
   Retrieve, update or delete a snippet instance.
   """

   def get_object(self, pk):
       try:
           return Snippet.objects.get(pk=pk)
       except Snippet.DoesNotExist:
           raise Http404

   def get(self, request, pk, format=None):
       snippet = self.get_object(pk)
       serializer = SnippetSerializer(snippet)
       return Response(serializer.data)

   def put(self, request, pk, format=None):
       snippet = self.get_object(pk)
       serializer = SnippetSerializer(snippet, data=request.data)
       if serializer.is_valid():
           serializer.save()
           return Response(serializer.data)
       return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

   def delete(self, request, pk, format=None):
       snippet = self.get_object(pk)
       snippet.delete()
       return Response(status=status.HTTP_204_NO_CONTENT)



#модернизация классов

class SnippetViewSet(viewsets.ModelViewSet):
   """
   This viewset automatically provides `list`, `create`, `retrieve`,
   `update` and `destroy` actions.

   Additionally we also provide an extra `highlight` action.
   """
   queryset = Snippet.objects.all()
   serializer_class = SnippetSerializer
   permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                         IsOwnerOrReadOnly]

   @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
   def highlight(self, request, *args, **kwargs):
       snippet = self.get_object()
       return Response(snippet.highlighted)

   def perform_create(self, serializer):
       serializer.save(owner=self.request.user)

class UserViewSet(viewsets.ReadOnlyModelViewSet):
   """
   This viewset automatically provides `list` and `retrieve` actions.
   """
   queryset = User.objects.all()
   serializer_class = UserSerializer


@api_view(['GET'])
def api_root(request, format=None):
   return Response({
       'users': reverse('user-list', request=request, format=format),
       'snippets': reverse('snippet-list', request=request, format=format)
   })

