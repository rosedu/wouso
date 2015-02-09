from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from wouso.core.ui import register_footer_link
from wouso.interface.apps.qproposal.forms import QuestionForm
from django.shortcuts import render_to_response
from django.template import RequestContext
from wouso.core.qpool.models import Question, Tag, Answer, Category
from models import Qproposal


def propose(request):

    MAX_ANSWERS = 6

    if request.method == 'POST':
        form = QuestionForm(nr_ans=MAX_ANSWERS, data=request.POST)
        if form.is_valid():
            # create and save the question
            qdict = {}
            qdict['text'] = form.cleaned_data['text']
            qdict['answer_type'] = form.cleaned_data['answer_type']
            qdict['proposed_by'] = request.user
            qdict['category'] = Category.objects.filter(name='proposed')[0]
            q = Question(**qdict)
            q.save()

            tag = Tag.objects.filter(name=form.cleaned_data['category'])[0]
            q.tags.add(tag)

            # add the tags
            for tag_name in form.cleaned_data['tags']:
                tag = Tag.objects.filter(name=tag_name)[0]
                q.tags.add(tag)
            q.save()

            # add the answers
            for i in range(form.nr_ans):
                ansdict = {}
                if not form.cleaned_data['answer_%d' % i]:
                    continue
                ansdict['text'] = form.cleaned_data['answer_%d' % i]
                ansdict['correct'] = form.cleaned_data['correct_%d' % i]
                ans = Answer(question=q, **ansdict)
                ans.save()

            return render_to_response('qproposal/thanks.html',
                                      context_instance=RequestContext(request))
    else:
        form = QuestionForm(MAX_ANSWERS)
    return render_to_response('qproposal/propose.html',
                              {'form': form},
                              context_instance=RequestContext(request))


def footer_link(context):
    if Qproposal.disabled():
        return ''
    url = reverse('propose')
    return '<a href="%s">' % url + _('Propose question') + '</a>'


register_footer_link('qproposal', footer_link)
