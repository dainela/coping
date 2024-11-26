from datetime import timedelta, timezone
from django.contrib.auth.decorators import user_passes_test
import json
import os
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from .models import *
from .filters import *
from django.db.models import Max
from .forms import *
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from rest_framework import generics
from django.db.models import OuterRef, Subquery
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.jwt.access_token import AccessToken
from django.views.decorators.csrf import csrf_protect
from twilio.jwt.access_token.grants import VideoGrant
from django.http import Http404
from django.template.loader import select_template, TemplateDoesNotExist
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework import permissions
from django.db.models import Q
from .models import MoodEntry
from django.http import HttpResponseForbidden
from datetime import date
from django.utils.dateparse import parse_date
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings




# Create your views here.


def home(request):
    return render(request, 'pages/home.html')

@login_required
def navbar(request):
    try:
        # Attempt to fetch the psychologist associated with the logged-in user
        psychologist = Psychologist.objects.get(user=request.user)
    except Psychologist.DoesNotExist:
        psychologist = None  # If no associated psychologist is found, set to None

    context = {
        'psychologist': psychologist,
    }
    return render(request, 'pages/navbar.html', context)

def about(request):
    return render(request, 'pages/about.html')

@login_required
def prof(request):
    # Get the logged-in user's psychologist profile
    psychologist = Psychologist.objects.filter(user=request.user).first()  # Adjust as needed

    # Get all psychologists
    prof = Psychologist.objects.all()

    # Fetch the latest availability for each psychologist
    for p in prof:
        latest_availability = p.availability_set.order_by('-timestamp').first()
        p.latest_availability = latest_availability

    context = {
        'psychologist': psychologist,  # Logged-in user's profile
        'prof': prof,                  # All psychologists
    }

    return render(request, 'pages/prof.html', context)

@login_required
def coping(request):
    return render(request, 'pages/coping.html')

@login_required
def viewpsych(request):
    


    if not request.user.is_superuser:
        # If not a superuser, return a forbidden response or redirect
        return HttpResponseForbidden("You do not have permission to view this page.")    

    prof = Psychologist.objects.all()
    return render(request, 'pages/viewpsych.html', {'prof': prof})

@login_required
def approve_psychologist(request, psychologist_id):
    if request.method == 'POST':
        psychologist = get_object_or_404(Psychologist, id=psychologist_id)
        psychologist.is_approved = True
        psychologist.save()
        
        user = psychologist.user
        user.is_staff = True  
        user.save()
        
        messages.success(request, 'Psychologist approved successfully.')
        return redirect('viewpsych')  # Ensure this matches the URL name

@login_required
def reject_psychologist(request, psychologist_id):
    if request.method == 'POST':
        psychologist = get_object_or_404(Psychologist, id=psychologist_id)
        psychologist.is_rejected = True  # Alternatively, mark as rejected
        messages.success(request, 'Psychologist rejected successfully.')
        return redirect('viewpsych')  # Redirect to the admin approval page

@login_required
def viewfeed(request):
    feedback = Feedback.objects.all()  # Retrieve all feedback entries

    query = request.GET.get('q', '')  # Handle search queries
    if query:
        feedback = feedback.filter(
            feed__icontains=query
        )  # Filter feedback based on the query (case-insensitive)

    context = {
        'feedback': feedback,  # Pass the feedback to the template
        'query': query,  # Pass the search query back for display
    }
    return render(request, 'pages/viewfeed.html', context)



@login_required
def viewprof(request):
    # Fetch only non-admin, non-staff users
    users = User.objects.filter(is_staff=False, is_superuser=False, is_active=True) 

    # Get the most recent response for each user
    latest_responses = (
        GAD7Response.objects.values('user')
        .annotate(latest_timestamp=Max('timestamp'))  # Get the latest timestamp per user
        .order_by('user')
    )

    # Fetch the actual response objects for those timestamps
    responses = GAD7Response.objects.filter(
        timestamp__in=[item['latest_timestamp'] for item in latest_responses]
    )

    context = {
        'user': request.user,  # The currently logged-in user
        'users': users,  # All users
        'latest_responses': responses,  # Pass the latest responses to the template
    }
    return render(request, 'pages/viewprof.html', context)




@login_required
def viewfeed(request):
    query = request.GET.get('q', '')  # Get the search query from the request
    register = Feedback.objects.all()

    if query:
        # Filter profiles by first name, last name, or email
        register = register.filter(
            Q(First_Name__icontains=query) | 
            Q(Last_Name__icontains=query) | 
            Q(Email__icontains=query)
        )

    context = {
        'register': register,
        'query': query,  # Pass the query back to the template for input field
    }
    return render(request, 'pages/viewfeed.html', context)

