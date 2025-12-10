from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Team, PlayerRanking, MatchPredictionTemplate, FavoriteTeam, SavedPrediction, TeamStatistic, ChampionsLeagueMatch, CLRecord
from .forms import PredictorForm, FavoriteTeamForm
from .api_service import get_team_matches_from_api, get_team_cl_record_from_api, get_all_recent_matches_from_api
from ml_predictor import get_predictor


# Homepage
def home(request):
    """Homepage showing overview of UCL data"""
    teams = Team.objects.all()[:5]
    top_players = PlayerRanking.objects.all()[:5]
    featured_matches = MatchPredictionTemplate.objects.all()[:3]
    
    context = {
        'teams': teams,
        'top_players': top_players,
        'featured_matches': featured_matches,
    }
    return render(request, 'project/home.html', context)


# Team Views
class TeamListView(ListView):
    """List all teams"""
    model = Team
    template_name = 'project/team_list.html'
    context_object_name = 'teams'
    
    def get_queryset(self):
        return Team.objects.all().order_by('name')


class TeamDetailView(DetailView):
    """Detail view for a single team"""
    model = Team
    template_name = 'project/team_detail.html'
    context_object_name = 'team'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get team statistics (handle gracefully if doesn't exist)
        try:
            context['statistics'] = self.object.statistics
        except (TeamStatistic.DoesNotExist, AttributeError):
            context['statistics'] = None
        
        # Get up to 15 players from this team
        context['players'] = PlayerRanking.objects.filter(team=self.object)[:15]
        
        # Get recent Champions League matches (this season) - try API first, fallback to DB
        from datetime import datetime
        current_year = datetime.now().year
        current_season = f"{current_year}-{current_year + 1}"
        
        # Try to get from API (will fallback to DB if API unavailable)
        api_matches = get_team_matches_from_api(self.object.name, current_season)
        
        if api_matches and len(api_matches) > 0:
            # API returned data - use it directly
            context['recent_matches'] = api_matches
            context['using_api'] = True
        else:
            # Fallback to database
            try:
                db_matches = ChampionsLeagueMatch.objects.filter(
                    Q(team_a=self.object) | Q(team_b=self.object),
                    season=current_season
                ).order_by('-match_date')[:10]
                context['recent_matches'] = db_matches
                context['using_api'] = False
            except Exception:
                context['recent_matches'] = []
                context['using_api'] = False
        
        # Get CL records for last 5 years - try API first, fallback to DB
        api_records = get_team_cl_record_from_api(self.object.name)
        
        if api_records:
            context['cl_records'] = api_records
        else:
            # Fallback to database
            try:
                seasons = [f"{current_year - i}-{current_year - i + 1}" for i in range(5)]
                context['cl_records'] = CLRecord.objects.filter(
                    team=self.object,
                    season__in=seasons
                ).order_by('-season')
            except Exception:
                context['cl_records'] = []
        
        return context


# Player Views
class PlayerRankingListView(ListView):
    """List all player rankings"""
    model = PlayerRanking
    template_name = 'project/player_list.html'
    context_object_name = 'players'
    
    def get_queryset(self):
        return PlayerRanking.objects.all().order_by('rank_int')


# Match Views
class MatchListView(ListView):
    """List all recent Champions League matches with outcomes"""
    template_name = 'project/match_list.html'
    context_object_name = 'matches'
    
    def get_queryset(self):
        """Get recent matches from API or database"""
        matches = get_all_recent_matches_from_api(limit=50)
        return matches
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['using_api'] = True  # Indicates we're using live data
        return context


class MatchDetailView(DetailView):
    """Detail view for a single match"""
    model = MatchPredictionTemplate
    template_name = 'project/match_detail.html'
    context_object_name = 'match'


# Predictor Page with ML Integration
def predictor(request):
    """Match prediction form page with ML predictions"""
    prediction_result = None
    
    if request.method == 'POST':
        form = PredictorForm(request.POST)
        if form.is_valid():
            team_a = form.cleaned_data['team_a']
            team_b = form.cleaned_data['team_b']
            
            # Get ML prediction
            predictor_model = get_predictor()
            ml_prediction = predictor_model.predict_match(team_a, team_b)
            
            prediction_result = {
                'team_a': team_a,
                'team_b': team_b,
                'predicted_result': ml_prediction['predicted_result'],
                'predicted_result_display': ml_prediction['outcome_label'],
                'confidence': ml_prediction['confidence'],
                'probabilities': ml_prediction['probabilities'],
                'team_a_strength': ml_prediction.get('team_a_strength', 0),
                'team_b_strength': ml_prediction.get('team_b_strength', 0),
                'note': ml_prediction.get('note', None)
            }
            
            # Save prediction ONLY if user is logged in
            if request.user.is_authenticated:
                SavedPrediction.objects.create(
                    user=request.user,
                    team_a=team_a,
                    team_b=team_b,
                    predicted_result=ml_prediction['predicted_result'],
                    model_confidence=ml_prediction['confidence']
                )
                # Mark that prediction was saved
                prediction_result['saved'] = True
            else:
                prediction_result['saved'] = False
            # Show prediction result on the same page (no redirect)
    else:
        form = PredictorForm()
    
    context = {
        'form': form,
        'prediction_result': prediction_result
    }
    return render(request, 'project/predictor.html', context)


def prediction_success(request):
    """Success page after saving prediction"""
    return render(request, 'project/prediction_success.html')


# User's Saved Predictions (Login Required)
class SavedPredictionListView(LoginRequiredMixin, ListView):
    """List user's saved predictions - LOGIN REQUIRED"""
    model = SavedPrediction
    template_name = 'project/saved_predictions.html'
    context_object_name = 'predictions'
    
    def get_login_url(self):
        """Redirect to login page"""
        from django.urls import reverse
        return reverse('login') + '?next=' + reverse('project:saved_predictions')
    
    def get_queryset(self):
        return SavedPrediction.objects.filter(user=self.request.user).order_by('-timestamp')


def delete_prediction(request, pk):
    """Delete a saved prediction - LOGIN REQUIRED"""
    if not request.user.is_authenticated:
        from django.contrib.auth.views import redirect_to_login
        from django.urls import reverse
        return redirect_to_login(reverse('project:delete_prediction', args=[pk]))
    
    if request.method != 'POST':
        return redirect('project:saved_predictions')
    
    try:
        prediction = SavedPrediction.objects.get(pk=pk, user=request.user)
        prediction.delete()
        from django.contrib import messages
        messages.success(request, 'Prediction deleted successfully.')
    except SavedPrediction.DoesNotExist:
        from django.contrib import messages
        messages.error(request, 'Prediction not found or you do not have permission to delete it.')
    
    return redirect('project:saved_predictions')


# Favorite Teams (Login Required)
class FavoriteTeamListView(LoginRequiredMixin, ListView):
    """List user's favorite teams"""
    model = FavoriteTeam
    template_name = 'project/favorite_teams.html'
    context_object_name = 'favorites'
    
    def get_queryset(self):
        return FavoriteTeam.objects.filter(user=self.request.user).order_by('-created_at')


class AddFavoriteTeamView(LoginRequiredMixin, CreateView):
    """Add a team to favorites"""
    model = FavoriteTeam
    form_class = FavoriteTeamForm
    template_name = 'project/add_favorite.html'
    success_url = reverse_lazy('project:favorite_teams')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


# Sign-up View
def signup(request):
    """User registration view - same approach as mini_insta"""
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        if user_form.is_valid():
            # Save the User
            user = user_form.save()
            # Automatically log in the user after signup
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            # Redirect to home page
            return redirect('project:home')
    else:
        user_form = UserCreationForm()
    
    # Add styling to form fields
    if user_form:
        user_form.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
        user_form.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create a password'
        })
        user_form.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
    
    return render(request, 'project/signup.html', {'user_form': user_form})