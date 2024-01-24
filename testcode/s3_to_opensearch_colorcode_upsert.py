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
json_file_key = os.environ.get('AWS_S3_PATH')

# OpenSearch 엔드포인트 및 인증 정보 설정
open_search_endpoint = os.environ.get("AWS_OS_NODE")
opensearch_user = os.environ.get("AWS_OS_USERNAME")
opensearch_pass = os.environ.get("AWS_OS_PASSWORD")
auth = (opensearch_user, opensearch_pass)

# S3 클라이언트 생성
s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region_name)

# data 폼 생성
def json_to_bulk_data(entries):
    bulk_data = []

    for entry in entries:
        upsert_line = {
            "index": {
                "_index": 'color-knn',
                "_id": str(entry["id"]),
                "op_type": "upsert"  # Specify upsert operation
            }
        }
        doc_line = {
            "rgb_vector": [entry["r"], entry["g"], entry["b"]],  # Create RGB vector
            "hex": entry["hex"],
            "name_kr": entry["name_kr"],
            "name_en": entry["name_en"]
        }
        bulk_data.append(json.dumps(upsert_line))
        bulk_data.append(json.dumps(doc_line))

    return "\n".join(bulk_data) + "\n"

# POST _bulk 요청
def send_bulk_update_request(bulk_data):
    headers = {"Content-Type": "application/json"}
    response = requests.post(open_search_endpoint + "/_bulk", data=bulk_data, headers=headers, auth=auth)
    print(response)
    if response.status_code == 200:
        response_data = response.json()
        # 각 문서의 응답 확인
        for item in response_data['items']:
            item_data = item['upsert']
            if item_data['_shards']['failed'] > 0:
                print(f"문서 업데이트 실패: {item_data['_id']}")
            else:
                print(f"문서 업데이트 성공: {item_data['_id']}")
    else:
        print(f"업데이트 요청 실패: {response.status_code}")

    return response

def send_bulk_upsert_request(bulk_data):
    headers = {"Content-Type": "application/json"}
    response = requests.post(open_search_endpoint + "/_bulk", data=bulk_data, headers=headers, auth=auth)
    print(response)

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

# JSON을 Bulk API 데이터로 변환하여 OpenSearch에 삽입 또는 업데이트하는 메인 함수
def main():

    # S3에서 JSON 파일 읽기
    response = s3.list_objects_v2(Bucket=bucket_name)

    # 파일 목록 추출
    file_list = []
    if 'Contents' in response:
        for obj in response['Contents']:
            if 'color/' in obj['Key'] and obj['Key'] != 'color/':
                file_list.append(obj['Key'])

    print('File List:', file_list)

    for j in file_list :
        target_file_name = j
        print('File Name:', target_file_name)
        response = s3.get_object(Bucket=bucket_name, Key=target_file_name)
        json_content = response['Body'].read().decode('utf-8')
        json_data = json.loads(json_content)

        print(json_data)


        # bulk data 형식으로 변환
        bulk_data = json_to_bulk_data(json_data)
        print(bulk_data)
        response = send_bulk_upsert_request(bulk_data)
        print(response.text)


if __name__ == "__main__":
    main()
