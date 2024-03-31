from typing import Any, Dict, Optional, Tuple

from pydantic import BaseModel, ConfigDict, create_model

class FormBuilder:
    def __init__(self, **kwargs) -> None:
        self.data = kwargs

    def add_field(self, key: str, question: str, _type: type, default: Any) -> 'FormBuilder':
        self.data[key] = (question, (_type, default))
        return self
    
    @property
    def fields(self) -> Dict[str, Tuple[type, Any]]:
        return {k: f for k, (_, f) in self.data.items()}
    
    def get_question(self, key: str, default: Optional[str]) -> Optional[str]:
        question, _ = self.data.get(key, (default, None))
        return question
    
    def export_model(self, model_name: str) -> type[BaseModel]:
        return create_model(
            model_name,
            # __config__=ConfigDict(validate_assignment=True),
            **self.fields,
        )