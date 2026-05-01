from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from django.core.signing import Signer, BadSignature
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

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

@api_view(['GET'])
@permission_classes([AllowAny])
def unsubscribe_digest(request, token):
    signer = Signer()
    try:
        user_id = signer.unsign(token)
    except BadSignature:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        
    preference = get_object_or_404(JobPreference, user_id=user_id)
    preference.digest_frequency = 'off'
    preference.save()
    return HttpResponse('<h2>Unsubscribed Successfully</h2><p>You have been unsubscribed from the job digest emails.</p>')
