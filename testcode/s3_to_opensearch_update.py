import boto3
import json
import requests
from dotenv import load_dotenv
import os
import re


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
def json_to_bulk_data(entries, index_name):
    bulk_data = []

    for entry in entries:
        update_line = {
            "update": {
                "_index": index_name,  # OpenSearch index 이름
                "_id": entry["uuid"]
            }

        }
        doc_line = {"doc": entry}
        bulk_data.append(json.dumps(update_line))
        bulk_data.append(json.dumps(doc_line))

    return "\n".join(bulk_data) + "\n"

# 인덱스 결정
def extract_index_name(filename):
    # 정규표현식을 사용하여 'luxury_clothes_brand', 'luxury_shoes_brand', 'shoes_brand'를 추출
    match = re.search(r'_(luxury_clothes|luxury_shoes|shoes)_brand(_[a-zA-Z0-9._ ]+)?\.json', filename)

    # 매치가 존재하면 인덱스를 반환, 아니면 에러를 반환
    if match:
        return match.group(1) + '_brand'
    else:
        raise ValueError(f"{filename}에서 인덱스를 찾을 수 없습니다.")

# POST _bulk 요청
def send_bulk_update_request(bulk_data):
    headers = {"Content-Type": "application/json"}
    response = requests.post(open_search_endpoint + "/_bulk", data=bulk_data, headers=headers, auth=auth)
    print(response)
    if response.status_code == 200:
        response_data = response.json()
        # 각 문서의 응답 확인
        for item in response_data['items']:
            item_data = item['update']
            if item_data['_shards']['failed'] > 0:
                print(f"문서 업데이트 실패: {item_data['_id']}")
            else:
                print(f"문서 업데이트 성공: {item_data['_id']}")
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
            if 'update/' in obj['Key'] and obj['Key'] != 'update/':
                file_list.append(obj['Key'])

    # 파일&인덱스 선택
    target_file_index = 0
    target_file_name = file_list[target_file_index]
    index_name = extract_index_name(file_list[target_file_index])

    # print('Index Name:', os.environ.get("AWS_OS_INDEX"))
    print('File List:', file_list)
    print('Last Index of File List :', len(file_list) - 1)
    print('Target File Index:', target_file_index)
    print('File Name:', target_file_name)
    print('Bucket Name:', bucket_name)
    print('Index Name:', index_name)

    response = s3.get_object(Bucket=bucket_name, Key=target_file_name)
    json_content = response['Body'].read().decode('utf-8')
    json_data = json.loads(json_content)

    # 배치 크기로 조정
    batch_size = 1000
    for i in range(0, len(json_data), batch_size):
        batch_entries = json_data[i:i + batch_size]

        # bulk data 형식으로 변환
        bulk_data = json_to_bulk_data(batch_entries, index_name)
        response = send_bulk_update_request(bulk_data)
        print(f"Bulk insert response for batch {i}:")
        print(response.text)


if __name__ == "__main__":
    main()
