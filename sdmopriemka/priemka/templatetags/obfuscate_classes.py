from django import template
import hashlib
import re

register = template.Library()

@register.filter
def obfuscate_classes(html_content):
    """
    Обфусцирует имена классов в HTML, заменяя их на хэшированные строки.
    """
    def replace_class(match):
        class_name = match.group(1)
        # Создаем короткий хэш для имени класса
        hashed_class = hashlib.md5(class_name.encode()).hexdigest()[:8]
        return f'class="{hashed_class}"'

    # Ищем все атрибуты class в HTML
    obfuscated_html = re.sub(r'class="([^"]*)"', replace_class, html_content)
    return obfuscated_html