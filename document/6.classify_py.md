문자 처리
=========

가장 단순노가다가 많은 모듈이다. 전적으로 사용자 편의를 위해 만들어졌다.

우리가 사용하는 한국어 여성 모델은 "ko-KR-Chirp3-HD-Laomedeia"라는 이름을 가지고 있다.

그런데 이걸 사용자 인터페이스에 그대로 노출시키면 난해하게 느껴질것이다.

그래서 앱에서는 "한국어(여성)"이라고 부르고 코드 내부에선 "ko-KR-Chirp3-HD-Laomedeia"라고 불러야한다.

이를 원활하게 하기위해 텍스트를 변환시키는 코드이다.

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

코드의 구성도 아주 단순하다. 그냥 if-elif-else문을 이용해 텍스트를 변환시키는것이다. 만약 캐릭터가 추가되거나 음성모델을 바꾸고싶다면 이곳을 수정하면 된다.
