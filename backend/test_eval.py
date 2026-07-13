
from app.services.ai_service import evaluate_answer
from app.models.parsed_resume import ParsedResume
resume = ParsedResume(
    name="Muhammad Irfan",
    email="abc@gmail.com",
    skills=["Python", "YOLO", "OpenCV"],
    education=["FAST"],
    experience=["Computer Vision Research"],
    projects=["Secure Object Detection"]
)
evaluation = evaluate_answer(
    parsed_resume=resume,
    role_applied="Computer Vision Engineer",
    difficulty="Medium",
    conversation="""
AI: Tell me about your YOLO project.
Candidate: I used YOLOv8 with OpenCV.
""",
    candidate_answer="I used YOLOv8 with OpenCV."
)