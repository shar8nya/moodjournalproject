from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone


class Mood(models.Model):
    MOOD_CHOICES = [
        ('happy', 'Happy'),
        ('excited', 'Excited'),
        ('calm', 'Calm'),
        ('neutral', 'Neutral'),
        ('tired', 'Tired'),
        ('anxious', 'Anxious'),
        ('sad', 'Sad'),
        ('angry', 'Angry'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mood_type = models.CharField(max_length=20, choices=MOOD_CHOICES)
    date = models.DateField(default=timezone.now)
    
    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.username}'s mood on {self.date}: {self.get_mood_type_display()}"
    
    def get_absolute_url(self):
        return reverse('entry-detail', kwargs={'date': self.date})


class JournalEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']
        verbose_name_plural = 'Journal Entries'
    
    def __str__(self):
        return f"{self.title} - {self.date}"
    
    def get_absolute_url(self):
        return reverse('entry-detail', kwargs={'date': self.date})
    
    def get_mood(self):
        try:
            return Mood.objects.get(user=self.user, date=self.date)
        except Mood.DoesNotExist:
            return None
