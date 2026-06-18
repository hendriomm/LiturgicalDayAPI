from enum import Enum
from typing import List, Optional, Any
from .localization import format_android_string

class LiturgicalClass(Enum):
    I = 1
    II = 2
    III = 3
    IV = 4

    def precedes(self, other: 'LiturgicalClass') -> bool:
        return self.value < other.value

    @property
    def name_res_id(self) -> str:
        return f"class_{self.value}"

class LiturgicalColor(Enum):
    WHITE = "WHITE"
    RED = "RED"
    GREEN = "GREEN"
    VIOLET = "VIOLET"
    BLACK = "BLACK"
    ROSE = "ROSE"

class LiturgicalDay:
    def __init__(
        self,
        name: str,
        name_res_id: Optional[str] = None,
        name_args: Optional[List[Any]] = None,
        liturgical_class: LiturgicalClass = LiturgicalClass.IV,
        color: LiturgicalColor = LiturgicalColor.GREEN,
        is_lord_feast: bool = False
    ):
        self.name = name
        self.name_res_id = name_res_id
        self.name_args = name_args
        self.liturgical_class = liturgical_class
        self.color = color
        self.is_lord_feast = is_lord_feast

    def observance_key(self) -> str:
        args_key = ",".join(str(arg) for arg in self.name_args) if self.name_args else ""
        if self.name_res_id:
            return f"res:{self.name_res_id}:{args_key}"
        else:
            return f"name:{self.name.strip().lower()}"

    def to_dict(self, translations: dict) -> dict:
        name = self.name
        if self.name_res_id:
            resolved_args = []
            if self.name_args:
                for arg in self.name_args:
                    if isinstance(arg, int):
                        ord_generic = translations.get("ord_generic", "%1$sth")
                        resolved_args.append(format_android_string(ord_generic, str(arg)))
                    elif isinstance(arg, str):
                        if arg in translations:
                            resolved_args.append(translations[arg])
                        elif arg.isdigit():
                            ord_generic = translations.get("ord_generic", "%1$sth")
                            resolved_args.append(format_android_string(ord_generic, arg))
                        else:
                            resolved_args.append(arg)
                    else:
                        resolved_args.append(str(arg))
            
            raw_template = translations.get(self.name_res_id, self.name)
            name = format_android_string(raw_template, *resolved_args)

        class_name_key = self.liturgical_class.name_res_id
        class_name = translations.get(class_name_key, f"{self.liturgical_class.name} Class")

        return {
            "name": name,
            "class_code": self.liturgical_class.name,
            "class_name": class_name,
            "color": self.color.name,
            "is_lord_feast": self.is_lord_feast
        }

class LiturgicalResult:
    def __init__(self, main_day: LiturgicalDay, commemorations: Optional[List[LiturgicalDay]] = None):
        self.main_day = main_day
        self.commemorations = commemorations or []

    def to_dict(self, translations: dict) -> dict:
        return {
            "main_day": self.main_day.to_dict(translations),
            "commemorations": [c.to_dict(translations) for c in self.commemorations]
        }
