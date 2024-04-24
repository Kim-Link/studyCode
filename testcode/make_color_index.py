import boto3
import json
import requests
from dotenv import load_dotenv
import os

# load .env
load_dotenv()

# AWS 계정 정보 설정
aws_access_key = os.environ.get('KEY_ID')
aws_secret_key = os.environ.get('SECRET_ACCESS_KEY')
region_name = os.environ.get('AWS_REGION_NAME')
bucket_name = os.environ.get('AWS_S3_BUCKET_NAME')

# OpenSearch 엔드포인트 및 인증 정보 설정
open_search_endpoint = os.environ.get("AWS_OS_NODE")
opensearch_user = os.environ.get("AWS_OS_USERNAME")
opensearch_pass = os.environ.get("AWS_OS_PASSWORD")
auth = (opensearch_user, opensearch_pass)

# S3 클라이언트 생성
s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region_name)

# RGB -> Hex 코드로 변환하는 함수
def rgb_to_hex(rgb):
    return '{:02x}{:02x}{:02x}'.format(*rgb)

# Hex -> RGB 코드로 변환하는 함수
def hex_to_rgb(hex):
    r = int(hex[0:2], 16)
    g = int(hex[2:4], 16)
    b = int(hex[4:6], 16)
    return [r, g, b]


# 변환된 데이터를 bulk 요청 형식으로 생성하는 함수
def json_to_bulk_data(entries, index_name):
    bulk_data = []

    for entry in entries:
        rgb_color = hex_to_rgb(entry)
        upsert_line = {
            "index": {
                "_index": index_name,
            }
        }
        doc_line = {
            "rgb_vector": rgb_color,
            "hex": entry
        }
        bulk_data.append(json.dumps(upsert_line))
        bulk_data.append(json.dumps(doc_line))

    return "\n".join(bulk_data) + "\n"

# bulk 요청을 보내는 함수
def send_bulk_upsert_request(bulk_data):
    headers = {"Content-Type": "application/json"}
    response = requests.post(open_search_endpoint + "/_bulk", data=bulk_data, headers=headers, auth=auth)

    if response.status_code == 200:
        response_data = response.json()

        # 각 문서의 응답 확인
        for item in response_data['items']:
            item_data = list(item.values())[0]  # Extract the first (and only) item in the dictionary
            operation_result = item_data.get('result', None)
            document_id = item_data['_id']

            if operation_result == 'created' or operation_result == 'updated':
                print(f"문서 업데이트 성공: {document_id}")
            elif operation_result == 'noop':
                print(f"문서 업데이트 없음: {document_id}")
            elif 'error' in item_data:
                print(f"문서 업데이트 실패: {document_id}, 에러 메시지: {item_data['error']['reason']}")
            else:
                print(f"문서 업데이트 상태 알 수 없음: {document_id}")
    else:
        print(f"업데이트 요청 실패: {response.status_code}")

    return response

def main():
    # S3에서 JSON 파일 읽기
    response = s3.list_objects_v2(Bucket=bucket_name)

    # 파일 목록 추출
    file_list = []
    if 'Contents' in response:
        for obj in response['Contents']:
            if 'upsert/' in obj['Key'] and obj['Key'] != 'upsert/':
                file_list.append(obj['Key'])

    print('File List:', file_list)

    color_data = set()  # 중복된 데이터를 방지하기 위해 set 자료구조 사용

    for file_name in file_list:
        print('File Name:', file_name)
        response = s3.get_object(Bucket=bucket_name, Key=file_name)
        json_content = response['Body'].read().decode('utf-8')
        json_data = json.loads(json_content)

        # "rawColors"에서 RGB 데이터 추출하여 중복 없이 추가
        for item in json_data:
            if 'rawColors' in item:
                colors = item['rawColors']
                for color in colors:
                    color_data.add(color)

    color_data = list(color_data)


    # Elasticsearch에 색상 인덱스 업데이트를 위한 bulk 요청 데이터 생성
    bulk_data = json_to_bulk_data(color_data, "color-knn_v1.1.0")

    # print(len(color_data))
    # bulk 요청 전송
    send_bulk_upsert_request(bulk_data)

if __name__ == "__main__":
    main()
    print('Done!!!')
