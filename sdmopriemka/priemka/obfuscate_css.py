import hashlib
import re

def obfuscate_css(css_content):
    """
    Обфусцирует имена классов в CSS, заменяя их на хэшированные строки.
    """
    def replace_class(match):
        class_name = match.group(1)
        hashed_class = hashlib.md5(class_name.encode()).hexdigest()[:8]
        return f'.{hashed_class}'

    # Ищем все имена классов в CSS (начинаются с точки)
    obfuscated_css = re.sub(r'\.([^{,\s]+)', replace_class, css_content)
    return obfuscated_css

# Пример использования
if __name__ == "__main__":
    with open("/Users/memberremember/Software/Projects/Kursachi/SDMOPriemka/sdmopriemka/priemka/static/css/priemka_lc.css", "r") as css_file:
        css_content = css_file.read()
    
    obfuscated_css = obfuscate_css(css_content)
    
    with open("/Users/memberremember/Software/Projects/Kursachi/SDMOPriemka/sdmopriemka/priemka/static/css/priemka_lc_obfuscated.css", "w") as css_file:
        css_file.write(obfuscated_css)