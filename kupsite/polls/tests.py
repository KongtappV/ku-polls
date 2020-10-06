import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question

def create_question(question_text, days, ends_days=30):
    """
    Create a question with the given `question_text` and published the
    given number of `days` and `ends_days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    ends = timezone.now() + datetime.timedelta(days=ends_days)
    return Question.objects.create(question_text=question_text, pub_date=time, end_date=ends)


class QuestionIndexViewTests(TestCase):

    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        create_question(question_text="Past question.", days=-30, ends_days=-15)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30, ends_days=60)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        create_question(question_text="Past question.", days=-30, ends_days=60)
        create_question(question_text="Future question.", days=30, ends_days=60)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        create_question(question_text="Past question 1.", days=-30)
        create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )

class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        future_question = create_question(question_text='Future Question.', days=30, ends_days=60)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        end_time = timezone.now() + datetime.timedelta(days=30)
        old_question = Question(pub_date=time, end_date=end_time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        end_time = timezone.now() + datetime.timedelta(days=30)
        recent_question = Question(pub_date=time, end_date=end_time)
        self.assertIs(recent_question.was_published_recently(), True)

    def test_is_published_with_old_question(self):
        """
        is_published() returns True for questions whose pub_date is older than now
        """
        new_question = create_question(question_text='Future Question.', days=0, ends_days=30)
        old_question = create_question(question_text='Old Question.', days=-1, ends_days=30)
        self.assertIs(new_question.is_published(), True)
        self.assertIs(old_question.is_published(), True)

    def test_is_published_with_future_question(self):
        """
        is_published() returns False to questions which is not yet published
        """
        future_question = create_question(question_text='Future Question.', days=1, ends_days=30)
        self.assertIs(future_question.is_published(), False)

    def test_can_vote_not_published(self):
        """
        can_vote() returns False can not vote the question if the question
        is not yet published
        """
        future_question = create_question(question_text='Future Question.', days=1, ends_days=30)
        self.assertIs(future_question.can_vote(), False)

    def test_can_vote_expired_question(self):
        """
        can_vote() returns False if question is already expired
        """
        past_question = create_question(question_text='Past Question.', days=-8, ends_days=-1)
        self.assertIs(past_question.can_vote(), False)

    def test_can_vote_(self):
        """
        can_vote() returns True when the question is already published
        and not expired
        """
        recent_question = create_question(question_text='Recent Question.', days=-1, ends_days=30)
        self.assertIs(recent_question.can_vote(), True)


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text='Future question.', days=5, ends_days=30)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text='Past Question.', days=-5, ends_days=30)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
