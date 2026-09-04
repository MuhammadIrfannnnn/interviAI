# InterviAI

**AI-powered, voice-first mock interview practice.**

> Part of **BridgeAI** — where academia meets industry. InterviAI is the first working piece of that vision: real, spoken interview practice that adapts to you.

---

## Why InterviAI

Every year, technically capable graduates walk into interviews they've never actually rehearsed out loud. Reading questions off a page isn't the same as answering them under pressure, in real time, with someone listening. InterviAI closes that gap — a candidate uploads their CV, picks a target role and difficulty, and steps into a live, adaptive, voice-driven interview that reacts to what they actually say.

## What it does

- **Upload your CV** and select a target role and difficulty level
- **Speak your answers** — no typing required, the AI listens and responds in real time
- **Adaptive questioning** — each next question is generated based on your resume and how you've answered so far, not a fixed script
- **Evaluated across real competencies** — technical knowledge, communication, confidence, and problem-solving, not just right/wrong
- **Personalized report** at the end — strengths, weaknesses, evidence pulled from your actual answers, and a learning roadmap

## How it works

```
Candidate speaks
      │
      ▼
Groq Whisper  ──►  Gemini  ──►  ElevenLabs
(speech → text)   (evaluates &      (text → speech)
                   generates next
                    question)
      │
      ▼
Candidate hears the next question — loop repeats each turn
```

A React/TypeScript frontend manages the conversation loop, calling three focused FastAPI endpoints in sequence each turn. All session data, transcripts, and generated reports are stored in MySQL.

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | React, TypeScript |
| Backend | FastAPI (Python) |
| Database | MySQL |
| Interview intelligence | Gemini |
| Speech-to-text | Groq Whisper |
| Text-to-speech | ElevenLabs |

## Getting started

```bash
# Clone the repo (this branch)
git clone -b feature-voice-interview https://github.com/MuhammadIrfannnnn/interviAI.git
cd interviAI

# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

You'll need API keys for Gemini, Groq, and ElevenLabs — add them to a `.env` file in the backend directory (see `.env.example`).

## Project status

🎤 **Live today:** voice-based mock interview practice, end to end — CV upload, adaptive spoken interview, personalized report.

🔜 **On the roadmap (BridgeAI vision):**
- Course-to-career mapping — link university coursework directly to real interview questions
- Live industry radar — surface real-time in-demand skills from job postings
- AI virtual internship — a simulated first week at a company, with realistic workplace tasks and feedback

## Team

Built by the InterviAI team.

---

*InterviAI — practice interviews out loud, with an AI that listens and speaks back.*