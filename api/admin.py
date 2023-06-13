from django.contrib import admin

import api.models as models

admin.site.register(models.Flashcard)
admin.site.register(models.FlashcardsSet)
admin.site.register(models.Tag)
admin.site.register(models.Category)
admin.site.register(models.Quiz)
admin.site.register(models.Rating)
admin.site.register(models.QuizQuestion)
admin.site.register(models.QuizAnswer)