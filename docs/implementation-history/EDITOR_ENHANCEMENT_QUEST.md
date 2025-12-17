# Quest: Улучшение редактора презентаций

## Контекст проекта

Это веб-приложение для создания Google Slides презентаций. Пользователь загружает исходную презентацию, редактирует контент в визуальном редакторе, и система генерирует новую презентацию через Google Slides API.

### Ключевые файлы:
- **Frontend редактор**: `templates/slide_editor.html` (HTML + JavaScript + Tailwind CSS)
- **Backend генерации**: `presentation_design/generation/presentation_builder.py` (Python, Google Slides API)
- **Web сервер**: `web_app.py` (Flask)

### Текущее состояние:
- ✅ Текстовые поля (заголовок, основной текст, дополнительный текст)
- ✅ Выбор шрифта (Google Fonts)
- ✅ Размер шрифта (заголовок, текст)
- ✅ Изображения (drag&drop, позиционирование, слои)
- ✅ Ориентация страницы (горизонтальная/вертикальная)
- ❌ **Таблицы** - UI есть, но НЕ работает генерация
- ❌ **Выбор фона** - нет UI и функционала
- ❌ **Форматирование текста** (bold/italic/underline) - нет
- ❌ **Маркированные/нумерованные списки** - нет
- ❌ **Акцентные плашки** - нет
- ❌ **Выравнивание текста** - UI есть, но НЕ работает
- ❌ **Цвет шрифта** - нет
- ❌ **Однотонный фон слайда** - нет

---

## Задачи

### 1. Исправить таблицы

**Проблема**: В UI есть кнопка "Добавить таблицу" и модальное окно, но таблицы не сохраняются и не генерируются.

**Frontend (slide_editor.html)**:
```javascript
// Нужно реализовать функцию addTable()
function addTable() {
    const rows = parseInt(document.getElementById('tableRows').value);
    const columns = parseInt(document.getElementById('tableColumns').value);
    const x = parseInt(document.getElementById('tableX').value);
    const y = parseInt(document.getElementById('tableY').value);
    const width = parseInt(document.getElementById('tableWidth').value);
    const height = parseInt(document.getElementById('tableHeight').value);
    
    const table = {
        id: 'table_' + Date.now(),
        rows: rows,
        columns: columns,
        position: { x, y },
        size: { width, height },
        cellData: {} // Формат: {"0_0": "текст ячейки", "0_1": "текст", ...}
    };
    
    if (!slides[currentSlideIndex].tables) {
        slides[currentSlideIndex].tables = [];
    }
    slides[currentSlideIndex].tables.push(table);
    
    closeTableModal();
    updateTablesList();
    updateSlidePreview();
}
```

**Нужно добавить**:
- Редактор содержимого ячеек таблицы (модальное окно с сеткой input полей)
- Предпросмотр таблицы на слайде
- Функцию `updateTablesList()` для отображения списка таблиц

**Backend (presentation_builder.py)**:
Метод `_add_table()` уже существует (строки 1103-1161), но нужно проверить что данные корректно передаются.

---

### 2. Добавить выбор фона слайда

