from datetime import datetime, timedelta
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.generic import View
from models import QotdUser, QotdGame
from forms import QotdForm
from wouso.core.ui import register_sidebar_block


class QotdView(View):

    def dispatch(self, request, *args, **kwargs):
        if QotdGame.disabled():
            return redirect('wouso.interface.views.homepage')

        profile = request.user.get_profile()
        self.qotd_user = profile.get_extension(QotdUser)

        if self.qotd_user.magic.has_modifier('qotd-blind'):
            messages.error(request, _("You have been blinded, you cannot "
                                      "answer to the Question of the Day"))
            return redirect('games.qotd.views.history')
        elif not self.qotd_user.has_question:
            self.qotd = QotdGame.get_for_today()
            self.qotd_user.set_question(self.qotd)
        else:
            self.qotd = self.qotd_user.my_question

        if self.qotd_user.has_answered:
            self.qotd_user.reset_question()
            return redirect('games.qotd.views.history')

        return super(QotdView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if self.qotd is None:
            form = None
        else:
            form = QotdForm(self.qotd)
        return render_to_response('qotd/index.html',
                                  {'question': self.qotd, 'form': form},
                                  context_instance=RequestContext(request))

    def post(self, request, *args, **kwargs):
        if self.qotd is None:
            form = None
        else:
            form = QotdForm(self.qotd, request.POST)
            if form.is_valid():
                choice = int(form.cleaned_data['answers'])
                QotdGame.answered(self.qotd_user, self.qotd, choice)
                return redirect('games.qotd.views.done')

        return render_to_response('qotd/index.html',
                                  {'question': self.qotd, 'form': form},
                                  context_instance=RequestContext(request))


index = login_required(QotdView.as_view())


@login_required
def done(request):
    if QotdGame.disabled():
        return redirect('wouso.interface.views.homepage')
    # Do not show results until done
    if not request.user.get_profile().get_extension(QotdUser).has_answered:
        return redirect('games.qotd.views.history')

    user = request.user.get_profile().get_extension(QotdUser)
    qotd = user.my_question

    if not qotd:
        return redirect("homepage")

    choice = user.last_answer
    ans = [a for a in qotd.answers if a.id == choice]
    if ans:
        ans = ans[0]
        valid = ans.correct
    else:
        ans = None
        valid = False

    return render_to_response('qotd/done.html',
                              {'question': qotd,
                               'choice': ans,
                               'valid': valid},
                              context_instance=RequestContext(request))


@login_required
def history(request):
    return render_to_response(
        'qotd/history.html',
        {'history': QotdGame.get_history()},
        context_instance=RequestContext(request))


def sidebar_widget(context):
    # TODO: nothing should happen in the sidebar_widget
    user = context.get('user', None)
    if not user or not user.is_authenticated():
        return ''

    if QotdGame.disabled():
        return ''
    qotd = QotdGame.get_for_today()
    qotd_user = user.get_profile().get_extension(QotdUser)

    if not qotd_user.has_question:
        qotd_user.set_question(qotd)
    else:
        qotd = qotd_user.my_question

    if qotd_user.has_answered:
        time_passed = datetime.now() - qotd_user.last_answered
        qotd_user.reset_question()
        if time_passed > timedelta(seconds=120):  # two minutes
            return ''
    return render_to_string('qotd/sidebar.html',
                            {'question': qotd,
                             'quser': qotd_user,
                             'qotd': QotdGame,
                             'id': 'qotd'})


register_sidebar_block('qotd', sidebar_widget)
