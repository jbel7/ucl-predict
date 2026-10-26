from django.urls import path
from . import views

app_name = 'project'

urlpatterns = [
    # Homepage
    path('', views.home, name='home'),
    
    # Teams
    path('teams/', views.TeamListView.as_view(), name='team_list'),
    path('teams/<int:pk>/', views.TeamDetailView.as_view(), name='team_detail'),
    
    # Players
    path('players/', views.PlayerRankingListView.as_view(), name='player_list'),
    
    # Matches
    path('matches/', views.MatchListView.as_view(), name='match_list'),
    path('matches/<int:pk>/', views.MatchDetailView.as_view(), name='match_detail'),
    
    # Predictor
    path('predictor/', views.predictor, name='predictor'),
    path('predictor/success/', views.prediction_success, name='prediction_success'),
    
    # Authentication
    path('signup/', views.signup, name='signup'),
    
    # User Features (Login Required)
    path('my-predictions/', views.SavedPredictionListView.as_view(), name='saved_predictions'),
    path('my-predictions/<int:pk>/delete/', views.delete_prediction, name='delete_prediction'),
]