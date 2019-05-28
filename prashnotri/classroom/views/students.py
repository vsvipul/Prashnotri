from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView

from ..decorators import student_required
from ..forms import StudentInterestsForm, StudentSignUpForm, TakeReQuizForm,SubmitAttemptForm
from ..models import Quiz, Student, TakenQuiz, User, Attempt, attemptQuestion, Question
import random

class StudentSignUpView(CreateView):
    model = User
    form_class = StudentSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'student'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('students:quiz_list')


@method_decorator([login_required, student_required], name='dispatch')
class StudentInterestsView(UpdateView):
    model = Student
    form_class = StudentInterestsForm
    template_name = 'classroom/students/interests_form.html'
    success_url = reverse_lazy('students:quiz_list')

    def get_object(self):
        return self.request.user.student

    def form_valid(self, form):
        messages.success(self.request, 'Interests updated with success!')
        return super().form_valid(form)


@method_decorator([login_required, student_required], name='dispatch')
class QuizListView(ListView):
    model = Quiz
    ordering = ('name', )
    context_object_name = 'quizzes'
    template_name = 'classroom/students/quiz_list.html'

    def get_queryset(self):
        student = self.request.user.student
        student_interests = student.interests.values_list('pk', flat=True)
        taken_quizzes = student.quizzes.values_list('pk', flat=True)
        queryset = Quiz.objects.filter(subject__in=student_interests) \
            .exclude(pk__in=taken_quizzes) \
            .annotate(questions_count=Count('questions')) \
            .filter(questions_count__gt=0)
        return queryset


@method_decorator([login_required, student_required], name='dispatch')
class TakenQuizListView(ListView):
    model = TakenQuiz
    context_object_name = 'taken_quizzes'
    template_name = 'classroom/students/taken_quiz_list.html'

    def get_queryset(self):
        queryset = self.request.user.student.taken_quizzes \
            .select_related('quiz', 'quiz__subject') \
            .order_by('quiz__name')
        return queryset


# @login_required
# @student_required
# def take_quiz(request, pk):
#     quiz = get_object_or_404(Quiz, pk=pk)
#     student = request.user.student

#     if student.quizzes.filter(pk=pk).exists():
#         return render(request, 'students/taken_quiz.html')

#     total_questions = quiz.questions.count()
#     unanswered_questions = student.get_unanswered_questions(quiz)
#     total_unanswered_questions = unanswered_questions.count()
#     progress = 100 - round(((total_unanswered_questions - 1) / total_questions) * 100)
#     # unanswered_questions = list(unanswered_questions)
#     # random.shuffle(unanswered_questions)
#     question = unanswered_questions.first()

#     if request.method == 'POST':
#         form = TakeQuizForm(question=question, data=request.POST)
#         if form.is_valid():
#             with transaction.atomic():
#                 student_answer = form.save(commit=False)
#                 student_answer.student = student
#                 student_answer.save()
#                 if student.get_unanswered_questions(quiz).exists():
#                     return redirect('students:take_quiz', pk)
#                 else:
#                     correct_answers = student.quiz_answers.filter(answer__question__quiz=quiz, answer__is_correct=True).count()
#                     score = round((correct_answers / total_questions) * 100.0, 2)
#                     TakenQuiz.objects.create(student=student, quiz=quiz, score=score)
#                     if score < 50.0:
#                         messages.warning(request, 'Better luck next time! Your score for the quiz %s was %s.' % (quiz.name, score))
#                     else:
#                         messages.success(request, 'Congratulations! You completed the quiz %s with success! You scored %s points.' % (quiz.name, score))
#                     return redirect('students:quiz_list')
#     else:
#         form = TakeQuizForm(question=question)

#     return render(request, 'classroom/students/take_quiz_form.html', {
#         'quiz': quiz,
#         'question': question,
#         'form': form,
#         'progress': progress
#     })

@login_required
@student_required
def newretake_quiz(request,pk):
    student = request.user.student
    quiz = get_object_or_404(Quiz,pk=pk)
    questions = list(quiz.questions.all())
    random.shuffle(questions)
    attempt= Attempt(student=student,quiz=quiz,score=0)
    with transaction.atomic():
        attempt.save()
        for i in range(len(questions)):
            aq = attemptQuestion(attempt=attempt,question=questions[i],order=i+1)
            aq.save()
    return redirect('students:retake_quiz', attempt.pk)

