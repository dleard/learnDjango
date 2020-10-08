import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question

def create_question(question_text, days):
  time = timezone.now() + datetime.timedelta(days=days)
  return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionModelTests(TestCase):

  # was_published_recently() returns false for questions whose date is in the future
  def test_was_published_recently_with_future_question(self):
    time = timezone.now() + datetime.timedelta(days=30)
    future_question = Question(pub_date=time)
    self.assertIs(future_question.was_published_recently(), False)

  def test_was_published_recently_with_old_question(self):
    time = timezone.now() - datetime.timedelta(days=1, seconds=1)
    old_question = Question(pub_date=time)
    self.assertIs(old_question.was_published_recently(), False)

  def test_was_published_recently_with_recent_question(self):
    time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
    recent_question = Question(pub_date=time)
    self.assertIs(recent_question.was_published_recently(), True)

class QuestionIndexViewTests(TestCase):

  # displays proper text when there are no questions to show
  def test_no_questions(self):
    response = self.client.get(reverse('polls:index'))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, "No polls are available.")
    self.assertQuerysetEqual(response.context['latest_question_list'], [])

  # displays past questions
  def test_past_question(self):
    create_question(question_text="Past question.", days=-30)
    response = self.client.get(reverse('polls:index'))
    self.assertQuerysetEqual(
        response.context['latest_question_list'],
        ['<Question: Past question.>']
    )
  # only displays past question when both future & past exist
  def test_future_question_and_past_question(self):
    create_question(question_text='Past question.', days=-30)
    create_question(question_text='Future question.', days=30)
    response = self.client.get(reverse('polls:index'))
    self.assertQuerysetEqual(
      response.context['latest_question_list'],
      ['<Question: Past question.>']
    )

  # displays multiple past questions
  def test_two_past_questions(self):
    create_question(question_text="Past question 1.", days=-30)
    create_question(question_text="Past question 2.", days=-5)
    response = self.client.get(reverse('polls:index'))
    self.assertQuerysetEqual(
        response.context['latest_question_list'],
        ['<Question: Past question 2.>', '<Question: Past question 1.>']
    )

class QuestonDetailViewTests(TestCase):
  """Detail view returns 404 for a question with a pub_date in the future"""
  def test_future_questions(self):
    future_question = create_question(question_text='Future question.', days=30)
    url = reverse('polls:detail', args=(future_question.id,))
    response = self.client.get(url)
    self.assertEqual(response.status_code, 404)

  """Detail view displays question_text for a published question"""
  def test_future_questions(self):
    past_question = create_question(question_text='Past question.', days=-30)
    url = reverse('polls:detail', args=(past_question.id,))
    response = self.client.get(url)
    self.assertContains(response, past_question.question_text)
