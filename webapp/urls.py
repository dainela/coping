from django.urls import path 
from webapp import views
from django.conf import settings
from django.conf.urls.static import static
from .views import *
from django.contrib.auth.views import LoginView


urlpatterns = [
    path ('', views.home, name="home"),
    path ('navbar/', views.navbar, name="navbar"),
    path ('about/', views.about, name="about"),
    path ('feedback/', views.feedback, name="feedback"),
    path ('prof/', views.prof, name="prof"), 
    path ('viewfeed/', views.viewfeed, name="viewfeed"),
    path ('viewprof/', views.viewprof, name="viewprof"),
    
    path ('createprof/', views.createprof, name="createprof"),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),  
    path('psychprofile/', psychprofile, name='psychprofile'), 
    path('viewpsych/', views.viewpsych, name='viewpsych'), 
    path('viewpatient/', views.viewpatient, name='viewpatient'),    
    path('set_availability/<int:psychologist_id>/', set_availability, name='set_availability'),

    path ('signin/', views.signin, name="signin"),
    path ('signup/', views.signup, name="signup"),
    path ('signout/', views.signout, name="signout"),
    path('analytics/', analytics, name='analytics'),
    
    path('mood/', views.mood, name='mood'),
    path('save_mood/', views.save_mood, name='save_mood'),
    path('get_moods/', views.get_moods, name='get_moods'),
    
    path ('staff/', staff, name="staff"),
    path('approve_psychologist/<int:psychologist_id>/', approve_psychologist, name='approve_psychologist'),
    path('reject_psychologist/<int:psychologist_id>/', reject_psychologist, name='reject_psychologist'),
    path('categories/problem-focused/to-do-list/', views.todo_list, name='subcategory_to-do-list'),
    
    path('categories/emotion-focused/journal/', views.journal, name='subcategory_journal'),
    path('categories/emotion-focused/journal/edit/<int:entry_id>/', views.edit_journal, name='edit_journal_entry'),
    path('categories/emotion-focused/journal/delete/<int:entry_id>/', views.delete_journal, name='delete_journal_entry'),
    

    #coping techniques 
    path('add/', views.add_task, name='add_task'),
    path('update/<int:task_id>/', views.update_task, name='update_task'),
    path('delete/<int:task_id>/', views.delete_task, name='delete_task'),


    path('categories/problem-focused/exercise/save/', views.save_exercise_data, name='save_exercise'),
    path('categories/problem-focused/exercise/', views.exercise_view, name='exercise_view'),

    path('categories/emotion-focused/yoga/save/', views.save_yoga_data, name='save_yoga'),
    path('categories/emotion-focused/yoga/', views.yoga_view, name='yoga_view'),

    path('categories/meaning-focused/defusion-technique/', views.defusion_game, name='defusion_game'),
    path('categories/meaning-focused/defusion-technique/save_defusion_score/', views.save_defusion_score, name='save_defusion_score'),



    path('categories/meaning-focused/distraction/', views.distraction, name='distraction'),
    path('submit-score/', views.submit_score, name='submit_score'),

    path('categories/meaning-focused/cognitive-reframing/', views.mind_management, name='mind_management'),

    path('categories/emotion-focused/body-scan-meditation/', views.bodyscan, name='bodyscan'),





    path('categories/social-coping/online-community/', views.onlinecom, name='subcategory_online-community'),
    path('categories/social-coping/online-community/delete_post/<int:post_id>/', delete_post, name='delete_post'),
    path('categories/social-coping/online-community/delete_comment/<int:comment_id>/', delete_comment, name='delete_comment'),

    path('chat/<int:psychologist_id>/', views.chat_view, name='chat'),
    path('psychprofile/<int:psychologist_id>/<int:user_id>/', views.psychprofile, name='psychprofile'),
    path('adminmessage/<int:user_id>/', views.admin_message_user, name='admin_message_user'),

    path('psychview/<int:psychologist_id>/', psychview, name='psychview'),
    path('psychview/<int:psychologist_id>/edit/', views.edit_psychview, name='edit_psychview'),
    
    path('accept-message/<int:message_id>/', accept_message, name='accept_message'),
    path('reject-message/<int:message_id>/', reject_message, name='reject_message'),
    path('pending-message/<int:message_id>/', pending_message, name='pending_message'),
    
    path('hotline/', views.hotline, name='hotline'),
    path('hotline/add/', views.add_hotline, name='add_hotline'),
    path('hotline/edit/<int:hotline_id>/', views.edit_hotline, name='edit_hotline'),
    path('hotline/delete/<int:hotline_id>/', views.delete_hotline, name='delete_hotline'),
    
    path ('videocall/', views.videocall, name="videocall"),
    path('validation/', validation, name='validation'),
    path('post/upvote/<int:post_id>/', views.upvote_post, name='upvote_post'),
    path('post/downvote/<int:post_id>/', views.downvote_post, name='downvote_post'),
    path('comment/upvote/<int:comment_id>/', views.upvote_comment, name='upvote_comment'),
    path('comment/downvote/<int:comment_id>/', views.downvote_comment, name='downvote_comment'),
    path('addcategory/', add_category, name='add_category'),
    path('addsubcategory/', add_subcategory, name='add_subcategory'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/<slug:slug>/', views.category_detail, name='category_detail'),
    path('categories/<slug:category_slug>/<slug:subcategory_slug>/', views.subcategory_detail, name='subcategory_detail'),
    path('gad7/', views.gad7, name='gad7'),
    path("categories/meaning-focused/mind-management/save-score/", save_score, name="save_score"),
] 
if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)