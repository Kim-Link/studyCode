import json
import base64
import boto3
from botocore.exceptions import BotoCoreError, ClientError
import os
from dotenv import load_dotenv
import magic
import mimetypes

load_dotenv()

# S3 설정
BUCKET_NAME = os.environ.get("AWS_S3_BUCKET_NAME")  # S3 버킷 이름
REGION_NAME = os.environ.get("AWS_REGION")  # S3 리전 이름

s3_client = boto3.client("s3", region_name=REGION_NAME)


def upload_image_to_s3(event):
    try:
        # 이벤트에서 이미지 데이터 리스트와 파일명 가져오기
        body = json.loads(event.get("body", "{}"))
        images_data = body.get("images_data", [])
        file_names = body.get("file_names", [])  # 파일명 리스트 추가
        print("file_names >>>>>> ", file_names)
        if not images_data:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "No images data provided"}),
            }

        uploaded_urls = []

        # 각 이미지 처리
        for image_data, file_name in zip(images_data, file_names):
            # 이미지 데이터 디코딩
            image_bytes = base64.b64decode(image_data)

            # MIME 타입 감지
            mime_type = magic.from_buffer(image_bytes, mime=True)

            # 폴더 경로 추가
            folder_path = "test/"

            # S3에 업로드할 파일명 생성 (UUID + 원본 파일명)
            s3_file_name = f"{folder_path}{file_name}"

            # S3에 업로드
            s3_client.put_object(
                Bucket=BUCKET_NAME,
                Key=s3_file_name,
                Body=image_bytes,
                ContentType=mime_type,
            )

            file_url = (
                f"https://{BUCKET_NAME}.s3.{REGION_NAME}.amazonaws.com/{s3_file_name}"
            )
            uploaded_urls.append(file_url)

        return {"statusCode": 200, "body": json.dumps({"urls": uploaded_urls})}

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Failed to upload images", "error": str(e)}),
        }


def lambda_handler(event, context):
    try:
        result = upload_image_to_s3(event)
        print(result)

        return result

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


if __name__ == "__main__":
    # 테스트할 이미지 파일들의 리스트
    test_images = ["test_img_1.jpeg", "test_img_2.jpeg", "test_img_3.jpeg"]

    try:
        print("이미지 업로드 시작...")

        # 모든 이미지를 base64로 인코딩
        encoded_images = []
        for image_file_name in test_images:
            try:
                with open(image_file_name, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
                    encoded_images.append(encoded_string)
            except FileNotFoundError:
                print(f"에러: {image_file_name} 파일을 찾을 수 없습니다.")
                continue

        # 한 번에 모든 이미지 전송
        test_event = {
            "body": json.dumps(
                {"images_data": encoded_images, "file_names": test_images}
            )
        }

        # 함수 실행
        result = lambda_handler(test_event, {})
        print("업로드 결과:", result)

        if result["statusCode"] == 200:
            urls = json.loads(result["body"])["urls"]
            print("\n업로드된 이미지 URL들:")
            for i, url in enumerate(urls, 1):
                print(f"{i}. {url}")

    except Exception as e:
        print(f"에러: 업로드 중 오류 발생 - {str(e)}")
