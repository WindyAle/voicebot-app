# from dotenv import load_dotenv
# load_dotenv()

# --- env 관련 처리 ---
# 로컬이 아닌 streamlit-cloud에서는 .env를 사용할 수 없으므로 (GitHub에 올라가지 않기 때문)
# secrets 설정(TOML)에 OPENAI_API_KEY를 설정해야 한다.
# OPENAI_API_KEY="api key" 입력

from openai import OpenAI
import os
import base64

client = OpenAI()

def stt(audio):
    """
    1. 녹음된 음성을 mp3 파일로 변환하여 메모리에 임시 저장
    2. whisper로 텍스트 추출
    3. 용도가 없어진 파일을 삭제
    """
    # 파일로 변환
    filename = 'prompt.mp3'
    audio.export(filename, format='mp3')

    # whisper-1 모델로 stt
    with open(filename, 'rb') as f:
        transcription = client.audio.transcriptions.create(
            model='whisper-1',
            file=f
        )
    
    # 음원 파일 삭제
    os.remove(filename)

    return transcription.text

def ask_gpt(messages, model):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=1,
        top_p=1,
        max_tokens=4096
    )

    return response.choices[0].message.content

def tts(response):
    filename = 'voice.mp3'

    with client.audio.speech.with_streaming_response.create(
        model='tts-1',
        voice='alloy',
        input=response
    ) as stream:
        stream.stream_to_file(filename)

    # 음원을 base64 문자열로 인코딩
    with open(filename, 'rb') as f:
        data = f.read()
        base64_encoded = base64.b64encode(data).decode()

    # 음원파일 삭제
    os.remove(filename)

    return base64_encoded