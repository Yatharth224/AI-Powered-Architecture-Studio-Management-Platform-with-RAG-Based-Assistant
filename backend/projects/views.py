# projects/views.py

import logging
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from users.permissions import IsAdmin, IsAdminOrArchitect
from .models import Project, Milestone
from .serializers import (
    ProjectSerializer,
    ProjectCreateSerializer,
    MilestoneSerializer,
    AssignArchitectSerializer
)

logger = logging.getLogger(__name__)


class ProjectListView(generics.ListCreateAPIView):
    """
    GET  /api/projects/  → Projects list (role based)
    POST /api/projects/  → Naya project banao (Admin only)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        # POST ke liye alag serializer
        if self.request.method == 'POST':
            return ProjectCreateSerializer
        return ProjectSerializer

    def get_queryset(self):
        user = self.request.user

        if user.role == 'admin':
            return Project.objects.all()
        elif user.role == 'client':
            # Sirf apne projects
            return Project.objects.filter(client=user)
        elif user.role == 'architect':
            # Sirf assigned projects
            return Project.objects.filter(architect=user)
        else:
            return Project.objects.none()

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        project = serializer.save()
        logger.info(f"Project created: {project.title} by {self.request.user.email}")


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/projects/<id>/  → Project detail
    PUT    /api/projects/<id>/  → Project update
    DELETE /api/projects/<id>/  → Project delete (Admin)
    """
    serializer_class   = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Project.objects.all()
        elif user.role == 'client':
            return Project.objects.filter(client=user)
        elif user.role == 'architect':
            return Project.objects.filter(architect=user)
        return Project.objects.none()

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAdmin()]
        return [permissions.IsAuthenticated()]

    def destroy(self, request, *args, **kwargs):
        project = self.get_object()
        logger.info(f"Project deleted: {project.title} by {request.user.email}")
        return super().destroy(request, *args, **kwargs)


class AssignArchitectView(APIView):
    """
    PATCH /api/projects/<id>/assign/
    Admin architect assign kare project pe
    Body: { "architect": <user_id> }
    """
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        try:
            project = Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return Response(
                {'error': 'Project not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AssignArchitectSerializer(
            project,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        logger.info(
            f"Architect assigned to {project.title} "
            f"by {request.user.email}"
        )

        return Response({
            'message': 'Architect assigned successfully',
            'project': ProjectSerializer(project).data
        })


class MilestoneListView(generics.ListCreateAPIView):
    """
    GET  /api/projects/<id>/milestones/  → Milestones list
    POST /api/projects/<id>/milestones/  → Naya milestone
    """
    serializer_class   = MilestoneSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Milestone.objects.filter(
            project_id=self.kwargs['project_id']
        )

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrArchitect()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        project = Project.objects.get(pk=self.kwargs['project_id'])
        serializer.save(project=project)


class MilestoneDetailView(generics.RetrieveUpdateAPIView):
    """
    GET   /api/projects/milestones/<id>/  → Milestone detail
    PATCH /api/projects/milestones/<id>/  → Milestone update
    """
    serializer_class   = MilestoneSerializer
    permission_classes = [IsAdminOrArchitect]
    queryset           = Milestone.objects.all()