@login_required
def feedback(request):
    if request.method == "POST":
        feed = request.POST.get('feed')
        email_address = request.POST.get('email_address')

        # Save the feedback to the database
        Feedback.objects.create(user=request.user, email_address=email_address, feed=feed)
        messages.success(request, "Thank you for your feedback!")
        return redirect('feedback')  # Redirect to the same page after submission
    
    return render(request, 'pages/feedback.html')

@login_required
def videocall(request):
    return render(request,'pages/videocall.html')



@login_required  # Ensure only logged-in users can access this view
def profile(request):
    user = request.user

    if user.is_superuser:
        # Add any logic for superuser here
        pass

    # Fetch the user's profile
    profile = Profile.objects.get(user=user)

    # Get the latest GAD7Response for the user
    try:
        latest_mood = GAD7Response.objects.filter(user=user).order_by('-timestamp').first()
    except GAD7Response.DoesNotExist:
        latest_mood = None  # In case the user has no GAD7 responses

    # Fetch mood entries for the logged-in user
    mood_entries = MoodEntry.objects.filter(user=user)
    moods = {entry.date.strftime('%Y-%m-%d'): entry.mood for entry in mood_entries}

    # Calculate scores for the user as done in viewpatient
    tasks = Task.objects.filter(user=user, is_completed=True)
    total_task_score = sum(task.score for task in tasks)

    defusion_entries = Defusion.objects.filter(user=user)
    total_defusion_score = sum(entry.score for entry in defusion_entries)

    exercises = ExerciseCompletion.objects.filter(user=user)
    total_exercise_score = sum(exercise.score for exercise in exercises)

    yoga = YogaCompletion.objects.filter(user=user)
    total_yoga_score = sum(yoga.score for yoga in yoga)

    distraction_entries = Distraction.objects.filter(user=user)
    total_distraction_score = sum(entry.score for entry in distraction_entries)

    mind_management_scores = MindManagement.objects.filter(user=user)
    total_mind_management_score = sum(score.score for score in mind_management_scores)

    relaxation_scores = RelaxationScore.objects.filter(user=user)
    total_relaxation_score = sum(relaxation.score for relaxation in relaxation_scores)

    # Total score across all models
    total_score = (total_task_score + total_defusion_score + total_exercise_score +
                   total_yoga_score + total_distraction_score + total_mind_management_score +
                   total_relaxation_score)

    # Add the scores to the context
    context = {
        'user': user,
        'profile': profile,
        'mood': latest_mood,
        'moods': moods,
        'total_score': total_score,
        'total_task_score': total_task_score,
        'total_defusion_score': total_defusion_score,
        'total_exercise_score': total_exercise_score,
        'total_yoga_score': total_yoga_score,
        'total_distraction_score': total_distraction_score,
        'total_mind_management_score': total_mind_management_score,
        'total_relaxation_score': total_relaxation_score,
    }

    return render(request, 'pages/profile.html', context)


@login_required
def edit_profile(request):
    profile = request.user.profile  # Get the user's profile

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to the profile page after saving
    else:
        form = ProfileEditForm(instance=profile, user=request.user)

    context = {
        'form': form
    }
    return render(request, 'pages/edit_profile.html', context)

def signin(request):
    context = {}

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if not user.profile.completed_gad7:
                return redirect('gad7')
            else:
                return redirect('home') 
        
        else:
            # If authentication fails, set an error flag
            context['login_failed'] = True

    return render(request, 'pages/signin.html', context)

def signup(request):
    if request.method == 'POST':
        form = CreationForm(request.POST, request.FILES)  # Handle file uploads with request.FILES
        if form.is_valid():
            form.save()
            return redirect('signin')  # Redirect to login after registration
    else:
        form = CreationForm()
    
    return render(request, 'pages/signup.html', {'form': form})

def signout(request):
    logout(request)  # Log the user out
    return redirect('home')

@login_required
def updateprofile(request):
    form = CreationForm()
    if request.method == 'POST':
        form = CreationForm(request.POST)
        
        if form.is_valid():
            form.save()
            return redirect('updateprofile')
        
    context = {
        'form':form
    }
  
    return render(request, 'pages/updateprofile.html', context)




  

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'pages/category_list.html', {'categories': categories})


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    subcategories = category.subcategories.all()
    return render(request, 'pages/category_detail.html', {
        'category': category,
        'subcategories': subcategories
    })

