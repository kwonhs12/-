def voice(text):
    if text == '한국어(남성)':
        return "ko-KR-Chirp3-HD-Enceladus"
    elif text == "ko-KR-Chirp3-HD-Enceladus":
        return "한국어(남성)"
    elif text == "한국어(여성)":
        return "ko-KR-Chirp3-HD-Laomedeia"
    elif text == "ko-KR-Chirp3-HD-Laomedeia":
        return "한국어(여성)"
    
def gender(text):
    if text == '한국어(남성)':
        return "MALE"
    else:
        return "FEMALE"
    
def character(text):
    if text == "호랑이":
        return 'tiger'
    elif text == "tiger":
        return "호랑이"
    elif text == "dog":
        return "개"
    elif text=="개":
        return 'dog'