import json
from typing import Union


class JsonEncoder(json.JSONEncoder):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__indentation_level = 0

    def __convert_list(self, o: Union[list, tuple]) -> str:
        output = [self.encode(el) for el in o]
        return '[{0}]'.format(", ".join(output))
    
    def __convert_dict(self, o: dict) -> str:
        if not o:
            return "{}"
        
        self.__indentation_level += 1
        output = []
        for k, v in o.items():
            output.append('{0}{1}: {2}'.format(self.indent_str, json.dumps(k), self.encode(v)))
        self.__indentation_level -= 1
        if self.indent:
            return "{\n" + ",\n".join(output) + "\n" + self.indent_str + "}"
        else:
            return '{' + ", ".join(output) + '}'

    def encode(self, o: Union[list, tuple, dict]) -> str:
        if isinstance(o, (list, tuple)):
            return self.__convert_list(o)
        elif isinstance(o, dict):
            return self.__convert_dict(o)
        else:
            return json.dumps(o)

    def iterencode(self, o, **kwargs):
        return self.encode(o)

    @property
    def indent_str(self):
        return " " * self.__indentation_level * self.indent if self.indent else ''
