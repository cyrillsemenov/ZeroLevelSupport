from django.core.management.base import BaseCommand

from question_app.utils import Transformer


class Command(BaseCommand):
    help = "Generate OpenAI embeddings for all questions in the knowledge base"

    def add_arguments(self, parser):
        parser.add_argument("--api-key", type=str, help="OpenAI API key")
        parser.add_argument(
            "--embedding-model", type=str, help="Model name for embeddings"
        )
        parser.add_argument(
            "--update-all",
            action="store_true",
            help="Update embeddings for all questions",
        )

    def handle(self, *args, **options):
        transformer = Transformer.get(api_key=options["api_key"])
        transformer.update_base(options["update_all"])

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully generated OpenAI embeddings for all questions"
            )
        )
