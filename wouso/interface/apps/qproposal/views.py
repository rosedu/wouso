from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from wouso.core.ui import register_footer_link
from wouso.interface.apps.qproposal.forms import ProposedQuestionForm
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.views.generic import ListView
from django.http import HttpResponse, Http404, HttpResponseForbidden
from wouso.core.qpool.models import Question, Tag, Answer, Category, ProposedQuestion
from models import Qproposal
import json


def propose(request):
    MAX_ANSWERS = 6

    if request.method == 'POST':
        form = ProposedQuestionForm(nr_ans=MAX_ANSWERS, data=request.POST)
        if form.is_valid():
            # create and save the question
            qdict = {}
            qdict['text'] = form.cleaned_data['text']
            qdict['proposed_by'] = request.user
            qdict['category'] = Category.objects.filter(name=form.cleaned_data['category'])[0]
            
            q = ProposedQuestion(**qdict)
            q.save()

            #tag = Tag.objects.filter(name=form.cleaned_data['category'])[0]
            tag, created = Tag.objects.get_or_create(name=q.category)
            tag_prefix = q.category
            q.tags.add(tag)

            # add the tags
            for tag_name in form.cleaned_data['tags']:
                #tag = Tag.objects.filter(name=tag_name)[0]
                tag, created = Tag.objects.get_or_create(name=tag_prefix+tag_name)
                q.tags.add(tag)
            q.save()

            # add the answers
            answers_data = []
            for i in range (form.nr_ans):
                ansdict = {}
                if not form.cleaned_data['answer_%d' % i]:
                    continue
                ansdict['text'] = form.cleaned_data['answer_%d' % i]
                ansdict['correct'] = form.cleaned_data['correct_%d' % i]
                answers_data.append(ansdict)


            q.answers_json = json.dumps(answers_data)
            q.save()

            return render_to_response('qproposal/thanks.html',
                                      context_instance=RequestContext(request))
    else:
        form = ProposedQuestionForm(MAX_ANSWERS)

    player = request.user.get_profile() if request.user.is_authenticated() else None
    prop_questions = ProposedQuestion.objects.all().filter(proposed_by=player).order_by('-date_proposed')
    if request.is_ajax():
        return render_to_response('qproposal/propose_content.html',
                              {'form': form, 'prop_questions' : prop_questions, 'max_answers' : MAX_ANSWERS},
                              context_instance=RequestContext(request))
    else:
        return render(request,'qproposal/403_error.html',status=403)

