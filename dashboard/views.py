from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from tickets.models import Ticket, Category
from accounts.models import User


@login_required
def home(request):
    user = request.user
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    seven_days_ago = now - timedelta(days=7)

    if user.is_end_user:
        my_tickets = Ticket.objects.filter(submitted_by=user)
        context = {
            'open_count': my_tickets.filter(status__in=['open', 'in_progress', 'pending']).count(),
            'resolved_count': my_tickets.filter(status='resolved').count(),
            'recent_tickets': my_tickets.order_by('-created_at')[:5],
            'is_end_user': True,
        }
        return render(request, 'dashboard/user_home.html', context)

    # Agent/Manager dashboard
    all_tickets = Ticket.objects.all()
    open_tickets = all_tickets.filter(status__in=['open', 'in_progress', 'pending'])
    overdue = [t for t in open_tickets if t.is_overdue()]

    context = {
        'total_open': open_tickets.count(),
        'total_in_progress': all_tickets.filter(status='in_progress').count(),
        'total_resolved_today': all_tickets.filter(status='resolved', resolved_at__date=now.date()).count(),
        'critical_count': open_tickets.filter(priority='critical').count(),
        'overdue_count': len(overdue),
        'unassigned_count': open_tickets.filter(assigned_to__isnull=True).count(),
        'recent_tickets': all_tickets.select_related('submitted_by', 'category', 'assigned_to').order_by('-created_at')[:8],
        'overdue_tickets': overdue[:5],
        'my_queue_count': all_tickets.filter(assigned_to=user, status__in=['open', 'in_progress']).count(),
    }

    if user.is_manager:
        # Extended analytics for managers
        agents = User.objects.filter(role__in=[User.ROLE_AGENT, User.ROLE_MANAGER])
        agent_stats = []
        for agent in agents:
            agent_tickets = all_tickets.filter(assigned_to=agent)
            agent_stats.append({
                'agent': agent,
                'open': agent_tickets.filter(status__in=['open', 'in_progress']).count(),
                'resolved_30d': agent_tickets.filter(status='resolved', resolved_at__gte=thirty_days_ago).count(),
            })

        by_category = Category.objects.annotate(
            ticket_count=Count('tickets', filter=Q(tickets__status__in=['open', 'in_progress', 'pending']))
        ).filter(ticket_count__gt=0).order_by('-ticket_count')[:5]

        by_priority = {
            'critical': open_tickets.filter(priority='critical').count(),
            'high': open_tickets.filter(priority='high').count(),
            'medium': open_tickets.filter(priority='medium').count(),
            'low': open_tickets.filter(priority='low').count(),
        }

        # Volume trend last 7 days
        trend = []
        for i in range(6, -1, -1):
            day = now - timedelta(days=i)
            trend.append({
                'date': day.strftime('%b %d'),
                'count': all_tickets.filter(created_at__date=day.date()).count()
            })

        avg_csat = all_tickets.filter(csat_score__isnull=False).aggregate(avg=Avg('csat_score'))['avg']

        context.update({
            'agent_stats': agent_stats,
            'by_category': by_category,
            'by_priority': by_priority,
            'trend': trend,
            'avg_csat': round(avg_csat, 1) if avg_csat else None,
            'sla_compliance': _calculate_sla_compliance(all_tickets, thirty_days_ago),
            'is_manager': True,
        })

    return render(request, 'dashboard/home.html', context)


def _calculate_sla_compliance(tickets, since):
    resolved = tickets.filter(status__in=['resolved', 'closed'], resolved_at__gte=since)
    total = resolved.count()
    if total == 0:
        return 100
    breached = resolved.filter(sla_breached=True).count()
    return round(((total - breached) / total) * 100, 1)


@login_required
def reports(request):
    if not request.user.is_manager:
        from django.shortcuts import redirect
        return redirect('dashboard:home')

    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    all_tickets = Ticket.objects.all()

    monthly_stats = []
    for i in range(5, -1, -1):
        month_start = (now - timedelta(days=30 * i)).replace(day=1, hour=0, minute=0, second=0)
        month_end = (month_start + timedelta(days=32)).replace(day=1)
        monthly_stats.append({
            'month': month_start.strftime('%b %Y'),
            'created': all_tickets.filter(created_at__gte=month_start, created_at__lt=month_end).count(),
            'resolved': all_tickets.filter(resolved_at__gte=month_start, resolved_at__lt=month_end).count(),
        })

    return render(request, 'dashboard/reports.html', {
        'monthly_stats': monthly_stats,
        'total_tickets': all_tickets.count(),
        'avg_csat': all_tickets.filter(csat_score__isnull=False).aggregate(avg=Avg('csat_score'))['avg'],
    })
