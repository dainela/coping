from django.db import models
from django.core.validators import MaxValueValidator
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.validators import RegexValidator
from django.utils.timezone import now

class Profile(models.Model): 
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='pictures/', null=True, blank=True)
    
    # Social media links
    twitter = models.URLField(max_length=255, null=True, blank=True)
    facebook = models.URLField(max_length=255, null=True, blank=True)
    instagram = models.URLField(max_length=255, null=True, blank=True)
    
    # Contact information
    address = models.CharField(max_length=255, null=True, blank=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)  # For international phone numbers

    # New fields for grade and section
    grade = models.CharField(max_length=20, null=True, blank=True)  # Adjust max_length as needed
    completed_gad7 = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
        
 
class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link feedback to a user
    email_address = models.EmailField(max_length=254)  # Email field for validation
    feed = models.CharField(max_length=500, null=False, blank=False)  # Feedback content
    date = models.DateTimeField(default=now)  # Automatically set the date when feedback is created

    def __str__(self):
        return f"{self.user.username} - {self.feed[:50]} ({self.date.strftime('%Y-%m-%d')})"

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    image = models.ImageField(upload_to='pictures/')
    description = models.CharField(max_length=1000, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    # Define color choices
    LIGHT_BLUE = '#ADD8E6'
    LIGHT_YELLOW = '#FFFFE0'
    LIGHT_VIOLET = '#D3A6FF'
    LIGHT_PINK = '#FFB6C1'

    COLOR_CHOICES = [
        (LIGHT_BLUE, 'Light Blue'),
        (LIGHT_YELLOW, 'Light Yellow'),
        (LIGHT_VIOLET, 'Light Violet'),
        (LIGHT_PINK, 'Light Pink'),
    ]

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    image = models.ImageField(upload_to='pictures/')
    description = models.CharField(max_length=1000, unique=True)
    color = models.CharField(max_length=7, choices=COLOR_CHOICES, default=LIGHT_BLUE)  # Color choices field

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Validation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # Rating from 1 to 5
    feedback = models.TextField()

    def __str__(self):
        return f"{self.user.username} - {self.subcategory.name} - {self.rating}"
    
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='post_images/', null=True, blank=True) 
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.user.username} - {self.timestamp}'
    
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
    upvotes = models.PositiveIntegerField(default=0)
    downvotes = models.PositiveIntegerField(default=0)

    def total_votes(self):
        return self.upvotes - self.downvotes

    def __str__(self):
        return f'{self.user.username} - {self.content[:20]}'
    
class Professional(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    bio = models.CharField(max_length=500, null=True)
    expertise = models.CharField(max_length=5000, null=True)
    image = models.ImageField(upload_to='pictures/')
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


    #coping techniques 


class Task(models.Model):
    title = models.CharField(max_length=200)
    notes = models.TextField(blank=True, null=True)
    deadline = models.DateTimeField(null=True, blank=True)
    priority_choices = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    priority = models.CharField(max_length=6, choices=priority_choices, default='low')
    category_choices = [
        ('work', 'Work'),
        ('personal', 'Personal'),
        ('shopping', 'Shopping'),
    ]
    category = models.CharField(max_length=10, choices=category_choices, default='work')
    is_completed = models.BooleanField(default=False)
    completion_time = models.DateTimeField(null=True, blank=True)
    deleted = models.BooleanField(default=False)  # Mark tasks as deleted
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link tasks to the user
    score = models.IntegerField(default=0)  # New field to track the score for the task

    def __str__(self):
        return self.title


    
MOOD_CHOICES = [
    ('happy', '😊 Happy'),
    ('neutral', '😐 Neutral'),
    ('sad', '😞 Sad'),
    ('excited', '😄 Excited'),
    ('anxious', '😟 Anxious'),
]

class ExerciseCompletion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.CharField(max_length=255)
    score = models.IntegerField(default=0)
    time_taken = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.exercise} - {self.score}"

class YogaCompletion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.CharField(max_length=255)
    time_taken = models.CharField(max_length=50)
    score = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.exercise} - Completed: {self.completed}"


class Defusion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()
    date_played = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.score} - {self.date_played}"

class MindManagement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mind_management_scores")
    score = models.IntegerField(default=0)  # Total score for the user
    timestamp = models.DateTimeField(auto_now_add=True)  # When the score was recorded

    def str(self):
        return f"{self.user.username} - Score: {self.score}"







class MoodEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()  # The selected date
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES)
    note = models.TextField(blank=True, null=True)  # Optional note field

    def __str__(self):
        return f"{self.user.username}: {self.get_mood_display()} on {self.date}"
    
    
class JournalEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
class GAD7Response(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # ForeignKey to allow multiple entries per user
    responses = models.JSONField()
    severity = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.severity} ({self.timestamp})"

class Psychologist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=100, unique=True)
    qualification = models.CharField(max_length=255)
    years_of_experience = models.PositiveIntegerField()
    area_of_expertise = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20)
    image = models.ImageField(upload_to='psychologist_images/', default='default_profile.jpg', null=True, blank=True)
    bio = models.TextField(blank=True, null=True) 
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
    


class Message(models.Model):
    PENDING = 'pending'
    READ = 'read'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (READ, 'Read'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
    ]
    
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=PENDING
    )
    is_read = models.BooleanField(default=False) 

    def __str__(self):
        return f"{self.sender.username} to {self.recipient.username} at {self.timestamp} (Status: {self.status})"
    


class Hotline(models.Model):
    title = models.CharField(max_length=255)
    contact = models.CharField(max_length=255)  # Fixed the missing field type
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.title

class Quiz(models.Model):
    question = models.CharField(max_length=255)
    option_a = models.CharField(max_length=100)
    option_b = models.CharField(max_length=100)
    option_c = models.CharField(max_length=100)
    option_d = models.CharField(max_length=100)
    correct_option = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])

    def __str__(self):
        return self.question

class UserQuiz(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {'Completed' if self.completed else 'Pending'}"

class Distraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Associate score with a user
    score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Score: {self.score} at {self.created_at}"

class Mind(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)  
    
    def __str__(self):
        return f"Mind Management Score for {self.user.username}"

class RelaxationScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.score} - {self.date}"

class Availability(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('unavailable', 'Unavailable'),
    ]
    user = models.ForeignKey(Psychologist, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.status