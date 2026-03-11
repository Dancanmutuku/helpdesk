from django import forms
from .models import Ticket, TicketReply, Category
from accounts.models import User

# ----------------------------
# Ticket Submission Form
# ----------------------------
class TicketSubmitForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'category', 'priority']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief description of your issue'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Please describe your issue in detail...'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(is_active=True)
        if user and user.is_end_user:
            # Limit priority choices for end users
            self.fields['priority'].choices = [
                ('low', 'Low'),
                ('medium', 'Medium'),
                ('high', 'High'),
            ]


# ----------------------------
# Ticket Reply Form
# ----------------------------
class TicketReplyForm(forms.ModelForm):
    class Meta:
        model = TicketReply
        fields = ['body', 'is_internal']
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Type your reply here...'
            }),
            'is_internal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.is_end_user:
            # End users cannot send internal replies
            self.fields.pop('is_internal', None)


# ----------------------------
# Ticket Update Form (agents only)
# ----------------------------
class TicketUpdateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['status', 'priority', 'assigned_to', 'category']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(
            role__in=[User.ROLE_AGENT, User.ROLE_MANAGER]
        )
        self.fields['assigned_to'].empty_label = 'Unassigned'


# ----------------------------
# Ticket Filter Form
# ----------------------------
class TicketFilterForm(forms.Form):
    STATUS_CHOICES = [('', 'All Statuses')] + list(Ticket.STATUS_CHOICES)
    PRIORITY_CHOICES = [('', 'All Priorities')] + list(Ticket.PRIORITY_CHOICES)

    search = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Search tickets...'
    }))
    status = forms.ChoiceField(
        choices=STATUS_CHOICES, required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES, required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        empty_label='All Categories',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    assigned_to = forms.CharField(required=False, widget=forms.HiddenInput())


# ----------------------------
# CSAT Form
# ----------------------------
class CSATForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['csat_score', 'csat_comment']
        widgets = {
            'csat_score': forms.RadioSelect(choices=[(i, i) for i in range(1, 6)]),
            'csat_comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional feedback...'
            }),
        }