from django.contrib import admin, messages

from .models import KnowledgeBase
from .utils import Transformer


@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ("question", "display_answer", "embedding_indicator")
    actions = ["update_embedding"]

    def display_answer(self, obj):
        """Return the first 50 characters of the answer for display."""
        char_limit = 50
        string = obj.answer if obj.answer else ""
        truncated = (
            (string[:char_limit] + "...") if char_limit < len(string) else string
        )
        return truncated

    display_answer.short_description = "Answer Preview"  # Sets column header

    def embedding_indicator(self, obj):
        return "Yes" if obj.has_embedding() else "No"

    def update_embedding(self, request, queryset):
        transformer = Transformer.get()
        for kb in queryset:
            embedding = transformer.generate_embeddings(
                [
                    kb.question,
                ]
            )
            kb.set_embedding(embedding)
            kb.save()
        self.message_user(
            request,
            "Selected questions' embeddings have been updated.",
            messages.SUCCESS,
        )

    update_embedding.short_description = "Update Embedding for selected questions"

    embedding_indicator.short_description = "Embedding Created"
