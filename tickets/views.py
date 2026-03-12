# tickets/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse

from .models import Ticket, TicketReply, TicketAttachment, TicketHistory, Category, CannedResponse
from .forms import TicketSubmitForm, TicketReplyForm, TicketUpdateForm, TicketFilterForm, CSATForm
from .utils import send_ticket_email
from accounts.models import User


def log_history(ticket, user, field, old_val, new_val):
    """Log changes to ticket fields."""
    if str(old_val) != str(new_val):
        TicketHistory.objects.create(
            ticket=ticket,
            changed_by=user,
            field_changed=field,
            old_value=str(old_val) if old_val else '',
            new_value=str(new_val) if new_val else '',
        )


@login_required
def ticket_submit(request):
    form = TicketSubmitForm(request.POST or None, user=request.user)
    if request.method == 'POST' and form.is_valid():
        ticket = form.save(commit=False)
        ticket.submitted_by = request.user
        if ticket.category and ticket.category.auto_assign_to:
            ticket.assigned_to = ticket.category.auto_assign_to
        ticket.save()

        # Handle multiple attachments directly from request.FILES
        for f in request.FILES.getlist('attachments'):
            TicketAttachment.objects.create(
                ticket=ticket,
                uploaded_by=request.user,
                file=f,
                filename=f.name,
                file_size=f.size
            )

        messages.success(request, f'Ticket {ticket.ticket_id} submitted successfully!')
        return redirect('tickets:detail', ticket_id=ticket.ticket_id)

    return render(request, 'tickets/submit.html', {'form': form})


@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
    if request.user.is_end_user and ticket.submitted_by != request.user:
        messages.error(request, 'Access denied.')
        return redirect('tickets:list')

    replies = ticket.replies.all()
    if request.user.is_end_user:
        replies = replies.filter(is_internal=False)

    reply_form = TicketReplyForm(user=request.user)
    update_form = TicketUpdateForm(instance=ticket) if request.user.is_agent else None
    csat_form = CSATForm(instance=ticket) if ticket.status in ['resolved', 'closed'] and not ticket.csat_score else None

    if request.method == 'POST':
        action = request.POST.get('action')

        # -----------------------------
        # Reply action
        # -----------------------------
        if action == 'reply':
            reply_form = TicketReplyForm(request.POST, user=request.user)
            if reply_form.is_valid():
                reply = reply_form.save(commit=False)
                reply.ticket = ticket
                reply.author = request.user
                reply.save()

                # Handle attachments
                for f in request.FILES.getlist('attachments'):
                    TicketAttachment.objects.create(
                        ticket=ticket,
                        uploaded_by=request.user,
                        file=f,
                        filename=f.name,
                        file_size=f.size
                    )

                if not ticket.first_response_at and request.user.is_agent:
                    ticket.first_response_at = timezone.now()
                    ticket.save(update_fields=['first_response_at'])

                # Notify ticket owner (end user) if someone else replied
                if request.user != ticket.submitted_by:
                    send_ticket_email(
                        ticket.submitted_by,
                        subject=f"Update on Ticket {ticket.ticket_id}",
                        message=f"""
Hello {ticket.submitted_by.get_full_name() or ticket.submitted_by.username},

Your ticket "{ticket.title}" has received a new reply.

View it here: {request.build_absolute_uri()}

Regards,
IT HelpDesk
"""
                    )

                messages.success(request, 'Reply added.')
                return redirect('tickets:detail', ticket_id=ticket_id)

        # -----------------------------
        # Update action (status, priority, assignment)
        # -----------------------------
        elif action == 'update' and request.user.is_agent:
            update_form = TicketUpdateForm(request.POST, instance=ticket)
            if update_form.is_valid():
                old_status = ticket.status
                old_priority = ticket.priority
                old_assigned = ticket.assigned_to
                updated = update_form.save()
                log_history(ticket, request.user, 'status', old_status, updated.status)
                log_history(ticket, request.user, 'priority', old_priority, updated.priority)
                log_history(ticket, request.user, 'assigned_to', old_assigned, updated.assigned_to)

                # Track changes to notify end user
                changes = []
                if old_status != updated.status:
                    changes.append(f"Status changed from {old_status} to {updated.status}")
                if old_priority != updated.priority:
                    changes.append(f"Priority changed to {updated.priority}")
                if old_assigned != updated.assigned_to:
                    changes.append("Ticket has been assigned to an agent")

                if changes:
                    send_ticket_email(
                        ticket.submitted_by,
                        subject=f"Ticket {ticket.ticket_id} Updated",
                        message=f"""
Hello {ticket.submitted_by.get_full_name() or ticket.submitted_by.username},

Your ticket "{ticket.title}" has been updated:

{chr(10).join(changes)}

View ticket: {request.build_absolute_uri()}

Regards,
IT HelpDesk
"""
                    )

                # If ticket is closed, send separate notification
                if updated.status == "closed":
                    send_ticket_email(
                        ticket.submitted_by,
                        subject=f"Ticket {ticket.ticket_id} Closed",
                        message=f"""
Hello {ticket.submitted_by.get_full_name() or ticket.submitted_by.username},

Your ticket "{ticket.title}" has been marked as CLOSED.

If the issue persists, you may reopen or create a new ticket.

View ticket: {request.build_absolute_uri()}

Thank you for using IT HelpDesk.
"""
                    )

                messages.success(request, 'Ticket updated.')
                return redirect('tickets:detail', ticket_id=ticket_id)

        # -----------------------------
        # CSAT feedback
        # -----------------------------
        elif action == 'csat':
            csat_form = CSATForm(request.POST, instance=ticket)
            if csat_form.is_valid():
                csat_form.save()
                messages.success(request, 'Thank you for your feedback!')
                return redirect('tickets:detail', ticket_id=ticket_id)

    return render(request, 'tickets/detail.html', {
        'ticket': ticket,
        'replies': replies,
        'attachments': ticket.attachments.all(),
        'history': ticket.history.all()[:10],
        'reply_form': reply_form,
        'update_form': update_form,
        'csat_form': csat_form,
        'canned_responses': CannedResponse.objects.filter(is_active=True) if request.user.is_agent else [],
    })


