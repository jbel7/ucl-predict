from django import forms
from .models import FavoriteTeam, Team


class PredictorForm(forms.Form):
    """Simplified form for match predictions - ML handles the prediction"""
    
    team_a = forms.ModelChoiceField(
        queryset=Team.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Home Team'
    )
    
    team_b = forms.ModelChoiceField(
        queryset=Team.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Away Team'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        team_a = cleaned_data.get('team_a')
        team_b = cleaned_data.get('team_b')
        
        # Ensure teams are different
        if team_a and team_b and team_a == team_b:
            raise forms.ValidationError("Teams must be different!")
        
        return cleaned_data


class FavoriteTeamForm(forms.ModelForm):
    """Form for adding favorite teams"""
    
    class Meta:
        model = FavoriteTeam
        fields = ['team']
        widgets = {
            'team': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'team': 'Select Team',
        }

