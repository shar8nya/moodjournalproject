from django.contrib import admin
from .models import Mood, JournalEntry

@admin.register(Mood)
class MoodAdmin(admin.ModelAdmin):
    list_display = ('user', 'mood_type', 'date')
    list_filter = ('mood_type', 'date', 'user')
    search_fields = ('user__username', 'mood_type')
    date_hierarchy = 'date'

@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'date', 'get_mood')
    list_filter = ('date', 'user')
    search_fields = ('user__username', 'title', 'content')
    date_hierarchy = 'date'
    
    def get_mood(self, obj):
        mood = Mood.objects.filter(user=obj.user, date=obj.date).first()
        return mood.get_mood_type_display() if mood else 'No mood recorded'
    
    get_mood.short_description = 'Mood'
