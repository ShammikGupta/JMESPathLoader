import json
from typing import Any, Callable, Dict, List, Optional
import jmespath

class JMLoader:
    class Document:
        def __init__(self, page_content: str, metadata: dict):
            self.page_content = page_content
            self.metadata = metadata

    def __init__(self,
                 file_path: str,
                 jmespath_schema: str,
                 content_key: Optional[str] = None,
                 metadata_func: Optional[Callable[[Dict, Dict], Dict]] = None,
                 text_content: bool = True):

        self.file_path = file_path
        self._jmespath_schema = jmespath.compile(jmespath_schema)
        self._content_key = content_key
        self._metadata_func = metadata_func
        self._text_content = text_content
        self.load_json()
    
    def load_json(self):
        with open(self.file_path, 'r') as f:
            self.data = json.load(f)
    
    def load(self) -> List['JMLoader.Document']:
        data = self._jmespath_schema.search(self.data)
        docs = []
        for i, sample in enumerate(data, 1):
            metadata = dict(
                source=self.file_path,
                seq_num=i,
            )
            if self._metadata_func is not None:
                metadata = self._metadata_func(sample, metadata)
            text = self._get_text(sample=sample, metadata=metadata)
            docs.append(self.Document(text, metadata))
        return docs        

    def _get_text(self, sample: Any, metadata: dict) -> str:
        if self._content_key is not None:
            content = sample.get(self._content_key)
        else:
            content = sample
        if self._text_content and not isinstance(content, str):
            raise ValueError(
                f"Expected page_content is string, got {type(content)} instead. "
                "Set `text_content=False` if the desired input for "
                "`page_content` is not a string"
            )
        elif isinstance(content, str):
            return content
        elif isinstance(content, dict):
            return json.dumps(content) if content else ""
        else:
            return str(content) if content is not None else ""     

    def convert_list_to_string(self, sample: Dict, metadata: Dict) -> Dict:
        for key, value in metadata.items():
            if isinstance(value, list):
                metadata[key] = ", ".join(str(v) for v in value)
        return metadata
