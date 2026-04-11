from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import JobPreference
from .serializers import JobPreferenceSerializer


@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
def job_preference_detail(request):
    """Retrieve or update the current user's job preferences."""
    preference, _created = JobPreference.objects.get_or_create(user=request.user)

    if request.method == 'GET':
        return Response(JobPreferenceSerializer(preference).data)

    # PUT / PATCH
    partial = request.method == 'PATCH'
    serializer = JobPreferenceSerializer(preference, data=request.data, partial=partial)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
