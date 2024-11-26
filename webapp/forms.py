from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *

class CreationForm(UserCreationForm):
    # User fields
    first_name = forms.CharField(max_length=30, required=True, help_text='First name')
    last_name = forms.CharField(max_length=30, required=True, help_text='Last name')
    email = forms.EmailField(max_length=254, required=True, help_text='Enter a valid email address')

    # Profile fields
    image = forms.ImageField(required=False, help_text='Upload a profile image')  # Optional image field
    twitter = forms.URLField(max_length=255, required=False, help_text='Twitter profile link')
    facebook = forms.URLField(max_length=255, required=False, help_text='Facebook profile link')
    instagram = forms.URLField(max_length=255, required=False, help_text='Instagram profile link')
    address = forms.CharField(max_length=255, required=False, help_text='Address')
    phone_number = forms.CharField(max_length=17, required=False, help_text="Phone number in the format: '+999999999'")

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        # Save the User part of the form
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()

            # Create or update the Profile for the user
            profile, created = Profile.objects.get_or_create(user=user)
            
            # Save the Profile part of the form
            profile.image = self.cleaned_data.get('image')
            profile.twitter = self.cleaned_data.get('twitter')
            profile.facebook = self.cleaned_data.get('facebook')
            profile.instagram = self.cleaned_data.get('instagram')
            profile.address = self.cleaned_data.get('address')
            profile.phone_number = self.cleaned_data.get('phone_number')
            profile.save()

        return user


class ProfileEditForm(forms.ModelForm):
    # User fields
    first_name = forms.CharField(max_length=30, required=True, help_text='First name')
    last_name = forms.CharField(max_length=30, required=True, help_text='Last name')
    email = forms.EmailField(max_length=254, required=True, help_text='Enter a valid email address')

    class Meta:
        model = Profile
        fields = ['image', 'twitter', 'facebook', 'instagram', 'address', 'phone_number', 'grade']

    def __init__(self, *args, **kwargs):
        # Get the user instance
        self.user = kwargs.pop('user', None)
        super(ProfileEditForm, self).__init__(*args, **kwargs)

        # Initialize user fields with the user's data
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)

        # Update user fields
        if self.user:
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            self.user.email = self.cleaned_data['email']
            if commit:
                self.user.save()

        if commit:
            profile.save()
        return profile
        

        
class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'image', 'description']

class SubcategoryForm(forms.ModelForm):
    class Meta:
        model = Subcategory
        fields = ['category', 'name', 'image', 'description', 'color']
               

class StaffUserSignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # Hash the password
        user.is_staff = True  # Set the user as staff
        if commit:
            user.save()
        return user
    
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'placeholder': 'Add a comment...', 'rows': 2}),
        }

class ProfessionalSignUpForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput())
    email = forms.EmailField()

    class Meta:
        model = Professional
        fields = ['first_name', 'last_name', 'bio', 'expertise', 'image']

class ValidationForm(forms.ModelForm):
    class Meta:
        model = Validation
        fields = ['subcategory', 'rating', 'feedback']
        widgets = {
            'feedback': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Your feedback...'}),
        }

    subcategory = forms.ModelChoiceField(queryset=Subcategory.objects.all(), label="Select Subcategory")
    
class JournalEntryForm(forms.ModelForm):
    class Meta:
        model = JournalEntry
        fields = ['title', 'content']
        


class PsychologistSignUpForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Enter your first name"})
    )
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Enter your last name"})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "Enter your email address"})
    )
    license_number = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Enter your license number"})
    )
    qualification = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={"placeholder": "Enter your address"})
    )
    years_of_experience = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={"placeholder": "Enter years of experience"})
    )
    area_of_expertise = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={"placeholder": "Enter your area of expertise"})
    )
    contact_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={"placeholder": "Enter your contact number"})
    )
    image = forms.ImageField(
        required=False
    )
    bio = forms.CharField(
        widget=forms.Textarea(attrs={"placeholder": "Write a short bio about yourself"}), 
        required=False
    )


    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            psychologist = Psychologist.objects.create(
                user=user,
                license_number=self.cleaned_data['license_number'],
                qualification=self.cleaned_data['qualification'],
                years_of_experience=self.cleaned_data['years_of_experience'],
                area_of_expertise=self.cleaned_data['area_of_expertise'],
                contact_number=self.cleaned_data['contact_number'],
                image=self.cleaned_data.get('image'),
                bio=self.cleaned_data.get('bio')  # Save the bio
            )
        return user


class PsychologistProfileForm(forms.ModelForm):
    class Meta:
        model = Psychologist
        fields = ['years_of_experience', 'contact_number', 'qualification','area_of_expertise', 'bio', 'image']
        
class HotlineForm(forms.ModelForm):
    class Meta:
        model = Hotline
        fields = ['title', 'contact', 'description']

class DefusionGameScoreForm(forms.ModelForm):
    class Meta:
        model = Defusion
        fields = ['score']

class RelaxationScoreForm(forms.ModelForm):
    class Meta:
        model = RelaxationScore
        fields = ['score']

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'notes', 'deadline', 'priority', 'category']

