# Service Account Setup Guide

Service Account позволяет серверу получать доступ к Google APIs без интерактивной OAuth авторизации.

## Шаг 1: Создание Service Account

1. Откройте [Google Cloud Console](https://console.cloud.google.com/)
2. Выберите ваш проект (тот же, где настроен OAuth)
3. Перейдите в **IAM & Admin** → **Service Accounts**
   - URL: https://console.cloud.google.com/iam-admin/serviceaccounts

4. Нажмите **+ CREATE SERVICE ACCOUNT**

5. Заполните форму:
   - **Service account name**: `ai-presentolog-server`
   - **Service account ID**: `ai-presentolog-server` (заполнится автоматически)
   - **Description**: `Server account for AI Presentolog to access Google Slides`

6. Нажмите **CREATE AND CONTINUE**

7. **Grant this service account access to project** (можно пропустить):
   - Нажмите **CONTINUE** (роли не нужны для доступа к публичным презентациям)

8. **Grant users access to this service account** (можно пропустить):
   - Нажмите **DONE**

## Шаг 2: Создание ключа (JSON)

1. В списке Service Accounts найдите только что созданный аккаунт
2. Нажмите на email аккаунта (например, `ai-presentolog-server@your-project.iam.gserviceaccount.com`)
3. Перейдите на вкладку **KEYS**
4. Нажмите **ADD KEY** → **Create new key**
5. Выберите тип **JSON**
6. Нажмите **CREATE**

Файл автоматически скачается (например, `your-project-123456-abcdef.json`)

## Шаг 3: Установка ключа в проект

**Windows PowerShell:**

```powershell
# Перейдите в директорию проекта
cd C:\Users\Zloyslon\Desktop\Projects\ai_presentolog

# Создайте папку credentials если её нет
New-Item -ItemType Directory -Force -Path credentials

# Переместите скачанный файл и переименуйте
Move-Item "$env:USERPROFILE\Downloads\your-project-*.json" "credentials\service_account.json"
```

**Или вручную:**
1. Скопируйте скачанный JSON файл
2. Вставьте в `C:\Users\Zloyslon\Desktop\Projects\ai_presentolog\credentials\`
3. Переименуйте в `service_account.json`

## Шаг 4: Включение Google Slides API

Убедитесь, что Google Slides API включен:

1. Откройте: https://console.cloud.google.com/apis/library/slides.googleapis.com
2. Нажмите **ENABLE** если API не включен

## Шаг 5: Настройка доступа к презентациям

**ВАЖНО:** Service Account может читать только:
1. **Публичные презентации** ("Все в интернете")
2. **Презентации, к которым явно предоставлен доступ** Service Account email

### Вариант A: Публичные презентации
Сделайте презентацию публичной:
- Откройте презентацию в Google Slides
- Нажмите **Share** (Поделиться)
- В разделе "General access" выберите **Anyone with the link** (Все, у кого есть ссылка)
- Права: **Viewer** (Читатель)
- Нажмите **Done**

### Вариант B: Предоставить доступ Service Account
Если презентация приватная, добавьте Service Account как читателя:
- Откройте презентацию в Google Slides
- Нажмите **Share**
- Добавьте email Service Account (например, `ai-presentolog-server@your-project.iam.gserviceaccount.com`)
- Выберите роль **Viewer**
- Нажмите **Send** (можно снять галочку "Notify people")

## Проверка установки

После установки запустите тест:

```bash
python test_service_account.py
```

## Безопасность

⚠️ **ВАЖНО:**
- Файл `service_account.json` содержит приватный ключ
- НЕ публикуйте его в Git
- НЕ делитесь им публично
- Файл уже добавлен в `.gitignore`

Если ключ скомпрометирован:
1. Удалите ключ в Google Cloud Console
2. Создайте новый ключ
3. Обновите файл `service_account.json`
