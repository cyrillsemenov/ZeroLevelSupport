import os
from django.core.management.base import BaseCommand
from question_app.models import KnowledgeBase
from openai import OpenAI
from question_app.utils import Transformer


class Command(BaseCommand):
    help = 'Generate OpenAI embeddings for all questions in the knowledge base'

    def add_arguments(self, parser):
        parser.add_argument('--api-key', type=str, help='OpenAI API key')
        parser.add_argument('--embedding-model', type=str, help='Model name for embeddings')
        parser.add_argument('--update-all', action='store_true', help='Update embeddings for all questions')

    def handle(self, *args, **options):
        transformer = Transformer.get(api_key=options['api_key'])
        # client = OpenAI(api_key=options['api_key'])
        questions = KnowledgeBase.objects.all()

        # response = client.embeddings.create(
        #     input=[question.question for question in questions if options['update_all'] or question.embedding is None],
        #     model=options['embedding_model']
        # )
        vectors = transformer.generate_embeggings(
            [question.question for question in questions if options['update_all'] or question.embedding is None]
        )
        for question, embedding in zip(questions, vectors):
            question.set_embedding(embedding)
            question.save()
        
        self.stdout.write(self.style.SUCCESS('Successfully generated OpenAI embeddings for all questions'))
