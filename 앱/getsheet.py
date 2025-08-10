import os.path
import sys
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

#경로 오류가 나지 않게하는 과정
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#인증키가 담긴 파일
KEY_FILE_PATH = os.path.join(BASE_DIR, "boss-tts-key.json")

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"] 

def getcred():
    #인증함수
    try:
        creds = service_account.Credentials.from_service_account_file(
            KEY_FILE_PATH, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)
        return service
    except Exception as e:
        return None
    
def getsheetnames(service, spreadsheet_id='1DK7QJv4rDdLpmld7LfqUJZ0xFs1LvF1e-7ffmBFFbu0'):
    #시트목록 탐색함수
    if not service:
        return []
    try:
        spreadsheet_metadata = service.spreadsheets().get(
            spreadsheetId=spreadsheet_id, 
            fields='sheets.properties.title' # 시트 제목만 가져오도록 필터링
        ).execute()

        sheet_names = []
        if 'sheets' in spreadsheet_metadata:
            for sheet in spreadsheet_metadata['sheets']:
                if 'properties' in sheet and 'title' in sheet['properties']:
                    sheet_names.append(sheet['properties']['title'])
        
        return sheet_names

    except HttpError as err:
        return []
    except Exception as e:
        return []
    
def getscript(service, sheet_name, spreadsheet_id='1DK7QJv4rDdLpmld7LfqUJZ0xFs1LvF1e-7ffmBFFbu0'):
    #대본 가져오기 함수
    if not service:
        return []
    try:
        # 시트 이름과 전체 범위를 지정하여 데이터 가져오기 (예: '시트1!A:Z')
        # A:Z는 충분히 넓은 범위를 의미하며, 실제 사용된 데이터만 반환됩니다.
        range_name = f'{sheet_name}!A:Z' 
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, 
            range=range_name
        ).execute()
        
        values = result.get("values", [])
        
        if not values:
            print(f"⚠️ '{sheet_name}' 시트에서 데이터를 찾을 수 없습니다.")
            return []

        # 첫 번째 행을 헤더로 사용 (발언자, 내용, type)
        headers = values[0]
        data_rows = values[1:] # 두 번째 행부터 실제 데이터

        script_list = []
        for row in data_rows:
            # 각 행의 데이터를 딕셔너리로 매핑
            # 헤더와 데이터의 길이가 다를 경우를 대비하여 .get() 사용
            # 실제 스프레드시트의 열 순서에 맞게 인덱스를 조정해야 합니다.
            # 예시: '발언자'가 0번째, '내용'이 1번째, 'type'이 2번째 열이라고 가정
            
            # 헤더 인덱스를 찾아 안전하게 값 가져오기
            speaker_idx = headers.index('발언자') if '발언자' in headers else -1
            content_idx = headers.index('내용') if '내용' in headers else -1
            type_idx = headers.index('type') if 'type' in headers else -1

            speaker = row[speaker_idx] if speaker_idx != -1 and speaker_idx < len(row) else ""
            content = row[content_idx] if content_idx != -1 and content_idx < len(row) else ""
            type_ = row[type_idx] if type_idx != -1 and type_idx < len(row) else ""

            dic = {
                'speaker': speaker,
                'text': content,
                'type': type_
            }
            script_list.append(dic)
        
        return script_list

    except HttpError as err:
        return []
    except Exception as e:
        return []