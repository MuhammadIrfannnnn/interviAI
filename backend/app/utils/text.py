import re

def clean_resume_text(text:str)->str:
    text=re.sub(r"[ \t]+"," ",text)
    text=re.sub(r"\n{3,}","\n\n",text)
    text=text.strip()
    return text