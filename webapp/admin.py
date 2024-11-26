from django.contrib import admin
from .models import *

admin.site.register(Profile)
admin.site.register(MoodEntry)
admin.site.register(Feedback)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Message)
admin.site.register(Validation)
admin.site.register(JournalEntry)
admin.site.register(GAD7Response)
admin.site.register(Hotline)
admin.site.register(Availability)

#coping
admin.site.register(Task)
admin.site.register(ExerciseCompletion)
admin.site.register(YogaCompletion)
admin.site.register(Defusion)
admin.site.register(Quiz)
admin.site.register(UserQuiz)
admin.site.register(Distraction)
admin.site.register(RelaxationScore)
admin.site.register(MindManagement)

class SubcategoryInline(admin.TabularInline):
    model = Subcategory
    extra = 1

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    inlines = [SubcategoryInline]

class SubcategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Category, CategoryAdmin)
admin.site.register(Subcategory, SubcategoryAdmin)

class PsychologistAdmin(admin.ModelAdmin):
    list_display = ('user', 'license_number', 'is_approved')
    list_filter = ('is_approved',)

admin.site.register(Psychologist, PsychologistAdmin)