from django import forms
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template.context import RequestContext

from models import DAY_CHOICES
from models import WorkshopGame, Semigroup, Schedule
from wouso.core.user.models import Player

class AGForm(forms.ModelForm):
    class Meta:
        model = Semigroup
        fields = ('name', 'day', 'hour')

@login_required
def workshop_home(request, **kwargs):
    return render_to_response('workshop/cpanel/index.html',
                        {'module': 'workshop',
                         'days': DAY_CHOICES,
                         'hours': range(8, 22, 2),
                         'info': WorkshopGame},
                        context_instance=RequestContext(request)
    )

@login_required
def add_group(request):
    if request.method == 'POST':
        form = AGForm(request.POST)
        if form.is_valid():
            sg = form.save()
            sg.owner = WorkshopGame.get_instance()
            sg.save()
            return redirect('ws_edit_spot', day=sg.day, hour=sg.hour)
    else:
        form = AGForm()

    return render_to_response('workshop/cpanel/addgroup.html',
                        {'module': 'workshop',
                         'form': form,
                         },
                        context_instance=RequestContext(request)
    )

@login_required
def edit_group(request, semigroup):
    semigroup = get_object_or_404(Semigroup, pk=semigroup)

    if request.method == 'POST':
        form = AGForm(request.POST, instance=semigroup)
        if form.is_valid():
            sg = form.save()
            sg.owner = WorkshopGame.get_instance()
            sg.save()
            return redirect('ws_edit_spot', day=sg.day, hour=sg.hour)
    else:
        form = AGForm(instance=semigroup)

    return render_to_response('workshop/cpanel/editgroup.html',
            {'module': 'workshop',
             'form': form,
             'instance': semigroup,
             },
        context_instance=RequestContext(request)
    )


@login_required
def edit_spot(request, day, hour):
    sg = Semigroup.get_by_day_and_hour(day, hour)

    if not sg:
        return redirect('ws_add_group')

    if request.method == 'POST':
        try:
            player = Player.objects.get(pk=int(request.POST.get('player')))
        except ValueError, Player.DoesNotExist:
            pass
        else:
            sg.add_player(player)

    return render_to_response('workshop/cpanel/editspot.html',
                        {'module': 'workshop',
                         'semigroup': sg,
                         },
                        context_instance=RequestContext(request)
    )

@login_required
def kick_off(request, player):
    player = get_object_or_404(Player, pk=player)

    sgs = player.playergroup_set.filter(owner=WorkshopGame.get_instance())
    for s in sgs:
        s.players.remove(player)

    return redirect('workshop_home')

@login_required
def schedule(request):
    schedules = Schedule.objects.all().order_by('start_date')

    return render_to_response('workshop/cpanel/schedule.html',
                        {'module': 'workshop',
                         'schedules': schedules},
                        context_instance=RequestContext(request)
    )

@login_required
def schedule_change(request, schedule=None):
    class SCForm(forms.ModelForm):
        class Meta:
            model = Schedule
            fields = ('name', 'start_date', 'end_date')

    if schedule:
        schedule = get_object_or_404(Schedule, pk=schedule)

    if request.method == 'POST':
        form = SCForm(request.POST, instance=schedule)
        if form.is_valid():
            sc = form.save()
            sc.category = WorkshopGame.get_question_category()
            sc.save()
            return redirect('ws_schedule')
    else:
        form = SCForm(instance=schedule)

    return render_to_response('workshop/cpanel/schedule_change.html',
                        {'module': 'workshop',
                         'form': form,
                         'instance': schedule},
                        context_instance=RequestContext(request)
    )