@login_required
def subcategory_detail(request, category_slug, subcategory_slug):
    category = get_object_or_404(Category, slug=category_slug)
    subcategory = get_object_or_404(Subcategory, slug=subcategory_slug, category=category)

    # Look for a subcategory-specific template, e.g., subcategory_daniel.html
    template_name = f'pages/subcategory_{subcategory.slug}.html'
    
    try:
        return render(request, template_name, {
            'category': category,
            'subcategory': subcategory,
        })
    except TemplateDoesNotExist:
        raise Http404("The requested page does not exist.")

    return render(request, template.template.name, {
        'category': category,
        'subcategory': subcategory,
    })

@login_required
def add_category(request):
    if request.method == 'POST':
        category_form = CategoryForm(request.POST, request.FILES)
        if category_form.is_valid():
            category = category_form.save()  # Save the category
            return redirect('add_subcategory')  # Redirect to subcategory page
    else:
        category_form = CategoryForm()

    context = {
        'category_form': category_form,
    }

    return render(request, 'pages/add_category.html', context)

@login_required
def add_subcategory(request):
    if request.method == 'POST':
        subcategory_form = SubcategoryForm(request.POST, request.FILES)
        if subcategory_form.is_valid():
            subcategory = subcategory_form.save()  # Save the category
            return redirect('add_subcategory')  # Redirect to subcategory page
    else:
        subcategory_form = SubcategoryForm()

    context = {
        'subcategory_form': subcategory_form,
    }

    return render(request, 'pages/add_subcategory.html', context)

def staff(request):
    if request.method == 'POST':
        form = StaffUserSignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('staff')  # Redirect to login or any other page after signup
    else:
        form = StaffUserSignupForm()
    return render(request, 'pages/staff.html', {'form': form})

def upvote_post(request, post_id):
        post = get_object_or_404(Post, id=post_id)
        post.upvotes += 1
        post.save()
        return JsonResponse({'upvotes': post.upvotes, 'downvotes': post.downvotes})

def downvote_post(request, post_id):
        post = get_object_or_404(Post, id=post_id)
        post.downvotes += 1
        post.save()
        return JsonResponse({'upvotes': post.upvotes, 'downvotes': post.downvotes})

def upvote_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    comment.upvotes += 1
    comment.save()
    return JsonResponse({'upvotes': comment.upvotes, 'downvotes': comment.downvotes})

def downvote_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    comment.downvotes += 1
    comment.save()
    return JsonResponse({'upvotes': comment.upvotes, 'downvotes': comment.downvotes})


@login_required
def onlinecom(request):
    # Fetch posts and profiles
    posts = Post.objects.prefetch_related('comments').all().order_by('-timestamp')
    profile = Profile.objects.all()

    if request.method == "POST":
        # Handle post creation
        if 'content' in request.POST:
            post_form = PostForm(request.POST, request.FILES)
            if post_form.is_valid():
                new_post = post_form.save(commit=False)
                new_post.user = request.user
                new_post.save()
                messages.success(request, "Post created successfully!")
                return redirect('subcategory_online-community')
            else:
                messages.error(request, "Failed to create the post. Please check the form.")

        # Handle comment creation
        elif 'comment_content' in request.POST:
            post_id = request.POST.get('post_id')  # Safely retrieve 'post_id'
            if post_id:
                try:
                    post = Post.objects.get(id=post_id)
                    Comment.objects.create(
                        post=post,
                        user=request.user,
                        content=request.POST['comment_content']
                    )
                    messages.success(request, "Comment added successfully!")
                except Post.DoesNotExist:
                    messages.error(request, "The post you're trying to comment on does not exist.")
            else:
                messages.error(request, "Post ID is missing.")
            return redirect('subcategory_online-community')

    # Render the page with posts, profiles, and forms
    return render(request, 'pages/subcategory_online-community.html', {
        'posts': posts,
        'profile': profile,
        'post_form': PostForm(),
        'comment_form': CommentForm(),
    })


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)  # Ensure the post belongs to the logged-in user
    
    if request.method == 'POST':
        post.delete()  # Delete the post if the request is POST
        return redirect('subcategory_online-community')  # Redirect to the online community page after deletion

    # If the request is GET, we should not return anything, as the deletion form handles the confirmation
    return redirect('subcategory_online-community')  # Optionally, you can just redirect without rendering

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)  # Ensure the comment belongs to the logged-in user
    
    if request.method == 'POST':
        comment.delete()  # Delete the comment if the request is POST
        return redirect('subcategory_online-community')  # Redirect to the online community page after deletion

    # If the request is GET, we should not return anything, as the deletion form handles the confirmation
    return redirect('subcategory_online-community')  # Optionally, you can just redirect without rendering


def createprof(request):
    if request.method == 'POST':
        form = PsychologistSignUpForm(request.POST, request.FILES) 
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  
    else:
        form = PsychologistSignUpForm()
    
    return render(request, 'pages/createprof.html', {'form': form})



