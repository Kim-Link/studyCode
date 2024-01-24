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

# S3 클라이언트 생성
s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region_name)


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

    print(file_list)
    if file_list and len(file_list) > 2:
        first_file = file_list[0]
        s3.delete_object(Bucket=bucket_name, Key=first_file)
        print(f'Deleted file: {first_file}')
    else:
        print('No files found in the bucket.')

    return {
        'statusCode': 200,
        'body': 'File deletion complete.'
    }


if __name__ == "__main__":
    main()