**UI (slide_editor.html)** - добавить в панель настроек:
```html
<div class="pt-4 border-t">
    <h3 class="text-sm font-semibold text-gray-700 mb-2">Фон слайда</h3>
    
    <!-- Тип фона -->
    <div class="space-y-2">
        <label class="flex items-center">
            <input type="radio" name="bgType" value="none" checked onchange="changeBackgroundType('none')">
            <span class="ml-2 text-sm">Без фона (белый)</span>
        </label>
        <label class="flex items-center">
            <input type="radio" name="bgType" value="solid" onchange="changeBackgroundType('solid')">
            <span class="ml-2 text-sm">Однотонный цвет</span>
        </label>
        <label class="flex items-center">
            <input type="radio" name="bgType" value="gradient" onchange="changeBackgroundType('gradient')">
            <span class="ml-2 text-sm">Градиент</span>
        </label>
    </div>
    
    <!-- Выбор цвета (показывать при solid) -->
    <div id="solidColorPicker" class="hidden mt-3">
        <label class="block text-xs text-gray-600 mb-1">Цвет фона</label>
        <input type="color" id="bgColor" value="#FFFFFF" class="w-full h-10 rounded border" onchange="updateBackground()">
    </div>
    
    <!-- Градиент (показывать при gradient) -->
    <div id="gradientPicker" class="hidden mt-3 space-y-2">
        <div class="flex gap-2">
            <div class="flex-1">
                <label class="block text-xs text-gray-600 mb-1">Цвет 1</label>
                <input type="color" id="gradientColor1" value="#667eea" class="w-full h-8 rounded border" onchange="updateBackground()">
            </div>
            <div class="flex-1">
                <label class="block text-xs text-gray-600 mb-1">Цвет 2</label>
                <input type="color" id="gradientColor2" value="#764ba2" class="w-full h-8 rounded border" onchange="updateBackground()">
            </div>
        </div>
        <select id="gradientDirection" class="w-full p-2 border rounded text-sm" onchange="updateBackground()">
            <option value="to right">Горизонтальный →</option>
            <option value="to bottom">Вертикальный ↓</option>
            <option value="to bottom right">Диагональный ↘</option>
        </select>
    </div>
</div>
```

**JavaScript**:
```javascript
function changeBackgroundType(type) {
    document.getElementById('solidColorPicker').classList.toggle('hidden', type !== 'solid');
    document.getElementById('gradientPicker').classList.toggle('hidden', type !== 'gradient');
    updateBackground();
}

function updateBackground() {
    const bgType = document.querySelector('input[name="bgType"]:checked').value;
    const preview = document.getElementById('slidePreview');
    
    let background = { type: bgType };
    
    if (bgType === 'none') {
        preview.style.background = '#FFFFFF';
        background.color = '#FFFFFF';
    } else if (bgType === 'solid') {
        const color = document.getElementById('bgColor').value;
        preview.style.background = color;
        background.color = color;
    } else if (bgType === 'gradient') {
        const c1 = document.getElementById('gradientColor1').value;
        const c2 = document.getElementById('gradientColor2').value;
        const dir = document.getElementById('gradientDirection').value;
        preview.style.background = `linear-gradient(${dir}, ${c1}, ${c2})`;
        background.gradient = { color1: c1, color2: c2, direction: dir };
    }
    
    slides[currentSlideIndex].background = background;
}
```

**Backend (presentation_builder.py)** - в методе `_build_advanced_slide_content()`:
```python
# Добавить обработку фона
background = slide_data.get('background', {})
bg_type = background.get('type', 'none')

if bg_type == 'solid':
    color = background.get('color', '#FFFFFF')
    requests.append({
        'updatePageProperties': {
            'objectId': slide_id,
            'pageProperties': {
                'pageBackgroundFill': {
                    'solidFill': {
                        'color': {
                            'rgbColor': self._hex_to_rgb(color)
                        }
                    }
                }
            },
            'fields': 'pageBackgroundFill'
        }
    })
# Примечание: Google Slides API не поддерживает градиенты напрямую,
# нужно использовать изображение-градиент или оставить только solid
```

---

### 3. Добавить форматирование текста (Bold/Italic/Underline)

**Подход**: Использовать специальные маркеры в тексте, которые будут парситься при генерации.

