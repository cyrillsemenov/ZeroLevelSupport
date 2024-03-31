import os
from typing import List, Optional, Tuple
import numpy as np
# from sentence_transformers import SentenceTransformer, util
# from loguru import logger
# from sklearn.metrics.pairwise import cosine_similarity

from string import Template
from .database import database

import openai

PROMPT_TEMPLATE = """Вот список вопросов:
$faq_index

Я представлю вопрос другими словами. Пожалуйста, определи, какой из перечисленных вопросов я задал, и отправь его мне без изменений. Если вопроса в списке нет, ответь ":not_found". Если вопрос касается сбоя в работе ресурса или шатдаун, используй формат:
:report {"url": "[если доступен]", "geo": "[регион или город, если доступен]",  "provider": "[провайдер, если доступен]",  "message": "[любой дополнительный контекст]"}
Убери поля из отчёта, информация по которым отсутствует и приведи url в надлежащий вид, если он присутствует. Отвечай строго по форме, пожалуйста, ничего не добавляя от себя.

Вопрос: $question
"""

class App:
    def __init__(self, similarity_threshold: float = 0.7, model: str = "all-MiniLM-L6-v2") -> None:
        pass
        self._similarity_threshold = similarity_threshold
        # self._model = SentenceTransformer(model)
        # self.vectors = {q: self._model.encode(q, convert_to_tensor=True) for q in database.keys()}
        # self.client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    class NotFound(Exception):
        pass

    class Report(Exception):
        pass

    def find_answer(self, question: str, similarity_threshold: Optional[float] = None) -> str:
        """Searches for the most similar question in the database and returns its answer

        Args:
            question (str): question for which an answer is sought
            similarity_threshold (int): the lowest similarity which does note raise a NotFound

        Returns:
            str: answer to the question that best matches the input question

        Raises:
            NotFound: if no question in the database is similar enough to the input question
        """
        if similarity_threshold is None:
            similarity_threshold = self._similarity_threshold

        if question.startswith(":easter_egg"):
            raise App.Report('{"url": "https://nasvyazi.org/", "geo": "The best place in a whole World (Saburtalo)", "message": "Example of hidden report from message to support"}')
        
        raise self.NotFound("No suitable answer found in the database.")
        # Analize question here using designed prompt        
        
        # response = self.client.completions.create(
        #     model="gpt-3.5-turbo-instruct",
        #     prompt=Template(PROMPT_TEMPLATE).substitute(faq_index="\n".join(database.keys()), question=question),
        #     n=1,
        #     max_tokens=256,
        #     # temperature=1,
        #     presence_penalty=-1,
        #     frequency_penalty=-1
        # )
        # completion = response.choices[0].text.strip("\"' ")
        # logger.info(question)
        # logger.info(completion)

        # if ":report" in completion:
        #     raise self.Report(completion[len(":report "):])

        # if ":not_found" in completion:
        #     raise self.NotFound("No suitable answer found in the database.")
        
        # question_vector = self._model.encode(completion, convert_to_tensor=True)
        # highest_similarity = 0
        # best_match = None

        # for db_question, db_vector in self.vectors.items():
        #     similarity = util.pytorch_cos_sim(question_vector, db_vector)
        #     if similarity > highest_similarity:
        #         highest_similarity = similarity
        #         best_match = db_question

        # if highest_similarity < similarity_threshold:
        #     raise self.NotFound("No suitable answer found in the database.")

        # return database.get(best_match)


# class QuestionAnsweringApp:
#     def __init__(self, model_name='all-MiniLM-L6-v2', knowledge_base=None, similarity_threshold=0.6, top_n=5):
#         self._model = SentenceTransformer(model_name)
#         self.database = knowledge_base if knowledge_base else {}
#         self.similarity_threshold = similarity_threshold
#         self.top_n = top_n
#         self.vectors = {question: self._model.encode(question, convert_to_tensor=True) for question in self.database.keys()}

#     class NotFound(Exception):
#         pass

#     def find_similar_questions(self, question: str) -> List[Tuple[str, float]]:
#         question_vector = self._model.encode(question, convert_to_tensor=True)
#         similarities = []

#         for db_question, db_vector in self.vectors.items():
#             similarity = util.pytorch_cos_sim(question_vector, db_vector)[0].item()
#             if similarity >= self.similarity_threshold:
#                 similarities.append((db_question, similarity))

#         # Sort by similarity
#         similarities.sort(key=lambda x: x[1], reverse=True)

#         # Return the top N matches
#         return similarities[:self.top_n]




# if __name__ == "__main__":
#     app = QuestionAnsweringApp(knowledge_base=database, top_n=3)

#     while True:
#         try:
#             question = input("Q: ")
#             similar_questions = app.find_similar_questions(question)
#             if not similar_questions:
#                 print("No suitable answers found in the database.")
#             else:
#                 for q, similarity in similar_questions:
#                     print(f"Question: {q}, Similarity: {similarity:.4f}, Answer: app.database[q]")
#         except QuestionAnsweringApp.NotFound as e:
#             print(e)


#     app = App(0.7)

#     while True:
#         try:
#             question = input("Q: ")
#             # Looking for an answer in DB (answer -> vector  -> value -> text)
#             # and raising exception if answe is not found
#             answer = app.find_answer(question)
#             print("A:", answer)
#         except App.NotFound as e:
#             print(e)