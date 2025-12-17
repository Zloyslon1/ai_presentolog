"""
Test the new text splitter approach.
"""

from presentation_design.extraction.text_splitter import TextSplitter

def test_title_slide():
    """Test first slide with title and subtitle."""
    text = """Презентация по проекту
Название компании
2024"""
    
    components = TextSplitter.split_slide_text(text, slide_index=0)
    
    print("=== TITLE SLIDE TEST ===")
    for comp in components:
        print(f"Role: {comp['role']}")
        print(f"Content: {comp['content']}")
        print()

def test_content_slide_with_list():
    """Test content slide with heading and list."""
    text = """Ключевые задачи
    
Основные цели проекта:
1. Разработать прототип
2. Провести тестирование
3. Внедрить систему

Следующие шаги определены командой."""
    
    components = TextSplitter.split_slide_text(text, slide_index=1)
    
    print("=== CONTENT SLIDE WITH LIST ===")
    for comp in components:
        print(f"Role: {comp['role']}")
        print(f"Content: {comp['content'][:100]}")
        if comp.get('is_list'):
            print(f"List type: {comp['content_type']}")
            print(f"Items: {comp['items']}")
        print()

def test_heading_detection():
    """Test heading detection."""
    text = """Важные метрики

КЛЮЧЕВЫЕ ПОКАЗАТЕЛИ

Результаты работы:
• Рост продаж
• Увеличение команды
• Выход на рынки"""
    
    components = TextSplitter.split_slide_text(text, slide_index=2)
    
    print("=== HEADING DETECTION TEST ===")
    for comp in components:
        print(f"Role: {comp['role']}")
        print(f"Content: {comp['content'][:80]}")
        print()

if __name__ == "__main__":
    test_title_slide()
    test_content_slide_with_list()
    test_heading_detection()
    
    print("✅ All tests completed!")
