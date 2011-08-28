from forms import QuestionForm
from wouso.interface import render_response
from wouso.core.qpool.models import Question, Tag, Answer


def propose(request):

    if request.method == 'POST':
        form = QuestionForm(5, request.POST)
        if form.is_valid():
            # create and save the question
            qdict = {}
            qdict['text'] = form.cleaned_data['text']
            qdict['answer_type'] = form.cleaned_data['answer_type']
            qdict['proposed_by'] = request.user
            q = Question(**qdict)
            q.save()

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

            return render_response('qproposal/thanks.html', request, {})
    else:
        form = QuestionForm()
    return render_response('qproposal/propose.html', request,
                           {'form': form})