@login_required
@student_required
def retake_quiz(request, pk):
    attempt = get_object_or_404(Attempt,pk=pk)
    quiz = attempt.quiz
    student = request.user.student
    if(student!=attempt.student or attempt.over):
        print("Attempt_OVER!")
        return redirect('students:taken_quiz_list')
    # if student.quizzes.filter(pk=pk).exists():
    #     return render(request, 'students/taken_quiz.html')

    total_questions = quiz.questions.count()
    unanswered_questions = student.get_attempt_unanswered_questions(attempt)
    total_unanswered_questions = unanswered_questions.count()
    if(total_unanswered_questions==0):
        return redirect('students:taken_quiz_list')
    progress = 100 - round(((total_unanswered_questions - 1) / total_questions) * 100)
    if(attempt.currquestion==None):
        question = unanswered_questions.first()
        question = Question.objects.get(pk=question)
        with transaction.atomic():
            attempt.currquestion = question 
            attempt.save()
    else:
        question = attempt.currquestion
    is_answered = student.attempt_answer.filter(attempt=attempt,question=question)
    temp_a = is_answered.values_list('answer',flat=True)
    is_a = len(list(temp_a))
    question_number = attemptQuestion.objects.filter(attempt=attempt,question=question) \
        .values_list('order',flat=True).first()
    print(question_number)
    if request.method == 'POST':
        form = TakeReQuizForm(question=question, data=request.POST, attempt=attempt)
        if form.is_valid():
            with transaction.atomic():
                if(is_a):
                    ans = is_answered.get()
                    ans.answer = form.cleaned_data['answer']
                    ans.save()
                else:
                    student_answer = form.save(commit=False)
                    student_answer.student = student
                    student_answer.attempt = attempt
                    student_answer.question = question
                    student_answer.save()
                attempt.currquestion = None
                attempt.save()
                if student.get_attempt_unanswered_questions(attempt).exists():
                    return redirect('students:retake_quiz', pk)
                else:
                    return redirect('students:show_submit', pk)
    else:
        if(is_a):
            ans = is_answered.values_list('answer',flat=True).first()
            form = TakeReQuizForm(question=question, attempt=attempt,initial={'answer':ans})
        else:
            form = TakeReQuizForm(question=question,attempt=attempt)

    return render(request, 'classroom/students/take_quiz_form.html', {
        'quiz': quiz,
        'question': question,
        'form': form,
        'progress': progress,
        'question_num': question_number
    })

@login_required
@student_required
def goto_quiz(request,pk,q_pk):
    attempt = get_object_or_404(Attempt,pk=pk)
    quiz = attempt.quiz
    student = request.user.student
    if(student!=attempt.student or attempt.over):
        print("Attempt_OVER!")
        return redirect('students:taken_quiz_list')
    question = list(student.get_question(attempt,q_pk))
    if(len(question)==0):
        print("BLANK")
        return redirect('students:retake_quiz',pk)
    with transaction.atomic():
        question = get_object_or_404(Question,pk=question[0])
        print(question)
        attempt.currquestion = question
        attempt.save()
        return redirect('students:retake_quiz',pk)

@login_required
@student_required
def show_submit(request,pk):
    attempt = get_object_or_404(Attempt,pk=pk)
    student = request.user.student
    if attempt.over or student != attempt.student:
        return redirect('students:taken_quiz_list')
    if request.method=='POST':
        form = SubmitAttemptForm(data = request.POST)
        print(form.is_valid())
        if form.is_valid():
            return redirect('students:submit_attempt',pk)
    else:
        form = SubmitAttemptForm()
    
    return render(request, 'classroom/students/submit.html',{
        'quiz': get_object_or_404(Quiz,pk=attempt.quiz.pk)
    })
    
@login_required
@student_required
def submit_attempt(request,pk):
    attempt = get_object_or_404(Attempt,pk=pk)
    quiz = attempt.quiz
    student = request.user.student
    total_questions = quiz.questions.count()

    if(student!=attempt.student or attempt.over):
        print("Attempt_OVER!")
        return redirect('students:taken_quiz_list')
    with transaction.atomic():
        correct_answers = student.attempt_answer.filter(attempt=attempt, answer__is_correct=True).count()
        score = round((correct_answers / total_questions) * 100.0, 2)
        # TakenQuiz.objects.create(student=student, quiz=quiz, score=score)
        attempt.score = score
        attempt.over = True
        attempt.save()
        if score < 50.0:
            messages.warning(request, 'Better luck next time! Your score for the quiz %s was %s.' % (quiz.name, score))
        else:
            messages.success(request, 'Congratulations! You completed the quiz %s with success! You scored %s points.' % (quiz.name, score))
        if student.quizzes.filter(pk=quiz.pk).exists():
            pass
        else:
            TakenQuiz.objects.create(student=student, quiz=quiz, score=score)
        return render(request,'classroom/students/result.html',{
            'score':score,
            'quiz':quiz
        })

#@login_required
def get_ranklist(request,pk):
    quiz = get_object_or_404(Quiz,pk=pk)
    ranklist = TakenQuiz.objects.filter(quiz=quiz).order_by('-score')
    return render(request, 'classroom/ranklist.html',{
        'ranklist':ranklist,
        'quiz': quiz
    })

@login_required
@student_required
def attempts(request,pk=-1):
    student = request.user.student
    attemptlist = Attempt.objects.filter(student=student).filter(over=True)
    print(pk)
    if(pk>=0):
        attemptlist = attemptlist.filter(quiz__pk=pk)
    attemptlist.order_by('date')
    return render(request,'classroom/students/attempts.html',{
        'attemptlist':attemptlist,
        'student':student
    })