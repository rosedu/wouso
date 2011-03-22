from django.db import models
from wouso.core.app import App
from wouso.core.user.models import UserProfile
from wouso.interface import render_string

class Top(App):
    
    @classmethod
    def get_sidebar_widget(kls, request):
        top5 = UserProfile.objects.all().order_by('-points')[:5]
        
        return render_string('top/sidebar.html', 
            {'topusers': top5}
        )

