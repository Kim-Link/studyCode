import time
import requests
from dotenv import load_dotenv
import os
import json
import base64
import boto3

# .env 파일 로드
load_dotenv()



def create_jwt(client_id, service_account, key_id):
    current_time = int(time.time())

    # JWT의 JOSE 헤더 설정
    headers = {
        "alg": "RS256",
        "typ": "JWT",
    }

    # JWT의 페이로드 설정 (예시 데이터)
    payload = {
        "iss": client_id,
        "sub": service_account,
        "iat": current_time,  # 발급 시간 설정 (현재 시간)
        "exp": current_time + 3600  # 만료 시간 설정 (현재 시간 + 1시간)
    }

    # JOSE 헤더와 페이로드를 base64url 인코딩
    encoded_header = base64.urlsafe_b64encode(json.dumps(headers).encode()).decode().rstrip("=")
    encoded_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")

    # 서명되지 않은 JWT 생성 (signing_input)
    signing_input = f"{encoded_header}.{encoded_payload}"


    # KMS 클라이언트 생성
    kms_client = boto3.client('kms')

    # 데이터 서명 (JWT 서명)
    response = kms_client.sign(
        KeyId=key_id,
        Message=signing_input.encode('utf-8'),
        MessageType='RAW',
        SigningAlgorithm='RSASSA_PKCS1_V1_5_SHA_256',
    )
    signature = response['Signature']

    print("Signature: ", signature)  # 디버그 출력

    # Base64로 인코딩된 서명 생성
    encoded_signature = base64.urlsafe_b64encode(signature).decode().rstrip("=")

    print("Encoded Signature: ", encoded_signature)  # 디버그 출력

    # 서명된 JWT 생성
    jwt_token = f'{signing_input}.{encoded_signature}'
    return jwt_token

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
        token_response = response.json()
        if 'access_token' not in token_response:
            print(f"Error in token response: {token_response}")
        return token_response
    except ValueError:
        print("Response is not in JSON format")
        return None

def get_post_list(token_response, board_id):
    # 엑세스 토큰
    access_token = token_response.get('access_token')
    if not access_token:
        print("No access token found in token response.")
        return

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
    access_token = token_response.get('access_token')
    if not access_token:
        print("No access token found in token response.")
        return

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
    key_id = os.environ.get('KMS_KEY_ID')
    scope = os.environ.get('SCOPE')
    private_key = os.environ.get('PRIVATE_KEY')

    # board 구분
    board_id = os.environ.get('NEWS_BOARD_ID')
    if event['board'] == 'recruit':
        board_id = os.environ.get('EMPLOY_BOARD_ID')

    jwt_token = create_jwt(client_id, service_account, key_id)
    print("JWT Token: ", jwt_token)  # 디버그 출력
    token_response = request_token(jwt_token, client_id, client_secret, scope)

    if not token_response or 'access_token' not in token_response:
        return {
            'statusCode': 400,
            'body': 'Failed to retrieve access token'
        }

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
