from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.utils import timezone
from django.contrib import messages
from .models import JournalEntry, Mood
from .forms import RegisterForm, CombinedEntryForm
from django.http import JsonResponse
from django.db.models import Count, Avg
from django.db.models.functions import TruncWeek, TruncMonth
import datetime
import json
import calendar
from collections import defaultdict


@login_required
def home(request):
    today = timezone.now().date()
    
    try:
        journal_entry = JournalEntry.objects.get(user=request.user, date=today)
    except JournalEntry.DoesNotExist:
        journal_entry = None
    
    try:
        mood = Mood.objects.get(user=request.user, date=today)
    except Mood.DoesNotExist:
        mood = None
    
    # Get recent entries
    recent_entries = JournalEntry.objects.filter(user=request.user).order_by('-date')[:5]
    
    return render(request, 'home.html', {
        'journal_entry': journal_entry,
        'mood': mood,
        'today': today,
        'recent_entries': recent_entries,
    })


@login_required
def entry_list(request):
    entries = JournalEntry.objects.filter(user=request.user).order_by('-date')
    return render(request, 'journal/entry_list.html', {'entries': entries})


@login_required
def entry_detail(request, date):
    date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date()
    journal_entry = get_object_or_404(JournalEntry, user=request.user, date=date_obj)
    
    try:
        mood = Mood.objects.get(user=request.user, date=date_obj)
    except Mood.DoesNotExist:
        mood = None
    
    return render(request, 'journal/entry_detail.html', {
        'journal_entry': journal_entry,
        'mood': mood,
    })


@login_required
def create_entry(request):
    if request.method == 'POST':
        form = CombinedEntryForm(request.POST, user=request.user)
        if form.is_valid():
            journal_entry, mood = form.save()
            messages.success(request, 'Your journal entry has been saved!')
            return redirect('entry-detail', date=journal_entry.date)
    else:
        form = CombinedEntryForm(initial={'date': timezone.now().date()}, user=request.user)
    
    return render(request, 'journal/entry_form.html', {'form': form})


@login_required
def edit_entry(request, date):
    date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date()
    journal_entry = get_object_or_404(JournalEntry, user=request.user, date=date_obj)
    
    try:
        mood = Mood.objects.get(user=request.user, date=date_obj)
    except Mood.DoesNotExist:
        mood = None
    
    initial_data = {
        'title': journal_entry.title,
        'content': journal_entry.content,
        'date': journal_entry.date,
        'mood_type': mood.mood_type if mood else 'neutral',
    }
    
    if request.method == 'POST':
        form = CombinedEntryForm(request.POST, user=request.user)
        if form.is_valid():
            journal_entry, mood = form.save()
            messages.success(request, 'Your journal entry has been updated!')
            return redirect('entry-detail', date=journal_entry.date)
    else:
        form = CombinedEntryForm(initial=initial_data, user=request.user)
    
    return render(request, 'journal/entry_form.html', {'form': form, 'editing': True})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = RegisterForm()
    
    return render(request, 'registration/register.html', {'form': form})


