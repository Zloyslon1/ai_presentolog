import sqlite3
import json

conn = sqlite3.connect('db/presentation_jobs.db')
cursor = conn.cursor()
cursor.execute('SELECT id, slides_json FROM jobs ORDER BY updated_at DESC LIMIT 1')
row = cursor.fetchone()

print(f'Job: {row[0]}')
slides = json.loads(row[1])
print(f'Slides count: {len(slides)}')

s = slides[2]  # Check slide 2
print(f'Slide 2 titleText: {repr(s.get("titleText", "NOT SET"))[:100]}')
print(f'Slide 2 mainTextContent: {repr(s.get("mainTextContent", "NOT SET"))[:100]}')
print(f'Slide 2 titleFontSize: {s.get("titleFontSize", "NOT SET")}')
print(f'Slide 2 mainTextFontSize: {s.get("mainTextFontSize", "NOT SET")}')

conn.close()
