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

def convert_to_hex(color):
    # Convert RGB color to hex
    return '{:02x}{:02x}{:02x}'.format(*color)

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

    for file_name in file_list:
        print('File Name:', file_name)
        response = s3.get_object(Bucket=bucket_name, Key=file_name)
        json_content = response['Body'].read().decode('utf-8')
        json_data = json.loads(json_content)


        # Convert rawColors to hex and store in hexColors, then remove rawColors
        for item in json_data:
            if 'rawColors' in item:
                hex_colors = [convert_to_hex(color) for color in item['rawColors']]
                item['rawColors'] = hex_colors
            else:
                item['rawColors'] = []

        # Save processed data
        file_name_safe = re.sub(r'[^\w\s]', '', file_name)  # 특수 문자 제거
        processed_file_name = f"processed_{file_name_safe}.json"
        with open(processed_file_name, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        # Upload processed data to target bucket
        with open(processed_file_name, 'rb') as f:
            s3.upload_fileobj(f, bucket_name, f"upsert/color_{processed_file_name}")

        # Remove local processed file
        os.remove(processed_file_name)

if __name__ == "__main__":
    main()