@login_required
def todo_list(request):
    # Filter tasks that are not deleted and completed
    tasks = Task.objects.filter(deleted=False)
    completed_task_count = tasks.filter(is_completed=True).count()  # Count completed tasks
    total_tasks = tasks.count()  # Total number of tasks

    # Fetch tasks that are marked as deleted
    deleted_tasks = Task.objects.filter(deleted=True)
    
    return render(request, 'pages/subcategory_to-do-list.html', {
        'tasks': tasks,
        'completed_task_count': completed_task_count,
        'total_tasks': total_tasks,
        'deleted_tasks': deleted_tasks  # Pass deleted tasks to the template
    })

@login_required
def add_task(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        notes = request.POST.get('notes')
        deadline = request.POST.get('deadline')
        priority = request.POST.get('priority')
        category = request.POST.get('category')

        # Create a new task and assign the current logged-in user to the 'user' field
        task = Task.objects.create(
            title=title,
            notes=notes,
            deadline=deadline,
            priority=priority,
            category=category,
            user=request.user  # Assign the logged-in user to the task
        )
    return redirect('subcategory_to-do-list') 



def update_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    
    # Toggle the completed status
    task.is_completed = not task.is_completed
    
    # Adjust the score based on the new completion status
    if task.is_completed:
        task.score += 1  # Increment score when task is marked as completed
    else:
        task.score = max(task.score - 1, 0)  # Optionally decrement score when unmarking, ensuring it doesn't go below 0
    
    task.save()
    return JsonResponse({'success': True, 'is_completed': task.is_completed, 'score': task.score})

@login_required
def delete_task(request, task_id):
    try:
        task = Task.objects.get(id=task_id, user=request.user)
        task.deleted = True
        task.save()
        return JsonResponse({'success': True})
    except Task.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Task not found'})







def exercise_view(request):
    return render(request, 'pages/subcategory_exercise.html')

@csrf_exempt
def save_exercise_data(request):
    if request.method == "POST":
        data = json.loads(request.body)
        exercise = data.get('exercise')
        time_taken = data.get('time_taken')
        score = data.get('score')

        # Save data in the database
        completion = ExerciseCompletion.objects.create(
            user=request.user,
            exercise=exercise,
            score=score,
            time_taken=time_taken
        )

        return JsonResponse({'success': True, 'exercise': completion.exercise})

    return JsonResponse({'success': False}, status=400)

@login_required
def yoga_view(request):
    return render(request, 'pages/subcategory_yoga.html')


@csrf_exempt
def save_yoga_data(request):
    if request.method == "POST":
        data = json.loads(request.body)
        exercise = data.get('exercise')
        time_taken = data.get('time_taken')
        score = data.get('score')

        # Save data in the YogaCompletion model
        completion = YogaCompletion.objects.create(
            user=request.user,
            exercise=exercise,
            score=score,
            time_taken=time_taken,
            completed=True,  # Set completed to True
        )

        return JsonResponse({'success': True, 'exercise': completion.exercise})

    return JsonResponse({'success': False}, status=400)




@login_required
def defusion_game(request):
    # Initialize score if not post data exists
    score = 0
    if request.method == 'POST':
        score = int(request.POST.get('score', 0))
    return render(request, 'pages/subcategory_defusion-technique.html', {'score': score})

@login_required
def save_defusion_score(request):
    if request.method == 'POST':
        score = request.POST.get('score')
        if score:
            # Save score to the database
            Defusion.objects.create(user=request.user, score=score)
        return redirect('defusion_game')  




@login_required
def validation(request):
    if request.method == 'POST':
        form = ValidationForm(request.POST)
        if form.is_valid():
            validation = form.save(commit=False)
            validation.user = request.user  # Associate the current user with the validation
            validation.save()
            return redirect('validation')  # Change this to your success URL
    else:
        form = ValidationForm()

    return render(request, 'pages/validation.html', {'form': form})



@login_required
def mood(request):
    """ Renders the calendar page. """
    return render(request, 'pages/mood.html')

@csrf_exempt
@login_required  # Ensure only logged-in users can save mood entries
def save_mood(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        date = data.get('date')
        mood = data.get('mood')
        note = data.get('note', '')  # Retrieve the optional note

        if date and mood:
            # Check if a mood entry already exists for the current user on the specified date
            existing_entry = MoodEntry.objects.filter(user=request.user, date=date).first()

            if existing_entry:
                return JsonResponse({'status': 'error', 'message': 'Mood entry already exists for this date'})

            # If no existing entry, create a new mood entry
            mood_entry = MoodEntry.objects.create(
                user=request.user,  # Associate with the current user
                date=date,
                mood=mood,
                note=note  # Include the note if provided
            )

            return JsonResponse({'status': 'success', 'created': True})

        return JsonResponse({'status': 'error', 'message': 'Invalid data'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def get_moods(request):
    """ Fetches mood entries for the logged-in user for displaying on the calendar. """
    mood_entries = MoodEntry.objects.filter(user=request.user)  # Fetch moods for the current user
    moods = {
        entry.date.strftime('%Y-%m-%d'): {
            'mood': entry.mood,
            'note': entry.note
        }
        for entry in mood_entries
    }
    return JsonResponse(moods)


@login_required
def journal(request):
    # Filter journal entries by the logged-in user
    entries = JournalEntry.objects.filter(user=request.user).order_by('-created_at')

    if request.method == 'POST':
        form = JournalEntryForm(request.POST, instance=None)

        if form.is_valid():
            # Save the entry with the user assigned to it
            journal_entry = form.save(commit=False)
            journal_entry.user = request.user
            journal_entry.save()
            return redirect('subcategory_journal')  # Redirect to the journal page after saving

    else:
        form = JournalEntryForm()

    return render(request, 'pages/subcategory_journal.html', {
        'form': form,
        'entries': entries
    })

@login_required
def edit_journal(request, entry_id):
    entry = get_object_or_404(JournalEntry, id=entry_id, user=request.user)
    
    if request.method == 'POST':
        form = JournalEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect('subcategory_journal')
    else:
        form = JournalEntryForm(instance=entry)

    return render(request, 'pages/subcategory_journal.html', {'form': form})

@login_required
def delete_journal(request, entry_id):
    entry = get_object_or_404(JournalEntry, id=entry_id, user=request.user)
    
    if request.method == 'POST':
        entry.delete()
        return redirect('subcategory_journal')
    
    return render(request, 'pages/subcategory_journal.html') 


def is_admin(user):
    return user.is_superuser

@login_required
def analytics(request):
    # Subquery to get the latest response for each user
    latest_responses_subquery = GAD7Response.objects.filter(
        user=OuterRef('user')
    ).order_by('-timestamp').values('id')[:1]

    # Fetch only the latest responses
    latest_responses = GAD7Response.objects.filter(
        id__in=Subquery(latest_responses_subquery)
    )

    # Initialize severity counts
    severity_counts = {
        'Minimal Anxiety': 0,
        'Mild Anxiety': 0,
        'Moderate Anxiety': 0,
        'Severe Anxiety': 0
    }

    # Count severity levels from the latest responses
    for response in latest_responses:
        severity = response.severity
        if severity in severity_counts:
            severity_counts[severity] += 1
        total_users = Profile.objects.count() - 9

        total_superusers = User.objects.filter(is_superuser=True).count()

        total_staff = Psychologist.objects.count()


    # Pass the necessary data to the template
    return render(request, 'pages/analytics.html', {
        'users': latest_responses,
        'severity_counts': severity_counts,
        'total_users': total_users,
        'total_superusers': total_superusers,
        'total_staff': total_staff,
    })

@login_required
def viewpatient(request):
    # Get the search query from the request (if any)
    search_query = request.GET.get('search', '')

    # Get the distinct users who have submitted a GAD7 response
    patients = GAD7Response.objects.values('user').distinct()

    latest_responses = []
    for patient in patients:
        latest_response = GAD7Response.objects.filter(user=patient['user']).order_by('-timestamp').first()
        if latest_response:
            # Fetch tasks for this patient and calculate total task score
            tasks = Task.objects.filter(user=patient['user'], is_completed=True)
            total_task_score = sum(task.score for task in tasks)

            # Get Defusion entries and calculate total defusion score
            defusion_entries = Defusion.objects.filter(user=patient['user'])
            total_defusion_score = sum(entry.score for entry in defusion_entries)

            # Get Exercise and Yoga Completion data and calculate total scores
            exercises = ExerciseCompletion.objects.filter(user=patient['user'])
            total_exercise_score = sum(exercise.score for exercise in exercises)

            # Get Yoga completion data
            yoga = YogaCompletion.objects.filter(user=patient['user'])
            total_yoga_score = sum(yoga.score for yoga in yoga)

            # Fetch all other data (like Distraction scores, MindManagement scores, etc.)
            distraction_entries = Distraction.objects.filter(user=patient['user'])
            total_distraction_score = sum(entry.score for entry in distraction_entries)
            mind_management_scores = MindManagement.objects.filter(user=patient['user'])
            total_mind_management_score = sum(score.score for score in mind_management_scores)

            # Fetch Relaxation scores for the patient
            relaxation_scores = RelaxationScore.objects.filter(user=patient['user'])
            total_relaxation_score = sum(relaxation.score for relaxation in relaxation_scores)

            # Calculate total score across all models
            total_score = (total_task_score + total_defusion_score + total_exercise_score +
                           total_yoga_score + total_distraction_score + total_mind_management_score +
                           total_relaxation_score)

            # Add the total score and other individual scores to the response
            latest_response.total_score = total_score
            latest_response.total_task_score = total_task_score
            latest_response.total_defusion_score = total_defusion_score
            latest_response.total_exercise_score = total_exercise_score
            latest_response.total_yoga_score = total_yoga_score
            latest_response.total_distraction_score = total_distraction_score
            latest_response.total_mind_management_score = total_mind_management_score
            latest_response.total_relaxation_score = total_relaxation_score  # Add relaxation score here
            latest_response.exercises = exercises
            latest_response.yoga = yoga
            latest_response.relaxation_scores = relaxation_scores  # Add relaxation scores here

            latest_responses.append(latest_response)

    if search_query:
        latest_responses = [
            response for response in latest_responses
            if search_query.lower() in response.user.first_name.lower() or search_query.lower() in response.user.last_name.lower() or search_query.lower() in response.user.email.lower()
        ]

    context = {
        'latest_responses': latest_responses,
        'search_query': search_query,
    }

    return render(request, 'pages/viewpatient.html', context)




@login_required
def gad7(request):
    # Redirect staff users (excluding superusers) to the home page
    if request.user.is_staff and not request.user.is_superuser:
        return redirect('home')

    if request.method == 'POST':
        # Collect the responses from the form
        responses = {
            f'q{index + 1}': int(value) for index, value in enumerate(request.POST.getlist('questions[]'))
        }

        # Calculate the total GAD-7 score
        total_score = sum(responses.values())

        # Determine severity based on the total score
        if total_score <= 4:
            severity = "Minimal Anxiety"
        elif total_score <= 9:
            severity = "Mild Anxiety"
        elif total_score <= 14:
            severity = "Moderate Anxiety"
        else:
            severity = "Severe Anxiety"

        # Create a new GAD-7 response for the user each time they submit the form
        GAD7Response.objects.create(
            user=request.user,  # Associate the response with the current user
            responses=responses,  # Save the user's answers
            severity=severity  # Save the calculated severity
        )

        # Notify the user that their response was saved
        return redirect('profile')  # Redirect to the home page after submission

    # List of GAD-7 questions
    questions = [
        {"text": "Feeling nervous, anxious, or on edge?"},
        {"text": "Not being able to stop or control worrying?"},
        {"text": "Worrying too much about different things?"},
        {"text": "Trouble relaxing?"},
        {"text": "Being so restless that it's hard to sit still?"},
        {"text": "Becoming easily annoyed or irritable?"},
        {"text": "Feeling afraid as if something awful might happen?"}
    ]
    
    # Get the latest response for the logged-in user
    latest_response = GAD7Response.objects.filter(user=request.user).order_by('-timestamp').first()

    # Pass the latest response to the template
    context = {
        'questions': questions,
        'latest_response': latest_response  # Add the latest response to the context
    }
    
    # Render the GAD-7 form with the questions and latest response
    return render(request, 'pages/gad7.html', context)



@login_required
def chat_view(request, psychologist_id):
    psychologist = get_object_or_404(Psychologist, id=psychologist_id)

    # Retrieve messages between the user and the psychologist, ordered by timestamp
    messages = Message.objects.filter(
        sender__in=[request.user, psychologist.user],
        recipient__in=[request.user, psychologist.user]
    ).order_by('timestamp')

    # Mark messages as read for the logged-in user (or recipient)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            # Create a new message
            message = Message.objects.create(
                sender=request.user,
                recipient=psychologist.user,
                content=content,
                timestamp=timezone.now()
            )

            # Mark all messages from the current user to the psychologist as 'read'
            messages.filter(recipient=request.user, is_read=False).update(is_read=True)

            # Return the new message details in a JSON response
            return JsonResponse({
                'status': 'success',
                'sender': message.sender.username,
                'message': message.content,
                'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            })

    # Fetch unread messages for the logged-in user
    unread_messages = messages.filter(recipient=request.user, is_read=False)

    # Pass the messages and unread messages to the template
    return render(request, 'pages/chat.html', {
        'psychologist': psychologist,
        'messages': messages,
        'unread_messages': unread_messages,  # Pass unread messages to the template for notification
    })

@login_required
def psychprofile(request, psychologist_id, user_id=None):
    # Fetch the psychologist instance or return 404 if not found
    psychologist = get_object_or_404(Psychologist, id=psychologist_id)
    
    if user_id:
        # Fetch the user that the psychologist is chatting with
        user = get_object_or_404(User, id=user_id)
        # Fetch messages between the psychologist and this specific user
        messages = Message.objects.filter(
            sender__in=[user, psychologist.user],
            recipient__in=[user, psychologist.user]
        ).order_by('timestamp')
    else:
        messages = []

    if request.method == 'POST':
        content = request.POST.get('content')
        recipient_id = request.POST.get('recipient_id')  # The recipient is the user you are replying to

        if recipient_id and content:
            try:
                recipient = get_object_or_404(User, id=recipient_id)
                message = Message.objects.create(
                    sender=request.user,        # The current logged-in user (the user sending the reply)
                    recipient=recipient,        # The user the psychologist is replying to
                    content=content             # The content of the message (the reply)
                )
                message.save()  # Save the message to the database
                return redirect('psychprofile', psychologist_id=psychologist_id, user_id=recipient_id)

            except User.DoesNotExist:
                return render(request, 'pages/psychprofile.html', {
                    'psychologist': psychologist,
                    'messages': messages,
                    'error': 'Recipient user not found.',
                })
        else:
            return render(request, 'pages/psychprofile.html', {
                'psychologist': psychologist,
                'messages': messages,
                'error': 'Please provide a valid message and recipient.',
            })

    return render(request, 'pages/psychprofile.html', {
        'psychologist': psychologist,
        'messages': messages,
        'user_id': user_id,
    })

@login_required
def psychview(request, psychologist_id):
    psychologist = get_object_or_404(Psychologist, id=psychologist_id)

    if request.user != psychologist.user:
        return HttpResponseForbidden("You are not authorized to view this page.")

    # Fetch the latest availability status
    availability = Availability.objects.filter(user=psychologist).latest('timestamp') if psychologist.availability_set.exists() else None

    # Print to check if availability is None or has a value
    print("Availability:", availability)

    # Fetch messages as before
    latest_messages = Message.objects.filter(
        recipient=psychologist.user
    ).values('sender').annotate(latest_message=Max('timestamp')).order_by('latest_message')

    messages = Message.objects.filter(
        recipient=psychologist.user, timestamp__in=[m['latest_message'] for m in latest_messages]
    ).order_by('timestamp')

    for message in messages:
        try:
            severity = GAD7Response.objects.filter(user=message.sender).latest('timestamp').severity
            message.severity = severity
        except GAD7Response.DoesNotExist:
            message.severity = "No Severity Data"

    # Pass psychologist, messages, and availability to the template
    return render(request, 'pages/psychview.html', {
        'psychologist': psychologist,
        'messages': messages,
        'availability': availability,  # Ensure this is passed
    })



@login_required
def edit_psychview(request, psychologist_id):
    psychologist = get_object_or_404(Psychologist, id=psychologist_id)

    # Ensure the logged-in user is the psychologist
    if request.user != psychologist.user:
        return HttpResponseForbidden("You are not authorized to edit this profile.")

    if request.method == 'POST':
        form = PsychologistProfileForm(request.POST, request.FILES, instance=psychologist)
        if form.is_valid():
            form.save()
            return redirect('psychview', psychologist_id=psychologist.id)
    else:
        form = PsychologistProfileForm(instance=psychologist)

    return render(request, 'pages/edit_psychview.html', {'form': form, 'psychologist': psychologist})


@login_required
def admin_message_user(request, user_id):
    # Ensure the logged-in user is a superuser (admin)
    if not request.user.is_superuser:
        return redirect('home')  # Redirect to home if not admin

    # Get the user the admin is messaging
    user = get_object_or_404(User, id=user_id)

    # Get all messages between the admin and the user
    messages = Message.objects.filter(
        sender__in=[user, request.user],
        recipient__in=[user, request.user]
    ).order_by('timestamp')

    # Handle unread messages (optional)
    unread_messages = Message.objects.filter(
        recipient=user, 
        is_read=False
    )

    # Mark messages as read (optional behavior for user to mark messages as read)
    if unread_messages.exists():
        unread_messages.update(is_read=True)

    # Handle sending a new message (POST request)
    if request.method == 'POST':
        content = request.POST.get('content')
        
        if content:
            # Create a new message where the admin is the sender and the target user is the recipient
            message = Message.objects.create(
                sender=request.user,         # The admin is sending the message
                recipient=user,               # The target user is the recipient
                content=content              # The content of the message
            )
            message.save()

            # Redirect to the same page after sending the message
            return redirect('admin_message_user', user_id=user.id)

    # Render the page with the messages and form
    return render(request, 'pages/admin_message_user.html', {
        'user': user,
        'messages': messages,
        'unread_messages': unread_messages,
    })



@login_required
def accept_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)

    # Ensure that only the psychologist recipient can accept the message
    if request.user != message.recipient:
        return HttpResponseForbidden("You are not authorized to accept this message.")

    message.is_accepted = True
    message.status = Message.ACCEPTED  # Update status to accepted
    message.save()

    return redirect('psychview', psychologist_id=message.recipient.psychologist.id)

@login_required
def reject_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)

    # Ensure that only the psychologist recipient can reject the message
    if request.user != message.recipient:
        return HttpResponseForbidden("You are not authorized to reject this message.")

    message.is_accepted = False
    message.status = Message.REJECTED  # Update status to rejected
    message.save()

    return redirect('psychview', psychologist_id=message.recipient.psychologist.id)

@login_required
def pending_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)

    # Ensure that only the psychologist recipient can update the message status
    if request.user != message.recipient:
        return HttpResponseForbidden("You are not authorized to update this message.")

    message.is_accepted = None  # Set to None to represent a pending status
    message.status = Message.PENDING  # Update the status to 'Pending'
    message.save()

    return redirect('psychview', psychologist_id=message.recipient.psychologist.id)

def hotline(request):
    hotline = Hotline.objects.all()  # Fetch all hotline entries
    return render(request, 'pages/hotline.html', {'hotline': hotline})

def add_hotline(request):
    if request.method == 'POST':
        form = HotlineForm(request.POST)
        if form.is_valid():
            form.save()  # Save the new hotline
            return redirect('hotline')  # Redirect to hotline list page
    else:
        form = HotlineForm()

    return render(request, 'pages/add_hotline.html', {'form': form})

def edit_hotline(request, hotline_id):
    hotline = get_object_or_404(Hotline, id=hotline_id)
    if request.method == 'POST':
        form = HotlineForm(request.POST, instance=hotline)
        if form.is_valid():
            form.save()  # Save the updated hotline
            return redirect('hotline')  # Redirect to hotline list page
    else:
        form = HotlineForm(instance=hotline)

    return render(request, 'pages/edit_hotline.html', {'form': form, 'hotline': hotline})

def delete_hotline(request, hotline_id):
    hotline = get_object_or_404(Hotline, id=hotline_id)
    hotline.delete()  # Delete the hotline
    return redirect('hotline')





def distraction(request):
    return render(request, 'pages/subcategory_distraction.html')

@csrf_exempt
def submit_score(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        scores = data.get('scores', [])

        if not scores:
            return JsonResponse({"message": "No scores provided!"}, status=400)

        user = request.user if request.user.is_authenticated else None

        # Save all the scores regardless of duplicates
        for score in scores:
            if score == 20:  # Check for the desired score to save
                # Always save this score, even if it already exists
                Distraction.objects.create(user=user, score=score)

        return JsonResponse({"message": "Scores saved successfully!"}, status=200)

    return JsonResponse({"message": "Invalid request method!"}, status=405)


@login_required
def mind_management(request):
    # Retrieve or create a Mind object for the logged-in user
    mind, created = Mind.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Get score from the POST data
        new_score = request.POST.get('score', 0)
        
        # Update the score in the database
        mind.score = new_score
        mind.save()

        return JsonResponse({'status': 'success', 'score': mind.score})
    
    # For GET requests, send the current score to the frontend
    return render(request, 'pages/subcategory_mind-management.html', {'score': mind.score})

def save_score(request):
    if request.method == "POST":
        user = request.user
        score = int(request.POST.get("score", 1))

        # Save the score to the database
        mind_management = MindManagement.objects.create(user=user, score=score)

        return JsonResponse({"message": "Score saved successfully!"})

    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def bodyscan(request):
    if request.method == "POST":
        score = request.POST.get("score", "").strip()  # Get score from POST and remove whitespace

        if not score.isdigit():  # Check if the score is a valid number
            return HttpResponse("Invalid score value", status=400)

        score = int(score)  # Convert the score to an integer

        # Save the score to the database
        RelaxationScore.objects.create(user=request.user, score=score)

        return redirect('bodyscan') 

    return render(request, 'pages/subcategory_body-scan-meditation.html')


@login_required
def set_availability(request, psychologist_id):
    psychologist = get_object_or_404(Psychologist, id=psychologist_id)

    if request.user != psychologist.user:
        return HttpResponseForbidden("You are not authorized to set availability for this psychologist.")

    if request.method == 'POST':
        availability_status = request.POST.get('availability')

        # Save or update the availability status
        Availability.objects.update_or_create(
            user=psychologist,
            defaults={'status': availability_status}
        )

    # Redirect back to the psychview page
    return redirect('psychview', psychologist_id=psychologist_id)