**UI** - добавить панель инструментов над textarea:
```html
<div class="flex gap-1 mb-2 border-b pb-2">
    <button onclick="wrapSelection('**', '**')" class="px-3 py-1 bg-gray-100 rounded hover:bg-gray-200 font-bold" title="Жирный">B</button>
    <button onclick="wrapSelection('*', '*')" class="px-3 py-1 bg-gray-100 rounded hover:bg-gray-200 italic" title="Курсив">I</button>
    <button onclick="wrapSelection('__', '__')" class="px-3 py-1 bg-gray-100 rounded hover:bg-gray-200 underline" title="Подчёркнутый">U</button>
    <span class="border-l mx-2"></span>
    <button onclick="insertListMarker('•')" class="px-3 py-1 bg-gray-100 rounded hover:bg-gray-200" title="Маркированный список">• Список</button>
    <button onclick="insertListMarker('1.')" class="px-3 py-1 bg-gray-100 rounded hover:bg-gray-200" title="Нумерованный список">1. Нумерация</button>
</div>
```

**JavaScript**:
```javascript
function wrapSelection(before, after) {
    const textarea = document.getElementById('mainTextInput');
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const text = textarea.value;
    const selectedText = text.substring(start, end);
    
    textarea.value = text.substring(0, start) + before + selectedText + after + text.substring(end);
    textarea.selectionStart = start + before.length;
    textarea.selectionEnd = end + before.length;
    textarea.focus();
    
    updateSlidePreview();
}

function insertListMarker(marker) {
    const textarea = document.getElementById('mainTextInput');
    const start = textarea.selectionStart;
    const text = textarea.value;
    
    // Найти начало текущей строки
    const lineStart = text.lastIndexOf('\n', start - 1) + 1;
    
    textarea.value = text.substring(0, lineStart) + marker + ' ' + text.substring(lineStart);
    textarea.selectionStart = textarea.selectionEnd = start + marker.length + 1;
    textarea.focus();
    
    updateSlidePreview();
}
```

**Backend (presentation_builder.py)** - добавить парсинг форматирования:
```python
def _parse_formatted_text(self, text: str) -> list:
    """
    Парсит текст с маркерами форматирования.
    Возвращает список сегментов: [{text, bold, italic, underline}, ...]
    
    Маркеры:
    - **text** = жирный
    - *text* = курсив  
    - __text__ = подчёркнутый
    """
    import re
    
    segments = []
    current_pos = 0
    
    # Паттерны в порядке приоритета
    patterns = [
        (r'\*\*(.+?)\*\*', {'bold': True}),
        (r'\*(.+?)\*', {'italic': True}),
        (r'__(.+?)__', {'underline': True}),
    ]
    
    # ... реализация парсинга ...
    
    return segments
```

---

### 4. Добавить маркированные и нумерованные списки

**Уже частично реализовано** в `formatMainText()` для предпросмотра. Нужно:

1. Улучшить визуальное отображение в превью
2. Передавать информацию о списках в backend
3. Использовать Google Slides API `createParagraphBullets`

**Backend** - метод `_apply_list_formatting()` уже есть (строки 672-731), нужно вызывать его при обнаружении списков.

---

### 5. Добавить акцентные плашки (Highlight Boxes)

