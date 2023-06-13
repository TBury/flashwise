import json
import random

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.admin import User


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Tag(models.Model):
    name = models.CharField(max_length=16)

    def __str__(self):
        return self.name


class Category(models.Model):
    CATEGORY_LEVELS = [
        ("easy", "Początkujący"),
        ("medi", "Średniozaawansowany"),
        ("hard", "Zaawansowany"),
    ]
    name = models.CharField(max_length=32)
    level = models.CharField(max_length=4, choices=CATEGORY_LEVELS)
    slug = models.SlugField(max_length=32, unique=True, default="")

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class FlashcardsSet(models.Model):
    SET_STATUSES = [
        ("public", "Publiczny"),
        ("private", "Prywatny")
    ]

    name = models.CharField(max_length=96, null=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=7, choices=SET_STATUSES, default="public")
    is_premium = models.BooleanField(default=False)
    tag = models.ForeignKey(Tag, null=True, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    @property
    def flashcard_count(self):
        return Flashcard.objects.filter(flashcard_set=self).count()

    def __str__(self):
        return self.name


class Flashcard(models.Model):
    front = models.TextField(blank=False, null=False)
    back = models.TextField(blank=False, null=False)
    last_modified = models.DateTimeField(auto_now_add=True)
    flashcard_set = models.ForeignKey(FlashcardsSet, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)


class Rating(models.Model):
    set = models.ForeignKey(FlashcardsSet, models.CASCADE)
    user = models.ForeignKey(User, models.CASCADE)
    rate = models.PositiveSmallIntegerField()


class Log(models.Model):
    ACTIONS = [
        ("A1", "Użytkownik zalogował się do systemu."),
        ("A2", "Użytkownik wylogował się z systemu."),
        ("B1", "Utworzono fiszkę."),
        ("B2", "Utworzono zestaw."),
    ]
    user = models.ForeignKey(User, models.CASCADE)
    timestamp = models.DateTimeField(auto_created=True, auto_now=True)
    action = models.CharField(max_length=2, choices=ACTIONS)

    def __str__(self):
        return self.timestamp


class Quiz(models.Model):
    flashcards_set = models.ForeignKey(FlashcardsSet, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    questions = models.ManyToManyField("QuizQuestion", related_name="quiz_questions")
    timestamp = models.DateTimeField(auto_created=True, auto_now=True)
    is_finished = models.BooleanField(default=False)
    score = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return str(self.id)

    def generate_quiz(self):
        if self.flashcards_set.flashcard_count >= 4:
            shuffled_set = self.flashcards_set.flashcard_set.order_by('?')
            for flashcard in shuffled_set:
                shuffled_temp = list(filter(lambda x: x != flashcard, shuffled_set))
                question = QuizQuestion.objects.create(text=flashcard.front, quiz=self)
                answers = ["A", "B", "C", "D"]
                random_correct_answer = answers.pop(random.randint(0, len(answers) - 1))
                question.correct_answer = random_correct_answer
                correct = QuizAnswer.objects.create(question=question, text=flashcard.back, letter=random_correct_answer)
                question.answers.add(correct)
                for answer in answers:
                    random_answer = random.choice(shuffled_temp)
                    a = QuizAnswer.objects.create(question=question, text=random_answer.back,
                                                  letter=answer)
                    shuffled_temp.remove(random_answer)
                    question.answers.add(a)
                question.save()
                self.questions.add(question)

            self.serialize_quiz()
        else:
            return {"message": "Not enough flashcards in set."}

    def serialize_quiz(self):
        questions = [{"quiz_id": self.id}]
        for question in self.questions.all():
            answers = []
            for answer in question.answers.all().order_by("letter"):
                answers.append({"letter": answer.letter, "text": answer.text})
            questions.append({"id": question.id, "text": question.text, "answers": answers})
        return questions

    def check_quiz(self, answers):
        if self.score != 0:
            self.score = 0
        raport = {}
        answers_dict = json.loads(answers.get("answers"))
        for question in self.questions.all():
            if len(answers_dict.keys()) == len(self.questions.all()):
                if question.is_correct(answers_dict.get(str(question.id))):
                    raport[question.id] = "Correct"
                    self.score += 1
                else:
                    raport[question.id] = "Incorrect"
            else:
                return {"error": "Nie wszystkie odpowiedzi zaznaczone."}
        raport["final_score"] = self.score
        self.is_finished = True
        self.save()
        return raport


@receiver(post_save, sender=Quiz)
def generate_quiz(sender, instance=None, created=False, **kwargs):
    if created:
        instance.generate_quiz()


class QuizAnswer(models.Model):
    question = models.ForeignKey("QuizQuestion", on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    letter = models.CharField(max_length=1)

    def __str__(self):
        return self.text


class QuizQuestion(models.Model):
    text = models.CharField(max_length=255)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    answers = models.ManyToManyField(QuizAnswer)
    correct_answer = models.CharField(max_length=1)

    def __str__(self):
        return self.text

    def is_correct(self, answer):
        return self.correct_answer == answer
