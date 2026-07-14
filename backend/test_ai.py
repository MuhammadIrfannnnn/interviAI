# from app.services.ai_service import parse_resume

# text = """
# Muhammad

# Skills:
# Python
# FastAPI
# Docker

# Projects:
# InterviAI

# Education:
# BS Computer Science
# """

# print(parse_resume(text))
from google import genai

client = genai.Client(api_key="AIzaSyDewB7YaiNL9nz20IVB2veU0hhiSyEPR2E")

for model in client.models.list():
    print(model.name)