# -----------------------------
# Ticket List View
# -----------------------------
@login_required
def ticket_list(request):
    if request.user.is_agent:
        qs = Ticket.objects.all().order_by('-created_at')
    else:
        qs = Ticket.objects.filter(submitted_by=request.user).order_by('-created_at')

    filter_form = TicketFilterForm(request.GET or None)
    if filter_form.is_valid():
        search = filter_form.cleaned_data.get('search')
        status = filter_form.cleaned_data.get('status')
        priority = filter_form.cleaned_data.get('priority')
        category = filter_form.cleaned_data.get('category')

        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(ticket_id__icontains=search)
            )
        if status:
            qs = qs.filter(status=status)
        if priority:
            qs = qs.filter(priority=priority)
        if category:
            qs = qs.filter(category=category)

    paginator = Paginator(qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'tickets/list.html', {
        'tickets': page_obj,
        'filter_form': filter_form,
        'total_count': qs.count(),
    })


# -----------------------------
# Canned Responses API
# -----------------------------
@login_required
def canned_responses_api(request):
    if not request.user.is_agent:
        return JsonResponse({'error': 'Access denied'}, status=403)
    responses = CannedResponse.objects.filter(is_active=True).values('id', 'title', 'content')
    return JsonResponse(list(responses), safe=False)


# -----------------------------
# Escalate Ticket
# -----------------------------
@login_required
def ticket_escalate(request, ticket_id):
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)

    if not request.user.is_agent:
        messages.error(request, "Access denied.")
        return redirect('tickets:detail', ticket_id=ticket_id)

    old_priority = ticket.priority
    ticket.priority = 'critical'
    ticket.save(update_fields=['priority'])

    # Notify end user
    send_ticket_email(
        ticket.submitted_by,
        subject=f"Ticket {ticket.ticket_id} Escalated",
        message=f"""
Hello {ticket.submitted_by.get_full_name() or ticket.submitted_by.username},

Your ticket "{ticket.title}" has been escalated to CRITICAL priority.

View ticket: {request.build_absolute_uri()}

Regards,
IT HelpDesk
"""
    )

    messages.success(request, f"Ticket {ticket.ticket_id} escalated from {old_priority} to Critical.")
    return redirect('tickets:detail', ticket_id=ticket_id)