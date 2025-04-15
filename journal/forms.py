from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import JournalEntry, Mood


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class JournalEntryForm(forms.ModelForm):
    class Meta:
        model = JournalEntry
        fields = ['title', 'content', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'content': forms.Textarea(attrs={'rows': 6}),
        }


class MoodForm(forms.ModelForm):
    class Meta:
        model = Mood
        fields = ['mood_type', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }


class CombinedEntryForm(forms.Form):
    title = forms.CharField(max_length=100)
    content = forms.CharField(widget=forms.Textarea(attrs={'rows': 6}))
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    mood_type = forms.ChoiceField(choices=Mood.MOOD_CHOICES)
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(CombinedEntryForm, self).__init__(*args, **kwargs)
    
    def save(self):
        # Create or update the mood entry
        mood, created = Mood.objects.update_or_create(
            user=self.user,
            date=self.cleaned_data['date'],
            defaults={'mood_type': self.cleaned_data['mood_type']}
        )
        
        # Create or update the journal entry
        journal_entry, created = JournalEntry.objects.update_or_create(
            user=self.user,
            date=self.cleaned_data['date'],
            defaults={
                'title': self.cleaned_data['title'],
                'content': self.cleaned_data['content']
            }
        )
        
        return journal_entry, mood
