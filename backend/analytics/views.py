
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta

from rest_framework.views import APIView
from rest_framework.response import Response

from users.permissions import IsAdmin
from projects.models import Project, Milestone
from inquiries.models import Inquiry
from users.models import User


class DashboardStatsView(APIView):
    """
    GET /api/analytics/dashboard/
    Admin ke liye overall stats
    """
    permission_classes = [IsAdmin]

    def get(self, request):
        # ----------------------------
        # PROJECT STATS
        # ----------------------------
        total_projects     = Project.objects.count()
        active_projects    = Project.objects.filter(
            status__in=['planning', 'in_progress']
        ).count()
        completed_projects = Project.objects.filter(status='completed').count()

        # Status ke hisaab se breakdown
        # Jaise: {"planning": 5, "in_progress": 3, "completed": 10}
        projects_by_status = dict(
            Project.objects.values('status')
            .annotate(count=Count('id'))
            .values_list('status', 'count')
        )

        # ----------------------------
        # CLIENT STATS
        # ----------------------------
        total_clients = User.objects.filter(role='client').count()

        # Last 30 din mein naye clients
        thirty_days_ago = timezone.now() - timedelta(days=30)
        new_clients_this_month = User.objects.filter(
            role='client',
            created_at__gte=thirty_days_ago
            # __gte = greater than or equal (>=)
        ).count()

        # ----------------------------
        # REVENUE STATS
        # ----------------------------
        total_budget = Project.objects.aggregate(
            total=Sum('budget')
        )['total'] or 0
        # 'or 0' zaroori hai — agar koi project nahi hai
        # to Sum None return karega, error aa sakta hai

        # ----------------------------
        # INQUIRY / LEAD STATS
        # ----------------------------
        total_inquiries    = Inquiry.objects.count()
        new_inquiries       = Inquiry.objects.filter(status='new').count()
        converted_inquiries = Inquiry.objects.filter(status='converted').count()

        # Conversion rate — kitna % leads client bane
        conversion_rate = 0
        if total_inquiries > 0:
            conversion_rate = round(
                (converted_inquiries / total_inquiries) * 100, 2
            )

        return Response({
            'projects': {
                'total':      total_projects,
                'active':     active_projects,
                'completed':  completed_projects,
                'by_status':  projects_by_status,
            },
            'clients': {
                'total':          total_clients,
                'new_this_month': new_clients_this_month,
            },
            'revenue': {
                'total_budget': total_budget,
            },
            'leads': {
                'total':            total_inquiries,
                'new':              new_inquiries,
                'converted':        converted_inquiries,
                'conversion_rate':  f"{conversion_rate}%",
            }
        })
