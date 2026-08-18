---
title: KBC Voice Chatbot
emoji: 🎙️
colorFrom: purple
colorTo: yellow
sdk: docker
app_port: 7860
pinned: false
---

# KBC Voice Chatbot

A Hindi voice chatbot that role-plays Amitabh Bachchan from *Kaun Banega
Crorepati*. Ask a question in Hindi and get a dramatic, spoken-aloud answer.

Built with Chainlit, GPT-4o (via OpenRouter), and ElevenLabs TTS. See
`PROJECT_EXPLANATION.md` in this repo for a full stack breakdown.

## Required Space secrets

Set these under **Settings → Repository secrets** in the Space (not in
`.env`, which isn't deployed):

- `OPENROUTER_API_KEY`
- `ELEVEN_API_KEY`
