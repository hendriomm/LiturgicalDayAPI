import os
import re
import xml.etree.ElementTree as ET

def format_android_string(template: str, *args) -> str:
    """
    Formats an Android-style template string (e.g. '%1$s Sunday') using Python args.
    """
    if not template:
        return ""
    # Replace positional args like %1$s, %1$d with {0}
    temp = template
    temp = re.sub(r'%(\d+)\$[sSdD]', lambda m: f"{{{int(m.group(1)) - 1}}}", temp)
    # Replace simple %s, %d with {}
    temp = re.sub(r'%[sSdD]', '{}', temp)
    try:
        return temp.format(*args)
    except Exception:
        return template

class LocalizationManager:
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), "data")
        self.data_dir = data_dir
        self.translations = {}
        self.load_all()

    def load_all(self):
        locales = {
            "pt": "values",
            "en": "values-en",
            "es": "values-es",
            "fr": "values-fr",
            "de": "values-de",
            "pt-br": "values-pt-rBR"
        }
        for lang, folder in locales.items():
            path = os.path.join(self.data_dir, folder, "strings.xml")
            if os.path.exists(path):
                self.translations[lang] = self.parse_strings(path)
            else:
                self.translations[lang] = {}

    def parse_strings(self, path: str) -> dict:
        try:
            tree = ET.parse(path)
            root = tree.getroot()
            strings = {}
            for elem in root.findall("string"):
                name = elem.attrib.get("name")
                text = elem.text or ""
                # Clean up XML/Android specific escapes
                text = text.replace("\\'", "'").replace('\\"', '"')
                strings[name] = text
            return strings
        except Exception as e:
            print(f"Error parsing strings file {path}: {e}")
            return {}

    def get_translations(self, lang: str) -> dict:
        lang_normalized = lang.lower().replace("_", "-")
        if lang_normalized in self.translations:
            return self.translations[lang_normalized]
            
        base = lang_normalized.split("-")[0]
        if base in self.translations:
            return self.translations[base]
            
        # Fallback list: pt-br -> pt -> en -> first available
        if lang_normalized.startswith("pt"):
            if "pt-br" in self.translations:
                return self.translations["pt-br"]
            if "pt" in self.translations:
                return self.translations["pt"]
        
        if "en" in self.translations:
            return self.translations["en"]
        if "pt" in self.translations:
            return self.translations["pt"]
        return next(iter(self.translations.values())) if self.translations else {}
