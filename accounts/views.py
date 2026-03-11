from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import User, Department
from .forms import LoginForm, UserRegistrationForm, UserProfileForm, AgentCreateForm
from tickets.models import Ticket


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        next_url = request.GET.get('next', 'dashboard:home')
        return redirect(next_url)
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    form = UserRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.role = User.ROLE_END_USER
        user.save()
        login(request, user)
        messages.success(request, 'Account created successfully! Welcome to the IT Help Desk.')
        return redirect('dashboard:home')
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile_view(request):
    form = UserProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('accounts:profile')
    recent_tickets = Ticket.objects.filter(submitted_by=request.user).order_by('-created_at')[:5]
    return render(request, 'accounts/profile.html', {'form': form, 'recent_tickets': recent_tickets})


@login_required
def agent_list(request):
    if not request.user.is_manager:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    agents = User.objects.filter(role__in=[User.ROLE_AGENT, User.ROLE_MANAGER]).select_related('department')
    departments = Department.objects.all()
    return render(request, 'accounts/agent_list.html', {'agents': agents, 'departments': departments})


@login_required
def agent_create(request):
    if not request.user.is_manager:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    form = AgentCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Agent account created successfully.')
        return redirect('accounts:agent_list')
    return render(request, 'accounts/agent_form.html', {'form': form, 'title': 'Create Agent'})


@login_required
def agent_edit(request, pk):
    if not request.user.is_manager:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    agent = get_object_or_404(User, pk=pk)
    form = UserProfileForm(request.POST or None, request.FILES or None, instance=agent)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Agent updated successfully.')
        return redirect('accounts:agent_list')
    return render(request, 'accounts/agent_form.html', {'form': form, 'title': 'Edit Agent', 'agent': agent})
