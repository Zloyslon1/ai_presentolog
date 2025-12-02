"""
Quick test for content analyzer functionality.
"""

from presentation_design.extraction.content_analyzer import ContentAnalyzer

def test_numbered_list():
    """Test numbered list detection."""
    text = """Основные задачи:
1. Провести анализ
2. Разработать решение
3. Внедрить систему"""
    
    result = ContentAnalyzer.analyze_text_structure(text)
    print("=== NUMBERED LIST TEST ===")
    print(f"Content type: {result['content_type']}")
    print(f"Items found: {len(result['items'])}")
    for i, item in enumerate(result['items'], 1):
        print(f"  {i}. {item}")
    print()

def test_bullet_list():
    """Test bullet list detection."""
    text = """Преимущества:
• Высокая скорость
• Простота использования
• Масштабируемость
• Безопасность"""
    
    result = ContentAnalyzer.analyze_text_structure(text)
    print("=== BULLET LIST TEST ===")
    print(f"Content type: {result['content_type']}")
    print(f"Items found: {len(result['items'])}")
    for item in result['items']:
        print(f"  • {item}")
    print()

def test_emphasis_detection():
    """Test emphasis detection."""
    texts = [
        "ВАЖНАЯ ИНФОРМАЦИЯ",
        "Regular text here",
        "Title Case Text Here"
    ]
    
    print("=== EMPHASIS DETECTION TEST ===")
    for text in texts:
        result = ContentAnalyzer.analyze_text_structure(text)
        print(f"Text: '{text}'")
        print(f"  Has emphasis (ALL CAPS): {result['has_emphasis']}")
        print(f"  Is title case: {result['is_title_case']}")
    print()

def test_list_formatting():
    """Test list formatting."""
    items = ["First item", "Second item", "Third item"]
    
    print("=== LIST FORMATTING TEST ===")
    
    numbered = ContentAnalyzer.format_list_items(items, 'numbered_list')
    print("Numbered format:")
    print(numbered)
    print()
    
    bulleted = ContentAnalyzer.format_list_items(items, 'bullet_list')
    print("Bulleted format:")
    print(bulleted)
    print()

def test_mixed_content():
    """Test mixed content analysis."""
    text = """КЛЮЧЕВЫЕ ПОКАЗАТЕЛИ

Рост метрик:
1. Продажи: +45%
2. Клиенты: +120%
3. Доход: +78%"""
    
    print("=== MIXED CONTENT TEST ===")
    lines = text.split('\n\n')
    for idx, line in enumerate(lines, 1):
        result = ContentAnalyzer.analyze_text_structure(line)
        print(f"Section {idx}: {line[:30]}...")
        print(f"  Type: {result['content_type']}")
        print(f"  Emphasis: {result['has_emphasis']}")
        print(f"  Items: {len(result['items'])}")
    print()

if __name__ == "__main__":
    print("🧪 CONTENT ANALYZER TESTS\n")
    print("=" * 50)
    print()
    
    test_numbered_list()
    test_bullet_list()
    test_emphasis_detection()
    test_list_formatting()
    test_mixed_content()
    
    print("=" * 50)
    print("✅ All tests completed!")
