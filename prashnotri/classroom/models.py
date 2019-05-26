from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.html import escape, mark_safe


class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)


class Subject(models.Model):
    name = models.CharField(max_length=30)
    color = models.CharField(max_length=7, default='#007bff')

    def __str__(self):
        return self.name

    def get_html_badge(self):
        name = escape(self.name)
        color = escape(self.color)
        html = '<span class="badge badge-primary" style="background-color: %s">%s</span>' % (color, name)
        return mark_safe(html)


class Quiz(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quizzes')
    name = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='quizzes')
    averageScore = models.FloatField(default=0)
    def __str__(self):
        return self.name


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField('Question', max_length=2550)

    def __str__(self):
        return self.text


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField('Answer', max_length=255)
    is_correct = models.BooleanField('Correct answer', default=False)

    def __str__(self):
        return self.text


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    quizzes = models.ManyToManyField(Quiz, through='TakenQuiz')
    interests = models.ManyToManyField(Subject, related_name='interested_students')

    def get_unanswered_questions(self, quiz):
        answered_questions = self.quiz_answers \
            .filter(answer__question__quiz=quiz) \
            .values_list('answer__question__pk', flat=True)
        questions = quiz.questions.exclude(pk__in=answered_questions).order_by('?')
        return questions
    
    def get_attempt_unanswered_questions(self,attempt):
        answered_questions = self.attempt_answer \
            .filter(attempt=attempt) \
            .values_list('answer__question__pk',flat=True)
        qid = attemptQuestion.objects \
            .filter(attempt__pk=attempt.pk) \
            .exclude(question__pk__in=answered_questions) \
            .values_list('question',flat=True) \
            .order_by('order')
        return qid

    def get_question(self,attempt,order):
        qid = attemptQuestion.objects \
            .filter(attempt__pk=attempt.pk) \
            .filter(order=order) \
            .values_list('question',flat=True)
        return qid

    def __str__(self):
        return self.user.username


class TakenQuiz(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='taken_quizzes')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='taken_quizzes')
    score = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)


class StudentAnswer(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='quiz_answers')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='+')

class Attempt(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz,on_delete=models.CASCADE,related_name='quiz_attempts')
    score = models.FloatField()
    over = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    currquestion = models.ForeignKey(Question,null=True,default=None,on_delete=models.SET_NULL)
    
    class Meta:
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['quiz']),
        ]

class attemptAnswer(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE,related_name='attempt_answer')
    answer = models.ForeignKey(Answer,on_delete=models.CASCADE,related_name='a+')
    attempt = models.ForeignKey(Attempt,on_delete=models.CASCADE)
    question = models.ForeignKey(Question,on_delete = models.CASCADE)
    submitted = models.BooleanField(default=False)
    class Meta:
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['answer']),
            models.Index(fields=['attempt','question'])
        ]

class attemptQuestion(models.Model):
    question = models.ForeignKey(Question,on_delete=models.CASCADE)
    attempt = models.ForeignKey(Attempt,on_delete=models.CASCADE,related_name="attempt_q")
    order = models.IntegerField()

    class Meta:
        unique_together = ("order","attempt")
        indexes = [
            models.Index(fields=['attempt','question'])
        ]