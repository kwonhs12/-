# https://pythonpyqt.com/pyqt-gif/  show gif
# https://wikidocs.net/22413  pyqtsignal
# https://wikidocs.net/239490  qthread
# https://docs.google.com/spreadsheets/d/1DK7QJv4rDdLpmld7LfqUJZ0xFs1LvF1e-7ffmBFFbu0/edit?gid=796023838#gid=796023838 대본 url
# https://cloud.google.com/text-to-speech/docs/list-voices-and-types#wavenet_voices 성우 목록
# https://stackoverflow.com/questions/36061433/how-do-i-locate-a-google-spreadsheet-id 스프레드시트 id란?
# https://devpouch.tistory.com/33 json파일 다루기
# GPT
# Gemini

import sys
import os
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import QDate ,QThread ,pyqtSignal, QUrl, QTimer, QEvent, Qt, QEventLoop
from PyQt5.QtGui import QMovie, QPixmap, QDesktopServices
#아래 두개는 py파일로 직접 제작된 모듈입니다
import speakmodule
import getsheet
import json
import classify

#파일 디렉토리 설정과정. 해당 과정을 거쳐야 디렉토리 오류가 안남
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#UI파일 등록
PA_form = uic.loadUiType(os.path.join(BASE_DIR, "pa.ui"))[0]
Virtual_form = uic.loadUiType(os.path.join(BASE_DIR, "virtual.ui"))[0]
Main_form = uic.loadUiType(os.path.join(BASE_DIR, "main.ui"))[0]
Setting_form = uic.loadUiType(os.path.join(BASE_DIR, "setting.ui"))[0]

#말하는 함수를 별도의 스레드에서 구동하기위한 클래스(gif와 동시에 실행하기위함)
class SpeakingThread(QThread):
    # 음성 재생이 시작되었음을 알리는 시그널
    speak_started = pyqtSignal()
    # 음성 재생이 완료되었음을 알리는 시그널
    speak_finished = pyqtSignal()

    def __init__(self, text_to_speak, parent=None):
        super().__init__(parent)
        self.text_to_speak = text_to_speak

    def run(self):
        # 음성 재생 시작 전 시그널 발생
        self.speak_started.emit()
        # speakmodule.speak 함수 호출 (실제 음성 재생)
        speakmodule.speak(self.text_to_speak)
        # 음성 재생 완료 후 시그널 발생
        self.speak_finished.emit()

class SettingWindow(QWidget, Setting_form):
    def __init__(self):
        super().__init__()
        setting = json.load(open(os.path.join(BASE_DIR, 'setting.json')))
        self.setupUi(self)
        self.setStyleSheet("background-color: #ADC2A9;") # 연한 회색 (Qt Designer에서 설정한 색상과 유사하게)
        self.setAutoFillBackground(True)
        self.ratebar.setValue(int(setting['rate']*100))
        self.pitchbar.setValue(int(setting['pitch']*100)+2000)
        self.volumebar.setValue(int(setting['volume']*100)+1000)
        self.ratelabel.setText(str(self.ratebar.value()/100.0))
        self.pitchlabel.setText(f"{((self.pitchbar.value()/100)-20.0):.2f}")
        self.volumelabel.setText(f"{((self.volumebar.value()/100)-10.0):.2f}")
        self.voiceselect.setCurrentText(classify.voice(setting['model']))
        self.characterselect.setCurrentText(classify.character(setting['character']))
        self.ratebar.valueChanged.connect(self.changerate)
        self.pitchbar.valueChanged.connect(self.changepitch)
        self.volumebar.valueChanged.connect(self.changevolume)
        self.resetbutton.clicked.connect(self.reset)
        self.returnbutton.clicked.connect(self.returning)
        self.applybutton.clicked.connect(self.apply)
        image_path = os.path.join(BASE_DIR, 'images', f'{classify.character(self.characterselect.currentText())}closed.png')
        self.charactershow.setPixmap(QPixmap(image_path))
        self.charactershow.setScaledContents(True)
        self.characterselect.currentIndexChanged.connect(self.changeimage)

    def changeimage(self):
        image_path = os.path.join(BASE_DIR, 'images', f'{classify.character(self.characterselect.currentText())}closed.png')
        self.charactershow.setPixmap(QPixmap(image_path))
        self.charactershow.setScaledContents(True)

    def apply(self):
        setting = json.load(open(os.path.join(BASE_DIR, 'setting.json')))
        setting['rate'] = round(self.ratebar.value() / 100.0, 2)
        setting['pitch'] = round((self.pitchbar.value()/100)-20.0, 2)
        setting['volume'] = round((self.volumebar.value()/100)-10.0, 2)
        setting['model'] = classify.voice(self.voiceselect.currentText())
        setting['gender'] = classify.gender(self.voiceselect.currentText())
        setting['character'] = classify.character(self.characterselect.currentText())
        with open(os.path.join(BASE_DIR, 'setting.json'), 'w', encoding='utf-8') as f:
            json.dump(setting, f, ensure_ascii=False, indent=4)
    
    def returning(self):
        self.close()

    def reset(self):
        self.ratebar.setValue(100)
        self.pitchbar.setValue(2000)
        self.volumebar.setValue(1000)
        self.voiceselect.setCurrentIndex(0)

    def changerate(self):
        self.ratelabel.setText(str(self.ratebar.value()/100.0))

    def changepitch(self):
        self.pitchlabel.setText(f"{((self.pitchbar.value()/100)-20.0):.2f}")

    def changevolume(self):
        self.volumelabel.setText(f"{((self.volumebar.value()/100)-10.0):.2f}")
