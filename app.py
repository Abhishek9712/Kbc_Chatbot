from openai import OpenAI
import json
import os
import chainlit as cl
from elevenlabs import ElevenLabs
from dotenv import load_dotenv

load_dotenv()


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
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
    tools = [{
        "type": "function",
        "name": "kbc_response_format",
        "description": "Format answer like Amitabh Bachchan (KBC style)",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {"type": "string"},
                "answer_text": {"type": "string"}
            },
            "required": ["question", "answer_text"]
        }
    }]

    response = client.responses.create(
        model="gpt-4o-mini",
        input=(
    f"प्रश्न: {user_input}. प्रश्न को भी हिंदी में दोबारा लिखकर आउटपुट में शामिल करें। कोई अंग्रेज़ी शब्द न लिखें।"
    f"अमिताभ बच्चन के समान गम्भीर, धीमी और प्रभावशाली आवाज़ के अंदाज़ में लिखें। "
    f"लम्बे विराम और नाटकीय शैली अपनाएँ। "
    f"उत्तर अधिकतम 2 पंक्तियों में हो। "
    f"कोई अंग्रेज़ी शब्द न लिखें। "
    f"उत्तर केवल function_call arguments में दें।"
    ),
        tools=tools
    )

    output = response.output[0]
    if output.type == "function_call":
        args = json.loads(output.arguments)
        return kbc_response_format(args)

    return response.output_text


@cl.on_chat_start
async def start():
    await cl.Message("""
# नमस्कार! स्वागत है आपका  
## खोजबीन केंद्र में!

अपना सवाल पूछिए और कंप्यूटर जी का जवाब सुनिए!
    """).send()


@cl.on_message
async def main(message: cl.Message):
    user_q = message.content.strip()
    if user_q.lower() in ["exit", "quit", "samapt", "band karo"]:
        end()
        goodbye_text = "तो दोस्तों, यह वार्तालाप यहीं समाप्त होती है। आप सबका अत्यंत धन्यवाद!"
        audio_path = speak_like_bachchan(goodbye_text)

        await cl.Message(
            content=f"**KBC Bot:**\n\n{goodbye_text}",
            elements=[cl.Audio(name="Goodbye Voice", path=audio_path)]
        ).send()
        return
    msg = cl.Message(content="🎤 कंप्यूटर सोच रहा है...")
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
    pass