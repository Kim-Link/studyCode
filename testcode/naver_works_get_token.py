import jwt
import time
import requests
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

def create_jwt(client_id, service_account, private_key):
    current_time = int(time.time())
    payload = {
        "iss": client_id,
        "sub": service_account,
        "iat": current_time,
        "exp": current_time + 3600
    }
    headers = {
        "alg": "RS256",
        "typ": "JWT"
    }

    token = jwt.encode(
        payload,
        private_key,
        algorithm='RS256',
        headers=headers
    )
    print("token", token)
    return token

def request_token(jwt_token, client_id, client_secret, scope):
    url = 'https://auth.worksmobile.com/oauth2/v2.0/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
        'client_id': client_id,
        'client_secret': client_secret,
        'assertion': jwt_token,
        'scope': scope
    }

    response = requests.post(url, headers=headers, data=data)

    try:
        return response.json()
    except ValueError:
        print("Response is not in JSON format")
        return None

def get_post_list(token_response, board_id):
    # 엑세스 토큰
    access_token = token_response['access_token']

    # API 엔드포인트
    url = f'https://www.worksapis.com/v1.0/boards/{board_id}/posts'

    # 헤더 설정
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    # GET 요청 보내기
    response = requests.get(url, headers=headers)

    # 응답 처리
    if response.status_code == 200:
        posts_data = response.json()
        posts = posts_data['posts']

        print(posts)
        return posts
    else:
        print(f"Failed to retrieve posts from board {board_id}. Status code: {response.status_code}")
        print(response.text)


def get_post(token_response, board_id, post_id):
    # 엑세스 토큰
    access_token = token_response['access_token']

    # API 엔드포인트
    url = f'https://www.worksapis.com/v1.0/boards/{board_id}/posts/{post_id}'

    # 헤더 설정
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    # GET 요청 보내기
    response = requests.get(url, headers=headers)

    # 응답 처리
    if response.status_code == 200:
        post_details = response.json()
        return post_details
    else:
        print(f"Failed to retrieve boards. Status code: {response.status_code}")
        print(response.text)
        return None

def lambda_handler(event, context):
    func_type = event['type']

    # Client 정보
    client_id = os.environ.get('CLIENT_ID')
    client_secret = os.environ.get('CLIENT_SECRET')
    service_account = os.environ.get('SERVICE_ACCOUNT')
    private_key = os.environ.get('PRIVATE_KEY')
    scope = os.environ.get('SCOPE')

    # board 구분
    board_id = os.environ.get('NEWS_BOARD_ID')
    if event['board'] == 'recruit':
        board_id = os.environ.get('EMPLOY_BOARD_ID')

    jwt_token = create_jwt(client_id, service_account, private_key)
    token_response = request_token(jwt_token, client_id, client_secret, scope)

    result = ''
    # type 구분
    if func_type == 'list':
        result = get_post_list(token_response, board_id)
    if func_type == 'post':
        result = get_post(token_response, board_id, event['postId'])

    return {
        'statusCode': 200,
        'body': result
    }

if __name__ == "__main__":
    # board : news / recruit
    # type : list / post
    # postId : 'type' 이 'post' 인 경우에 id 적어줌
    event = { 'board': 'news', 'type': 'list', 'postId': 4070000000142597171}
    context = {}
    lambda_handler(event, context)