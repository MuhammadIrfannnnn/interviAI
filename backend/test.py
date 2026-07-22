from google import genai

client = genai.Client(api_key="AQ.Ab8RN6IrP4l3N97vMC1Lb5sE4yvTitLM5OTcnV-VG0lo1BUG9Q")

for model in client.models.list():
        print(model.name)