from django.core.management.base import BaseCommand

from question_app.solver import Solver


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
        solver = Solver()
        titles, save = solver.database.update_vectors(options["update_all"])
        save(solver.encoder.generate_embeddings(titles))

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully generated OpenAI embeddings for all questions"
            )
        )
