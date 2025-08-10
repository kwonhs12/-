import os
import sys
from google.cloud import texttospeech
from playsound import playsound # 음성 재생을 위해 playsound 사용
import tempfile # 임시 파일 생성을 위해 필요
import time
import json

if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

KEY = os.path.join(BASE_DIR, "boss-tts-key.json")
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = KEY

#말하기 함수
def speak(text):
    setting = json.load(open(os.path.join(BASE_DIR, 'setting.json')))
    gender_str = setting['gender'].upper()
    ssml_gender_enum = getattr(texttospeech.SsmlVoiceGender, gender_str)
    temp_file_path = None
    try:
        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code=setting['model'][0:5],
            name=setting['model'], 
            ssml_gender=ssml_gender_enum # FEMALE, MALE, NEUTRAL 중 선택
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=setting['rate'], # 속도 옵션 적용
            pitch=0.0,                 # 음높이 옵션 적용
            volume_gain_db=0.0 # 볼륨 옵션 적용
        )

        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_mp3_file:
            temp_mp3_file.write(response.audio_content)
            temp_file_path = temp_mp3_file.name # 임시 파일의 전체 경로를 얻습니다.

        playsound(temp_file_path) 
    except Exception as e: # 여기를 변경했습니다.
        print(f"음성 합성 오류: {e}")
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                # playsound가 파일 핸들을 완전히 해제할 시간을 주기 위해 짧은 지연을 줍니다.
                time.sleep(0.1) 
                os.remove(temp_file_path)
            except Exception as e:
                print(f"⚠️ 임시 파일 삭제 실패: {e}")