from app.services.ai_service import parse_resume

text = """
Muhammad

Skills:
Python
FastAPI
Docker

Projects:
InterviAI

Education:
BS Computer Science
"""

print(parse_resume(text))