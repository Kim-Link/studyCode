import cv2
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# 이미지 파일 경로
image_paths = []

def preprocess_image(image_path):
    # 이미지를 읽고 크기를 조정합니다.
    img = cv2.imread(image_path)
    img = cv2.resize(img, (100, 100))  # 이미지 크기를 조정하거나 다른 전처리를 수행할 수 있습니다.
    # 이미지를 1차원 벡터로 변환합니다.
    return img.flatten()

# 모든 이미지를 전처리하여 배열에 저장합니다.
preprocessed_images = []
for path in image_paths:
    preprocessed_images.append(preprocess_image(path))

# 입력 이미지를 전처리합니다.
input_image = preprocess_image("https://shoes-image-bucket.s3.ap-northeast-2.amazonaws.com/luxury/dior/shoes_20231212115100211503.jpg")

# 전처리된 이미지들을 NumPy 배열로 변환합니다.
preprocessed_images = np.array(preprocessed_images)
input_image = np.array([input_image])

# 코사인 유사도를 계산합니다.
similarities = cosine_similarity(input_image, preprocessed_images)

# 유사도가 높은 상위 3개 이미지의 인덱스를 찾습니다.
top_indices = similarities.argsort()[0][-3:][::-1]

# 상위 3개 이미지의 경로를 출력합니다.
print("가장 유사한 이미지 3장:")
for idx in top_indices:
    print(image_paths[idx])
