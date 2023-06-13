from django.urls import path

from rest_framework.routers import SimpleRouter

import api.views as views

router = SimpleRouter()
router.register('flashcards', views.FlashcardViewSet, basename='flashcard')
router.register('sets', views.FlashcardSetViewSet, basename='flashcardset')
router.register('ratings', views.RatingList, basename='rating')
router.register('quiz/generate', views.GenerateQuiz, basename='generate-quiz')
router.register('category', views.CategoryList, basename='category')

urlpatterns = [
    path('quiz/check/', views.CheckQuizView.as_view(), name='check-quiz')
]

urlpatterns += router.urls
