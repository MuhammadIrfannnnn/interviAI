# from google import genai

# client = genai.Client(api_key="AIzaSyDewB7YaiNL9nz20IVB2veU0hhiSyEPR2E")

# for model in client.models.list():
#     print(model.name)
from google import genai
from app.core.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="Say hello"
)

print(response.text)