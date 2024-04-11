from django import forms

from .solver.adapters.django import KnowledgeBase


class KnowledgeBaseForm(forms.ModelForm):
    class Meta:
        model = KnowledgeBase
        fields = ["question", "answer"]
        widgets = {
            "question": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "Enter the question",
                }
            ),
            "answer": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Enter the answer",
                }
            ),
        }
