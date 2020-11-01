import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


# Create your models here.
class Question(models.Model):
    """
    A class to represent the Question

    Attributes
    ----------
    question_text : str
        text which describes what the question is about
    pub_date : datetime
        time represent published date
    end_date : datetime
        time represent expired date

    Methods
    -------
    was_published_recently(self)
        Return true if the question is published date is longer than a day
    
    is_published(self)
        Returns true if the question is published date is longer than a day

    can_vote(self)
        Return true if voting is currently allowed for this question
    
    """
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    end_date = models.DateTimeField('date expired')

    def was_published_recently(self):
        """
        Returns true if the question is published date is longer than a day
        """
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def is_published(self):
        """
        Returns true if current date is on or after question’s publication date
        """
        now = timezone.now()
        return self.pub_date <= now

    def can_vote(self):
        """
        Return true if voting is currently allowed for this question
        """
        now = timezone.now()
        return self.pub_date <= now < self.end_date

    def __str__(self):
        return self.question_text

    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'


class Choice(models.Model):
    """
    A class to represent the question's choice

    Attributes
    ----------
    question : Question
        Question class which choice is associate with
    choice_text : str
        text which describes the choice for question
    votes : int
        an integer which keeps the number of votes cast by people

    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text

class Vote(models.Model):
    """
    A class to represent each vote for choice.

    Attributes
    ----------
    
    """
    choice = models.ForeignKey(Choice, null=True, on_delete=models.SET_NULL)
    question = models.ForeignKey(Question, null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
