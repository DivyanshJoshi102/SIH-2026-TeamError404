from django.contrib import admin

from .models import Question, Quiz, QuizAttempt


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "eco_points", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("title", "description")
    inlines = [QuestionInline]


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("student", "quiz", "score", "total_questions", "earned_points", "submitted_at")
    search_fields = ("student__full_name", "student__email", "quiz__title")