@login_required
def mood_analytics(request):
    # Get the last 30 days of mood data by default
    end_date = timezone.now().date()
    start_date = end_date - datetime.timedelta(days=30)
    
    # Get all moods in the date range
    moods = Mood.objects.filter(
        user=request.user,
        date__gte=start_date,
        date__lte=end_date
    ).order_by('date')
    
    # Prepare data for daily mood chart
    daily_mood_data = {
        'labels': [],
        'datasets': [{
            'label': 'Daily Mood',
            'data': [],
            'backgroundColor': [],
            'borderColor': [],
            'borderWidth': 1
        }]
    }
    
    # Color mapping for moods
    mood_colors = {
        'happy': '#FFD700',    # Gold
        'excited': '#FF4500',  # OrangeRed
        'calm': '#87CEEB',     # SkyBlue
        'neutral': '#A9A9A9',  # DarkGray
        'tired': '#8B4513',    # SaddleBrown
        'anxious': '#9932CC',  # DarkOrchid
        'sad': '#4682B4',      # SteelBlue
        'angry': '#FF0000',    # Red
    }
    
    # Numerical values for moods (for calculating averages)
    mood_values = {
        'happy': 4,
        'excited': 4,
        'calm': 3,
        'neutral': 2,
        'tired': 1,
        'anxious': 1, 
        'sad': 0,
        'angry': 0,
    }
    
    # For weekly and monthly aggregation
    weekly_moods = defaultdict(list)
    monthly_moods = defaultdict(list)
    
    for mood in moods:
        # Add to daily chart data
        daily_mood_data['labels'].append(mood.date.strftime('%Y-%m-%d'))
        daily_mood_data['datasets'][0]['data'].append(mood_values[mood.mood_type])
        daily_mood_data['datasets'][0]['backgroundColor'].append(mood_colors[mood.mood_type])
        daily_mood_data['datasets'][0]['borderColor'].append(mood_colors[mood.mood_type])
        
        # Add to weekly and monthly aggregations
        week_key = mood.date.strftime('%Y-%W')  # Year and week number
        month_key = mood.date.strftime('%Y-%m')  # Year and month
        
        weekly_moods[week_key].append(mood_values[mood.mood_type])
        monthly_moods[month_key].append(mood_values[mood.mood_type])
    
    # Calculate weekly averages
    weekly_avg_data = {
        'labels': [],
        'datasets': [{
            'label': 'Weekly Mood Average',
            'data': [],
            'backgroundColor': 'rgba(75, 192, 192, 0.2)',
            'borderColor': 'rgba(75, 192, 192, 1)',
            'borderWidth': 1
        }]
    }
    
    for week_key, values in sorted(weekly_moods.items()):
        year, week = week_key.split('-')
        # Create a readable label for the week
        week_label = f"Week {week}, {year}"
        weekly_avg_data['labels'].append(week_label)
        weekly_avg_data['datasets'][0]['data'].append(sum(values) / len(values))
    
    # Calculate monthly averages
    monthly_avg_data = {
        'labels': [],
        'datasets': [{
            'label': 'Monthly Mood Average',
            'data': [],
            'backgroundColor': 'rgba(153, 102, 255, 0.2)',
            'borderColor': 'rgba(153, 102, 255, 1)',
            'borderWidth': 1
        }]
    }
    
    for month_key, values in sorted(monthly_moods.items()):
        year, month = month_key.split('-')
        month_name = calendar.month_name[int(month)]
        monthly_avg_data['labels'].append(f"{month_name} {year}")
        monthly_avg_data['datasets'][0]['data'].append(sum(values) / len(values))
    
    # Count occurrences of each mood
    mood_counts = {}
    for mood_type, _ in Mood.MOOD_CHOICES:
        mood_counts[mood_type] = moods.filter(mood_type=mood_type).count()
    
    # Prepare data for mood distribution pie chart
    mood_distribution_data = {
        'labels': [label for _, label in Mood.MOOD_CHOICES],
        'datasets': [{
            'data': [mood_counts[mood_type] for mood_type, _ in Mood.MOOD_CHOICES],
            'backgroundColor': [mood_colors[mood_type] for mood_type, _ in Mood.MOOD_CHOICES],
        }]
    }
    
    # Get the most recent mood for content recommendations
    latest_mood = Mood.objects.filter(user=request.user).order_by('-date').first()
    
    context = {
        'daily_mood_data': json.dumps(daily_mood_data),
        'weekly_avg_data': json.dumps(weekly_avg_data),
        'monthly_avg_data': json.dumps(monthly_avg_data),
        'mood_distribution_data': json.dumps(mood_distribution_data),
        'latest_mood': latest_mood,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'journal/mood_analytics.html', context)


