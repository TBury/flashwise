from django.db.models import Q
from rest_framework import viewsets, mixins, status, permissions
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response

from . import models
from . import serializers


class FlashcardViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.FlashcardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = models.Flashcard.objects.filter(author=self.request.user)
        flashcard_set = self.request.query_params.get('flashcard_set', None)
        if flashcard_set is not None:
            queryset = queryset.filter(flashcard_set__name=flashcard_set)
        return queryset


class FlashcardSetViewSet(viewsets.ModelViewSet):
    queryset = models.FlashcardsSet.objects.all()
    serializer_class = serializers.FlashcardSetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        category = self.request.query_params.get('category', None)
        name = self.request.query_params.get('name', None)
        user_only = self.request.query_params.get('user_only', None)
        author_name = self.request.query_params.get('author', None)
        if category is not None:
            self.queryset = self.queryset.filter(category__name=category)
        if name is not None:
            self.queryset = self.queryset.filter(Q(name__contains=name) | Q(slug__contains=name))
        if author_name is not None and (user_only == "False" or user_only is None):
            self.queryset = self.queryset.filter(Q(status="public") & Q(author__username=author_name))
        elif user_only == "True":
            self.queryset = self.queryset.filter(author=self.request.user)
        elif user_only == "False" or user_only is None:
            self.queryset = self.queryset.filter(Q(status="public") | Q(author=self.request.user))

        return self.queryset


class TagList(viewsets.ModelViewSet):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer
    permission_classes = [permissions.IsAuthenticated]


class CategoryList(viewsets.ModelViewSet):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = models.Category.objects.all()
        level = self.request.query_params.get('level', None)
        name = self.request.query_params.get('name', None)
        if level is not None:
            queryset = queryset.filter(level=level)
        if name is not None:
            queryset = queryset.filter(Q(name__contains=name) | Q(slug__contains=name))
        return queryset


class RatingList(mixins.CreateModelMixin,
                 mixins.ListModelMixin,
                 viewsets.GenericViewSet):
    serializer_class = serializers.RatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        if models.Rating.objects.filter(user=user, set=self.request.data.get("set")).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'detail': 'Już zagłosowałeś na ten zestaw.'})
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED,
                            data={'detail': 'Musisz być zalogowany, aby głosować.'})
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({"message": "Ocena została dodana!"}, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        queryset = models.Rating.objects.all()
        flashcard_set = self.request.query_params.get('flashcard_set', None)
        if flashcard_set is not None:
            queryset = queryset.filter(set__name=flashcard_set)
        return queryset


class GenerateQuiz(mixins.CreateModelMixin,
                   viewsets.GenericViewSet):
    queryset = models.Quiz.objects.all()
    serializer_class = serializers.QuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        instance = serializer.save()
        data = instance.serialize_quiz()
        return data


class CheckQuizView(UpdateAPIView):
    serializer_class = serializers.QuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        quiz_id = self.request.data.get('quiz_id', None)
        if quiz_id is not None:
            quiz = models.Quiz.objects.filter(id=quiz_id).first()
            raport = models.Quiz.check_quiz(quiz, request.data.dict())
            if raport.get("error") is not None:
                return Response(raport, status=status.HTTP_400_BAD_REQUEST)
            return Response(raport, status=status.HTTP_200_OK)
        return Response({"error": "Quiz nie został sprawdzony poprawnie."}, status=status.HTTP_400_BAD_REQUEST)