#프로그램을 실행하면 처음 나타나는 창(메인화면)
class MainWindow(QWidget, Main_form):
    def __init__(self):
        #여기서 UI 속 요소들에 기능을 연결
        super().__init__()
        self.setupUi(self)
        self.setStyleSheet("background-color: #ADC2A9;") # 연한 회색 (Qt Designer에서 설정한 색상과 유사하게)
        self.setAutoFillBackground(True)
        self.to_PA.clicked.connect(self.topa)
        self.to_Virtual.clicked.connect(self.tovirtual)
        self.settingbutton.clicked.connect(self.setting)
        self.quitbutton.clicked.connect(QApplication.instance().quit)

    #이 아래에서부턴 연결한 기능들에 대해 작성

    def setting(self):
        self.settings_window = SettingWindow()
        self.settings_window.setWindowModality(Qt.ApplicationModal)
        self.settings_window.show()
    def topa(self):  #PA방송으로 가는 함수
        widget.addWidget(PAWindow())
        widget.showNormal()
        widget.resize(1060, 980)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def tovirtual(self):   #버추얼 화면으로 가는 함수
        widget.addWidget(VirtualWindow())
        widget.showFullScreen()
        widget.setCurrentIndex(widget.currentIndex()+1)
    
#PA방송 창
class PAWindow(QWidget, PA_form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.searchbutton.clicked.connect(self.search)
        self.setStyleSheet("background-color: #ADC2A9;") # 연한 회색 (Qt Designer에서 설정한 색상과 유사하게)
        self.setAutoFillBackground(True)
        self.textEdit.hide()
        self.listWidget.hide()
        self.info.hide()
        self.deletebutton.hide()
        self.combobox.hide()
        self.textEdit_2.hide()
        self.templatebutton.clicked.connect(self.template)
        self.custombutton.clicked.connect(self.custom)
        self.deletebutton.clicked.connect(self.delete)
        self.flag = 500
        self.eventflag = 500
        self.getevent.clicked.connect(self.get)
        self.writeevent.clicked.connect(self.write)
        self.pabutton.clicked.connect(self.pa)
        self.settingbutton.clicked.connect(self.setting)
        self.date.setDate(QDate.currentDate())
        self.returnbutton.clicked.connect(self.returning)
        self.quitbutton.clicked.connect(QApplication.instance().quit)

    def get(self):
        self.textEdit_2.hide()
        self.combobox.show()
        self.eventflag = 1
    
    def write(self):
        self.combobox.hide()
        self.textEdit_2.show()
        self.eventflag = 2

    def setting(self):
        self.settings_window = SettingWindow()
        self.settings_window.setWindowModality(Qt.ApplicationModal)
        self.settings_window.show()

    def returning(self):  #메인화면으로 돌아가는 함수
        widget.addWidget(MainWindow())
        widget.showNormal()
        widget.resize(1060, 980)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def delete(self):  #자율대본에서 작성한 내용을 삭제하는 버튼의 함수
        self.textEdit.clear()

    def template(self):  #'형식 선택'을 위한 UI를 나타내는 함수
        self.listWidget.show()
        self.textEdit.hide()
        self.info.hide()
        self.deletebutton.hide()
        self.flag=1

    def custom(self): #'직접 대본입력'을 위한 UI를 나타내는 함수
        self.textEdit.show()
        self.listWidget.hide()
        self.info.show()
        self.deletebutton.show()
        self.flag=2

    def search(self):  #행사를 불러오는 함수
        import requests
        import csv
        import io
        self.combobox.clear()
        url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQqkkkg5T9Rt2gwTAhSjO0Zn0SmOggtBWcws_NMO5q4u2GCWzpa-qVA_0AFZovKYQ04vCh7Qt7VuqYP/pub?output=csv"
        datevalue = self.date.date()
        response = requests.get(url)
        response.encoding = 'utf-8'
        reader = csv.reader(io.StringIO(response.text))

        today_str = f"{datevalue.month()}월 {datevalue.day()}일"

        events = []
        for i, row in enumerate(reader):
            if i == 0:
                continue  # 헤더 제외
            if len(row) >= 6:
                date_cell = row[2].strip()  # C열: 활동 날짜
                event = row[5].strip()      # F열: 행사명
                if today_str in date_cell and event:
                    events.append(event)
        print(events)
        for i in events:
            self.combobox.addItem(i)
        return events  #['방송방송'] <--- events의 형식을 나타냄(리스트임)
    

    def pa(self):  #방송하는 함수
        event = ""

        def has_coda(word):
            return not((ord(word[-1]) - 44032) % 28 == 0)
        #flag=1이면 형식 선택 상황, 2면 직접 입력 상황
        if self.eventflag == 1:
            event = self.combobox.currentText()
        elif self.eventflag == 2:
            event = self.textEdit_2.toPlainText()

        if self.flag == 1:
            if not event:
                QMessageBox.warning(self, '내용 오류', '행사명을 선택해 주세요')
            else:
                if self.listWidget.currentRow() == 0:
                    if not has_coda(event):
                        text = f"잠시 후 {event}가 있을 예정이니 채널을 2다시1번으로  맞추어 주시기  바랍니다."
                    else:
                        text = f"잠시 후 {event}이 있을 예정이니 채널을 2다시1번으로  맞추어 주시기  바랍니다."
                    speakmodule.speak(text)
                elif self.listWidget.currentRow() == 1:
                    if not has_coda(event):
                        text = f"지금부터 {event}가 시작됩니다. 모든 학생은 시청각실로 이동해주시기 바랍니다."
                    else:
                        text = f"지금부터 {event}이 시작됩니다. 모든 학생은 시청각실로 이동해주시기 바랍니다."
                    speakmodule.speak(text)
                elif self.listWidget.currentRow() == 2:
                    if not has_coda(event):
                        text = f"이상으로 {event}가 모두 종료되었습니다. 감사합니다."
                    else:
                        text = f"이상으로 {event}이 모두 종료되었습니다. 감사합니다."
                    speakmodule.speak(text)
        elif self.flag == 2:
            prompt = self.textEdit.toPlainText()
            if not prompt:
                QMessageBox.warning(self, '내용 오류', '내용을 입력해 주세요')
            else:
                newprompt=prompt.replace('{event}', event)
                speakmodule.speak(newprompt)
       
#버추얼 창
class VirtualWindow(QWidget, Virtual_form):
    enter_pressed = pyqtSignal()
    def __init__(self):
        super().__init__()
        set = json.load(open(os.path.join(BASE_DIR, 'setting.json')))
        self.setupUi(self)
        self.setStyleSheet("background-color: #ADC2A9;") # 연한 회색 (Qt Designer에서 설정한 색상과 유사하게)
        self.setAutoFillBackground(True)
        self.getsheetbutton.clicked.connect(self.getsheet)
        self.tosheetbutton.clicked.connect(self.tosheet)
        self.closemouth.hide()
        self.settingbutton.clicked.connect(self.setting)
        self.movie = QMovie(os.path.join(BASE_DIR,'images',f'{set['character']}speaking.gif'))
        self.speakinggif.setMovie(self.movie)
        self.launchbutton.clicked.connect(self.launch)
        self.quitbutton.clicked.connect(QApplication.instance().quit)
        self.returnbutton.clicked.connect(self.returning)
        QApplication.instance().installEventFilter(self) 
        self.cred = getsheet.getcred()
        self.speaking_thread = None 


    def setting(self):
        self.settings_window = SettingWindow()
        self.settings_window.setWindowModality(Qt.ApplicationModal)
        self.settings_window.show()

    def start_speaking_animation(self):
        set = json.load(open(os.path.join(BASE_DIR, 'setting.json')))
        new_movie_path = os.path.join(BASE_DIR,'images',f'{set['character']}speaking.gif')
        if self.movie and self.movie.fileName() == new_movie_path:
            # 이미 같은 GIF 파일이 로드되어 있으면 재생만 다시 시작
            self.movie.start()
        else:
            # 다른 GIF 파일이거나 처음 로드하는 경우, 새로 생성하고 연결
            if self.movie: # 기존 무비가 있다면 정지
                self.movie.stop()
            self.movie = QMovie(new_movie_path)
            self.speakinggif.setMovie(self.movie) # <-- !!! 새로 생성한 QMovie를 QLabel에 다시 연결 !!!
            self.movie.start()
        self.closemouth.hide()
        self.speakinggif.show()
        self.movie.start()

    def stop_speaking_animation(self):
        set = json.load(open(os.path.join(BASE_DIR, 'setting.json')))
        self.movie.stop()
        self.speakinggif.hide()
        self.closemouth.show()
        self.closemouth.setPixmap(QPixmap(os.path.join(BASE_DIR,'images',f'{set['character']}closed.png')) )
        self.closemouth.setScaledContents(True)
        
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
                self.enter_pressed.emit() # 엔터 키 감지 시 시그널 발생
                return True # 이벤트 처리 완료
        return super().eventFilter(obj, event) # 다른 이벤트는 부모 클래스로 전달
    
    def wait_for_enter(self):        
        loop = QEventLoop()
        # _enter_pressed 시그널이 발생하면 루프 종료
        self.enter_pressed.connect(loop.quit)
        
        loop.exec_() # 여기서 엔터 키가 눌릴 때까지 블로킹 (UI는 멈추지 않음)

    def returning(self): #메인화면으로 돌아가는 함수
        widget.addWidget(MainWindow())
        widget.showNormal()
        widget.resize(1060, 1080)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def launch(self): #말하는 함수
        set = json.load(open(os.path.join(BASE_DIR, 'setting.json')))
        prompt = getsheet.getscript(self.cred, self.comboBox.currentText())
        self.comboBox.hide()
        self.getsheetbutton.hide()
        self.launchbutton.hide()
        self.returnbutton.hide()
        self.settingbutton.hide()
        self.tosheetbutton.hide()
        self.quitbutton.hide()
        self.closemouth.show()
        self.closemouth.setPixmap(QPixmap(os.path.join(BASE_DIR,'images',f'{set['character']}closed.png')) )
        self.closemouth.setScaledContents(True)
        for i in prompt:
            if i['speaker'] != '사회자':
                if '타이머' in i['type']:
                    timeset = i['type'].split('=')[-1]
                    timesetset = timeset.split(':')
                    second = ((int(timesetset[0])*60)+(int(timesetset[-1])))*1000
                    loop = QEventLoop()
                    QTimer.singleShot(second, loop.quit)
                    loop.exec_()

                else:
                    self.wait_for_enter()

            else:                
                # SpeakingThread 인스턴스 생성 및 연결
                self.speaking_thread = SpeakingThread(i['text'])
                self.speaking_thread.speak_started.connect(self.start_speaking_animation)
                self.speaking_thread.speak_finished.connect(self.stop_speaking_animation)
                
                # 스레드 시작
                self.speaking_thread.start()
                
                # 음성 재생이 끝날 때까지 기다리는 로컬 이벤트 루프
                # QThread가 종료될 때 QThread.finished 시그널을 발생시키므로, 이를 활용합니다.
                speak_loop = QEventLoop()
                self.speaking_thread.finished.connect(speak_loop.quit)
                speak_loop.exec_() # 스레드가 끝날 때까지 여기서 대기
        loop = QEventLoop()
        QTimer.singleShot(5000, loop.quit)
        loop.exec_()
        self.closemouth.hide()
        self.comboBox.show()
        self.getsheetbutton.show()
        self.launchbutton.show()
        self.settingbutton.show()
        self.quitbutton.show()
        self.returnbutton.show()
        self.tosheetbutton.show()

    def tosheet(self): #시트로 연결하는 함수
        target_url = "https://docs.google.com/spreadsheets/d/1DK7QJv4rDdLpmld7LfqUJZ0xFs1LvF1e-7ffmBFFbu0/edit?gid=796023838#gid=796023838"  # 실제 URL로 변경하세요.
        QDesktopServices.openUrl(QUrl(target_url))

    def getsheet(self): #시트(대본명) 목록을 불러오는 함수
        self.comboBox.clear()
        lists = getsheet.getsheetnames(self.cred)
        for i in lists:
            self.comboBox.addItem(i)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = QStackedWidget()
    widget.addWidget(MainWindow())
    widget.setStyleSheet("background-color: #ADC2A9;") # MainWindow와 동일한 색상으로 설정
    widget.setAutoFillBackground(True)
    widget.resize(1060, 980)
    widget.show()
    app.exec_()