@login_required
def tailored_content(request):
    # Get the user's most recent mood
    latest_mood = Mood.objects.filter(user=request.user).order_by('-date').first()
    
    # Default content if no mood is logged
    mood_type = 'neutral'
    
    if latest_mood:
        mood_type = latest_mood.mood_type
    
    # Content recommendations based on mood
    recommendations = {
        'happy': {
            'title': 'Celebrate Your Happiness',
            'content_type': 'uplifting',
            'music': [
                {'name': 'Walking on Sunshine', 'artist': 'Katrina and The Waves', 'url': 'https://www.youtube.com/watch?v=iPUmE-tne5U'},
                {'name': 'Happy', 'artist': 'Pharrell Williams', 'url': 'https://www.youtube.com/watch?v=ZbZSe6N_BXs'},
                {'name': 'Good Vibrations', 'artist': 'The Beach Boys', 'url': 'https://www.youtube.com/watch?v=Eab_beh07HU'},
            ],
            'activities': [
                'Share your joy with a friend or family member',
                'Start a gratitude journal to remember these moments',
                'Take a walk outside to enjoy the positive energy',
            ],
            'quote': '"Happiness is not something ready made. It comes from your own actions." — Dalai Lama'
        },
        'excited': {
            'title': 'Channel Your Excitement',
            'content_type': 'energetic',
            'music': [
                {'name': 'Can\'t Stop the Feeling', 'artist': 'Justin Timberlake', 'url': 'https://www.youtube.com/watch?v=ru0K8uYEZWw'},
                {'name': 'Uptown Funk', 'artist': 'Mark Ronson ft. Bruno Mars', 'url': 'https://www.youtube.com/watch?v=OPf0YbXqDm0'},
                {'name': 'I Gotta Feeling', 'artist': 'Black Eyed Peas', 'url': 'https://www.youtube.com/watch?v=uSD4vsh1zDA'},
            ],
            'activities': [
                'Plan your next adventure or project',
                'Try a new energetic activity like dancing or a sport',
                'Create a vision board for your goals',
            ],
            'quote': '"The future belongs to those who believe in the beauty of their dreams." — Eleanor Roosevelt'
        },
        'calm': {
            'title': 'Embrace Your Tranquility',
            'content_type': 'peaceful',
            'music': [
                {'name': 'Clair de Lune', 'artist': 'Claude Debussy', 'url': 'https://www.youtube.com/watch?v=WNcsUNKlAKw'},
                {'name': 'Weightless', 'artist': 'Marconi Union', 'url': 'https://www.youtube.com/watch?v=UfcAVejslrU'},
                {'name': 'Gymnopédie No.1', 'artist': 'Erik Satie', 'url': 'https://www.youtube.com/watch?v=S-Xm7s9eGxU'},
            ],
            'activities': [
                'Deep breathing exercises: 4-7-8 breathing technique',
                'Gentle yoga or stretching',
                'Mindful walking meditation',
            ],
            'quote': '"Peace comes from within. Do not seek it without." — Buddha'
        },
        'neutral': {
            'title': 'Find Your Balance',
            'content_type': 'balanced',
            'music': [
                {'name': 'Here Comes the Sun', 'artist': 'The Beatles', 'url': 'https://www.youtube.com/watch?v=KQetemT1sWc'},
                {'name': 'Clocks', 'artist': 'Coldplay', 'url': 'https://www.youtube.com/watch?v=d020hcWA_Wg'},
                {'name': 'Fields of Gold', 'artist': 'Sting', 'url': 'https://www.youtube.com/watch?v=KLVq0IAzh1A'},
            ],
            'activities': [
                'Take some time for self-reflection',
                'Try a new hobby or revisit an old one',
                'Organize your space or make a plan for tomorrow',
            ],
            'quote': '"The middle path is the way to wisdom." — Rumi'
        },
        'tired': {
            'title': 'Restore Your Energy',
            'content_type': 'soothing',
            'music': [
                {'name': 'Nocturne in E-flat major', 'artist': 'Frédéric Chopin', 'url': 'https://www.youtube.com/watch?v=9E6b3swbnWg'},
                {'name': 'Weightless', 'artist': 'Marconi Union', 'url': 'https://www.youtube.com/watch?v=UfcAVejslrU'},
                {'name': 'The Rain', 'artist': 'Ambient Sounds', 'url': 'https://www.youtube.com/watch?v=q76bMs-NwRk'},
            ],
            'activities': [
                'Take a short power nap (20-30 minutes)',
                'Gentle stretching exercises',
                'Have a soothing cup of herbal tea',
            ],
            'quote': '"Rest when you\'re weary. Refresh and renew yourself, your body, your mind, your spirit." — Ralph Marston'
        },
        'anxious': {
            'title': 'Finding Calm in the Storm',
            'content_type': 'calming',
            'music': [
                {'name': 'Weightless', 'artist': 'Marconi Union', 'url': 'https://www.youtube.com/watch?v=UfcAVejslrU'},
                {'name': 'Time After Time', 'artist': 'Cyndi Lauper', 'url': 'https://www.youtube.com/watch?v=VdQY7BusJNU'},
                {'name': 'Orinoco Flow', 'artist': 'Enya', 'url': 'https://www.youtube.com/watch?v=LTrk4X9ACtw'},
            ],
            'activities': [
                '5-4-3-2-1 Grounding technique: Name 5 things you see, 4 things you feel, 3 things you hear, 2 things you smell, and 1 thing you taste',
                'Box breathing: Inhale for 4, hold for 4, exhale for 4, hold for 4',
                'Progressive muscle relaxation: Tense and release each muscle group',
            ],
            'quote': '"You don\'t have to control your thoughts. You just have to stop letting them control you." — Dan Millman'
        },
        'sad': {
            'title': 'Finding Comfort',
            'content_type': 'comforting',
            'music': [
                {'name': 'Fix You', 'artist': 'Coldplay', 'url': 'https://www.youtube.com/watch?v=k4V3Mo61fJM'},
                {'name': 'Breathe Me', 'artist': 'Sia', 'url': 'https://www.youtube.com/watch?v=ghPcYqn0p4Y'},
                {'name': 'Someone Like You', 'artist': 'Adele', 'url': 'https://www.youtube.com/watch?v=hLQl3WQQoQ0'},
            ],
            'activities': [
                'Write down your feelings in your journal',
                'Talk to a trusted friend or family member',
                'Practice self-compassion meditation',
            ],
            'quote': '"Sadness flies away on the wings of time." — Jean de La Fontaine'
        },
        'angry': {
            'title': 'Finding Peace',
            'content_type': 'calming',
            'music': [
                {'name': 'Mad World', 'artist': 'Gary Jules', 'url': 'https://www.youtube.com/watch?v=4N3N1MlvVc4'},
                {'name': 'Everybody Hurts', 'artist': 'R.E.M.', 'url': 'https://www.youtube.com/watch?v=5rOiW_xY-kc'},
                {'name': 'Nothing Else Matters', 'artist': 'Metallica', 'url': 'https://www.youtube.com/watch?v=tAGnKpE4NCI'},
            ],
            'activities': [
                'Physical exercise to release tension',
                'Deep breathing exercises: 4-7-8 breathing',
                'Write a letter expressing your feelings (you don\'t have to send it)',
            ],
            'quote': '"For every minute you remain angry, you give up sixty seconds of peace of mind." — Ralph Waldo Emerson'
        },
    }
    
    recommendation = recommendations.get(mood_type, recommendations['neutral'])
    
    return render(request, 'journal/tailored_content.html', {
        'mood_type': mood_type,
        'recommendation': recommendation,
        'latest_mood': latest_mood,
    })