**UI** - добавить кнопку и модальное окно:
```html
<button onclick="showAccentBoxModal()" class="w-full px-3 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 text-sm">
    📦 Добавить акцентный блок
</button>

<!-- Модальное окно -->
<div id="accentBoxModal" class="hidden fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg p-6 max-w-md w-full">
        <h3 class="text-lg font-bold mb-4">Акцентный блок</h3>
        <div class="space-y-4">
            <div>
                <label class="block text-sm font-medium mb-2">Текст</label>
                <textarea id="accentText" rows="3" class="w-full p-2 border rounded"></textarea>
            </div>
            <div class="grid grid-cols-2 gap-2">
                <div>
                    <label class="block text-sm text-gray-600">Цвет фона</label>
                    <input type="color" id="accentBgColor" value="#E0E7FF" class="w-full h-10 rounded">
                </div>
                <div>
                    <label class="block text-sm text-gray-600">Цвет границы</label>
                    <input type="color" id="accentBorderColor" value="#4F46E5" class="w-full h-10 rounded">
                </div>
            </div>
            <div class="grid grid-cols-2 gap-2">
                <div>
                    <label class="block text-sm text-gray-600">X</label>
                    <input type="number" id="accentX" value="50" class="w-full p-2 border rounded">
                </div>
                <div>
                    <label class="block text-sm text-gray-600">Y</label>
                    <input type="number" id="accentY" value="200" class="w-full p-2 border rounded">
                </div>
            </div>
            <div class="grid grid-cols-2 gap-2">
                <div>
                    <label class="block text-sm text-gray-600">Ширина</label>
                    <input type="number" id="accentWidth" value="300" class="w-full p-2 border rounded">
                </div>
                <div>
                    <label class="block text-sm text-gray-600">Высота</label>
                    <input type="number" id="accentHeight" value="100" class="w-full p-2 border rounded">
                </div>
            </div>
        </div>
        <div class="flex gap-2 mt-6">
            <button onclick="addAccentBox()" class="flex-1 px-4 py-2 bg-indigo-500 text-white rounded-lg">Добавить</button>
            <button onclick="closeAccentBoxModal()" class="flex-1 px-4 py-2 bg-gray-300 rounded-lg">Отмена</button>
        </div>
    </div>
</div>
```

**Структура данных**:
```javascript
{
    id: 'accent_123',
    text: 'Важная информация',
    position: { x: 50, y: 200 },
    size: { width: 300, height: 100 },
    backgroundColor: '#E0E7FF',
    borderColor: '#4F46E5',
    borderWidth: 2,
    borderRadius: 8, // скругление
    textColor: '#1E1B4B',
    fontSize: 14
}
```

**Backend** - добавить метод `_add_accent_box()`:
```python
def _add_accent_box(self, slide_id: str, box_data: dict, index: int) -> list:
    """Создаёт прямоугольник с текстом (акцентный блок)."""
    requests = []
    
    box_id = f"accent_{slide_id}_{index}"
    position = box_data.get('position', {'x': 50, 'y': 200})
    size = box_data.get('size', {'width': 300, 'height': 100})
    bg_color = box_data.get('backgroundColor', '#E0E7FF')
    border_color = box_data.get('borderColor', '#4F46E5')
    text = box_data.get('text', '')
    
    # Создать прямоугольник
    requests.append({
        'createShape': {
            'objectId': box_id,
            'shapeType': 'ROUND_RECTANGLE',
            'elementProperties': {
                'pageObjectId': slide_id,
                'size': {
                    'width': {'magnitude': self._pt_to_emu(size['width']), 'unit': 'EMU'},
                    'height': {'magnitude': self._pt_to_emu(size['height']), 'unit': 'EMU'}
                },
                'transform': {
                    'scaleX': 1,
                    'scaleY': 1,
                    'translateX': self._pt_to_emu(position['x']),
                    'translateY': self._pt_to_emu(position['y']),
                    'unit': 'EMU'
                }
            }
        }
    })
    
    # Стилизация (фон + граница)
    requests.append({
        'updateShapeProperties': {
            'objectId': box_id,
            'shapeProperties': {
                'shapeBackgroundFill': {
                    'solidFill': {
                        'color': {'rgbColor': self._hex_to_rgb(bg_color)}
                    }
                },
                'outline': {
                    'outlineFill': {
                        'solidFill': {
                            'color': {'rgbColor': self._hex_to_rgb(border_color)}
                        }
                    },
                    'weight': {'magnitude': 2, 'unit': 'PT'}
                }
            },
            'fields': 'shapeBackgroundFill,outline'
        }
    })
    
    # Добавить текст
    if text:
        requests.append({
            'insertText': {
                'objectId': box_id,
                'text': text,
                'insertionIndex': 0
            }
        })
    
    return requests
```

---

### 6. Исправить выравнивание по вертикали/горизонтали

**Проблема**: UI кнопки есть, но выравнивание применяется только к превью, не к генерируемой презентации.

