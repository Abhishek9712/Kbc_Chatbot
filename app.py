from openai import OpenAI
import json
import os
import chainlit as cl
from elevenlabs import ElevenLabs
from dotenv import load_dotenv

load_dotenv()


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

tts = ElevenLabs(api_key=os.getenv("ELEVEN_API_KEY"))

VOICE_ID = "w09cTDhY0QowONlKenzM"

def kbc_response_format(data):
    answer = data.get("answer_text", "")
    return f"तो आइए... देखते हैं... इस प्रश्न का सही जवाब क्या है! \n{answer}\n"

def speak_like_bachchan(text: str) -> str:

    audio = tts.text_to_speech.convert(
        voice_id=VOICE_ID,
        model_id="eleven_multilingual_v2",
        text=text,
        output_format="mp3_44100_128"
    )

    file_path = "kbc_response.mp3"
    with open(file_path, "wb") as f:
        for chunk in audio:
            f.write(chunk)

    return file_path

def ask_kbc_bot(user_input: str) -> str:

    response = client.chat.completions.create(
        model="openai/gpt-4o",  
        messages=[
            {
                "role": "system",
                "content": (
                    "आप अमिताभ बच्चन की तरह जवाब देते हैं। "
                    "JSON format में जवाब दें: {\"question\": \"...\", \"answer_text\": \"...\"} "
                    "गम्भीर, धीमी और प्रभावशाली आवाज़ के अंदाज़ में लिखें। "
                    "लम्बे विराम और नाटकीय शैली अपनाएँ। "
                    "उत्तर अधिकतम 2 पंक्तियों में हो। "
                    "केवल हिंदी में लिखें, कोई अंग्रेज़ी शब्द न लिखें।"
                )
            },
            {
                "role": "user",
                "content": f"प्रश्न: {user_input}"
            }
        ],
        response_format={"type": "json_object"},
        max_tokens=300
    )

    message = response.choices[0].message
    
    try:
        args = json.loads(message.content)
        return kbc_response_format(args)
    except json.JSONDecodeError:
        return f"तो आइए... देखते हैं... इस प्रश्न का सही जवाब क्या है! \n{message.content}\n"

@cl.password_auth_callback
async def auth_callback(username:str, password:str):
    if (username,password) == ("admin","admin"):
        return cl.User(
            identifier="admin", metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return None

@cl.on_chat_start
async def start():
    await cl.Message("""
# नमस्कार! स्वागत है आपका  
## खोजबीन केंद्र में!

अपना सवाल पूछिए और कंप्यूटर जी का जवाब सुनिए!
    """).send()

    # app_user = cl.user_session.get("user")
    # await cl.Message(f"Hello {app_user.identifier}").send()


@cl.on_message
async def main(message: cl.Message):
    user_q = message.content.strip()
    msg = cl.Message(content="कंप्यूटर सोच रहा है...")
    await msg.send()

    try:
        bot_reply = ask_kbc_bot(user_q)
        audio_path = speak_like_bachchan(bot_reply)

        msg.content = f"**KBC Bot:**\n\n{bot_reply}"
        msg.elements = [cl.Audio(name="Voice Reply", path=audio_path)]
        await msg.update()

    except Exception as e:
        msg.content = f"समस्या आ गई:\n{str(e)}"
        await msg.update()

@cl.on_chat_end
def end():
    print("goodbye", cl.user_session.get("id"))