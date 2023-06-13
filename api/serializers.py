from rest_framework import serializers

from . import models


class FlashcardSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = models.Flashcard
        fields = ('id', 'author', 'front', 'back', 'flashcard_set')

    def validate(self, data):
        data = super(FlashcardSerializer, self).validate(data)
        if models.Flashcard.objects.filter(**data).exists():
            raise serializers.ValidationError("Flashcard already exists.")
        return data


class FlashcardSetSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = models.FlashcardsSet
        fields = ('id', 'name', 'author', 'status', 'is_premium', 'tag', 'category')

    def validate(self, data):
        data = super(FlashcardSetSerializer, self).validate(data)
        if models.FlashcardsSet.objects.filter(**data).exists():
            raise serializers.ValidationError("Flashcards set already exists.")
        return data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = ('id', 'name')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ('id', 'name', 'level')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ('id', 'username')


class RatingSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    rate = serializers.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = models.Rating
        fields = ('id', 'user', 'set', 'rate')


class QuizSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = models.Quiz
        fields = ('id', 'flashcards_set', 'author', 'timestamp', 'is_finished', 'score')