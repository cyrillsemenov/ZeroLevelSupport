from datetime import datetime
from typing import Callable, Generator, Optional, Tuple, Type

# from loguru import logger
from pydantic import AnyUrl, BaseModel, ConfigDict, Field, create_model

from .form_builder import FormBuilder


form = FormBuilder(
    url=("Could you please tell me the URL of the site you're having issues with? ", (Optional[str], None)),
    geo= ("Which region or city are you located in right now? ", (Optional[str], None)),
    provider=("Which provider do you use? ", (Optional[str], None)),
    message= ("Do you want to add anything?", (Optional[str], None)),
    time=("This question sould be never asked", (datetime, Field(default_factory=lambda: datetime.now()))),
)
Problem: Type[BaseModel] = form.export_model("Problem")


class Form:
    def __init__(self, **kwargs) -> None:
        self.data = Problem(**kwargs)

    def get_next_empty_field(
        self,
    ) -> Generator[Optional[Tuple[str, Callable[[str], None]]], None, None]:
        none_fields = [k for k, v in iter(self.data) if v is None]
        for field_name in none_fields:
            # logger.debug(field_name)
            question = form.get_question(field_name, f"Could you please tell me {field_name}? ")
            def answer(value: str, field_name=field_name) -> None:
                # logger.debug(value, field_name)
                setattr(self.data, field_name, value)

            yield question, answer
        
        yield None, None


if __name__ == "__main__":
    d = Form()

    for q, a in iter(d.get_next_empty_field()):
        answer = input(q)
        a(answer)

    print(d.data)