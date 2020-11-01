# from django.template import loader
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Choice, Question, Vote

import logging

log = logging.getLogger("polls")
logging.basicConfig(level=logging.INFO)

class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the all published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:1000]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:1000]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'polls/index.html', context)

def detail(request, question_id):
    if not request.user.is_authenticated:
        messages.error(request, "You must login before you can vote")
        return redirect('polls:index')

    try:
        question = Question.objects.get(pk=question_id)
        if (not question.can_vote()):
            messages.error(request, "Can not vote current question")
    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    return render(request, 'polls/detail.html', {'question': question})

def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})

@login_required()
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    user = request.user
    try:
        choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        messages.error(request, "You didn't make a choice")
        return render(request, 'polls/detail.html', {
            'question': question,
        })
    else:
        Vote.objects.update_or_create(defaults={'choice': choice}, question=question, user=user)
        for choice in question.choice_set.all():
            choice.votes = Vote.objects.filter(question=question).filter(choice=choice).count()
            choice.save()
        
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        messages.success(request, "Your choice successfully recorded. Thank you.")
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