**Backend (presentation_builder.py)** - в `_build_advanced_slide_content()`:

Текущий код не учитывает вертикальное выравнивание внутри текстового блока. Нужно:

1. Изменить размер и позицию текстового блока в зависимости от выравнивания
2. Или использовать `contentAlignment` в свойствах фигуры

```python
# После создания текстового блока, добавить:
vertical_alignment_map = {
    'top': 'TOP',
    'center': 'MIDDLE', 
    'bottom': 'BOTTOM'
}
vertical = text_position.get('vertical', 'top')

requests.append({
    'updateShapeProperties': {
        'objectId': element_id,
        'shapeProperties': {
            'contentAlignment': vertical_alignment_map.get(vertical, 'TOP')
        },
        'fields': 'contentAlignment'
    }
})
```

---

### 7. Добавить выбор цвета шрифта

**UI** - добавить в панель настроек:
```html
<div>
    <label class="block text-sm font-medium text-gray-700 mb-2">Цвет текста</label>
    <div class="flex gap-2">
        <input type="color" id="textColor" value="#000000" class="w-full h-10 rounded border" onchange="changeTextColor()">
        <input type="text" id="textColorHex" value="#000000" class="w-24 p-2 border rounded text-sm font-mono" oninput="syncTextColor()">
    </div>
</div>
```

**JavaScript**:
```javascript
function changeTextColor() {
    const color = document.getElementById('textColor').value;
    document.getElementById('textColorHex').value = color;
    
    // Обновить превью
    document.getElementById('previewTitle').style.color = color;
    document.getElementById('previewMain').style.color = color;
    
    // Сохранить в слайд
    slides[currentSlideIndex].textColor = color;
}

function syncTextColor() {
    const hex = document.getElementById('textColorHex').value;
    if (/^#[0-9A-Fa-f]{6}$/.test(hex)) {
        document.getElementById('textColor').value = hex;
        changeTextColor();
    }
}
```

**Backend** - в `_build_advanced_slide_content()`:
```python
text_color = slide_data.get('textColor', '#000000')

# В updateTextStyle добавить:
'foregroundColor': {
    'opaqueColor': {
        'rgbColor': self._hex_to_rgb(text_color)
    }
}
```

---

## Структура данных слайда (итоговая)

```javascript
{
    title: "Заголовок",
    mainText: "Текст с **форматированием** и *курсивом*",
    secondaryText: "Дополнительный текст",
    
    // Настройки шрифта
    fontFamily: "Roboto",
    titleSize: 44,
    textSize: 18,
    textColor: "#333333",
    
    // Выравнивание
    textPosition: {
        vertical: "top",    // top | center | bottom
        horizontal: "left"  // left | center | right
    },
    
    // Фон
    background: {
        type: "solid",  // none | solid | gradient
        color: "#FFFFFF",
        gradient: { color1: "#667eea", color2: "#764ba2", direction: "to right" }
    },
    
    // Элементы
    images: [...],
    tables: [...],
    arrows: [...],
    accentBoxes: [...]  // НОВОЕ
}
```

---

## Приоритет задач

1. **Высокий**: Цвет шрифта, однотонный фон, выравнивание текста — базовые функции
2. **Средний**: Таблицы, форматирование текста (bold/italic)
3. **Низкий**: Акцентные плашки, градиенты

---

## Тестирование

После каждого изменения проверять:
1. Превью в редакторе отображается корректно
2. Данные сохраняются в slides array
3. Данные отправляются на backend при генерации
4. Google Slides API запросы формируются правильно
5. Итоговая презентация содержит все элементы

## Технические заметки

- Google Slides API использует EMU (English Metric Units): 1 PT = 12700 EMU
- Цвета передаются как RGB float 0-1, не hex
- Максимум 500 запросов в одном batchUpdate
- Градиенты фона НЕ поддерживаются Google Slides API напрямую
