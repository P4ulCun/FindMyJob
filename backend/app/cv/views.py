import os

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import CV
from .serializers import CVSerializer
from .cv_parser import extract_text_from_pdf, parse_cv_text

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def upload_cv(request):
    """Upload a PDF CV, extract text, and return parsed data."""
    file = request.FILES.get('file')

    if not file:
        return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate extension
    ext = os.path.splitext(file.name)[1].lower()
    if ext != '.pdf':
        return Response({'error': 'Only .pdf files are accepted.'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate size
    if file.size > MAX_FILE_SIZE:
        return Response(
            {'error': f'File exceeds the 5 MB limit (got {file.size} bytes).'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Extract & parse
    raw_text = extract_text_from_pdf(file)
    parsed = parse_cv_text(raw_text)

    # Persist
    cv = CV.objects.create(
        user=request.user,
        file=file,
        extracted_name=parsed['name'],
        extracted_skills=parsed['skills'],
        extracted_experience=parsed['experience'],
        extracted_education=parsed['education'],
    )

    return Response(CVSerializer(cv).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cv_me(request):
    """Return the current user's most recent CV, or 404 if none."""
    cv = request.user.cvs.first()
    if not cv:
        return Response({'error': 'No CV found.'}, status=status.HTTP_404_NOT_FOUND)
    return Response(CVSerializer(cv).data)


@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
def cv_detail(request, pk):
    """Retrieve or update extracted fields of a CV owned by the current user."""
    try:
        cv = CV.objects.get(pk=pk, user=request.user)
    except CV.DoesNotExist:
        return Response({'error': 'CV not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(CVSerializer(cv).data)

    # PUT / PATCH
    partial = request.method == 'PATCH'
    serializer = CVSerializer(cv, data=request.data, partial=partial)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