@login_required
def mood_data_api(request):
    # For AJAX requests to get mood data for charts
    timeframe = request.GET.get('timeframe', 'month')
    
    # Set the date range based on the timeframe
    end_date = timezone.now().date()
    if timeframe == 'week':
        start_date = end_date - datetime.timedelta(days=7)
    elif timeframe == 'month':
        start_date = end_date - datetime.timedelta(days=30)
    elif timeframe == 'year':
        start_date = end_date - datetime.timedelta(days=365)
    else:
        # Default to month
        start_date = end_date - datetime.timedelta(days=30)
    
    # Get all moods in the date range
    moods = Mood.objects.filter(
        user=request.user,
        date__gte=start_date,
        date__lte=end_date
    ).order_by('date')
    
    # Numerical values for moods (for calculating averages)
    mood_values = {
        'happy': 4,
        'excited': 4,
        'calm': 3,
        'neutral': 2,
        'tired': 1,
        'anxious': 1, 
        'sad': 0,
        'angry': 0,
    }
    
    # Prepare data for charts
    data = {
        'labels': [],
        'values': [],
    }
    
    for mood in moods:
        data['labels'].append(mood.date.strftime('%Y-%m-%d'))
        data['values'].append(mood_values[mood.mood_type])
    
    return JsonResponse(data)
