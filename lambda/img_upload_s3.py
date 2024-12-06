import json
import base64
import boto3
import uuid
from botocore.exceptions import BotoCoreError, ClientError
import os


# S3 설정
BUCKET_NAME = os.environ.get("AWS_S3_BUCKET_NAME")  # S3 버킷 이름
REGION_NAME = os.environ.get("AWS_REGION")  # S3 리전 이름

s3_client = boto3.client("s3", region_name=REGION_NAME)


def lambda_handler(event, context):
    try:
        # 이벤트에서 이미지 가져오기
        body = json.loads(event.get("body", "{}"))
        image_data = body.get("image_data")
        if not image_data:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "No image data provided"}),
            }

        # 이미지 데이터 디코딩
        image_bytes = base64.b64decode(image_data)

        # S3에 업로드할 파일명 생성
        file_name = f"{uuid.uuid4()}.jpg"  # 이미지 파일 확장자는 상황에 맞게 조정 가능

        # S3에 업로드
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=file_name,
            Body=image_bytes,
            ContentType="image/jpeg",
        )

        # 업로드된 파일 URL 생성
        file_url = f"https://{BUCKET_NAME}.s3.{REGION_NAME}.amazonaws.com/{file_name}"

        return {"statusCode": 200, "body": json.dumps({"url": file_url})}

    except (BotoCoreError, ClientError) as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Failed to upload image", "error": str(e)}),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps(
                {"message": "An unexpected error occurred", "error": str(e)}
            ),
        }
