import cv2
import numpy as np
import dlib
from datetime import datetime

# 이미지 경로 지정
sticker_path = 'kkkk.png'  # 파일 이름 영어로 저장해야 함!
img_hat = cv2.imread(sticker_path, cv2.IMREAD_UNCHANGED)

# 모델 설정
detector_hog = dlib.get_frontal_face_detector()
model_path = 'shape_predictor_68_face_landmarks.dat'
landmark_predictor = dlib.shape_predictor(model_path)

# 스티커 크기 조절 변수
scaling_factor_width = 1.0  # 기본 가로 크기
scaling_factor_height = 1.0  # 기본 세로 크기

# 원래 크기 저장
original_scaling_factor_width = scaling_factor_width
original_scaling_factor_height = scaling_factor_height

# 스티커 위치 조정 변수
sticker_offset_x = 0
sticker_offset_y = 0

# 원래 위치 저장
original_sticker_offset_x = sticker_offset_x
original_sticker_offset_y = sticker_offset_y

# 웹캠 0번으로 설정
cap = cv2.VideoCapture(0)

# 프레임이 안잡히면 종료
while True:
    ret, frame = cap.read()
    if not ret:
        break

    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img_show = frame.copy()

    # 얼굴 검출
    dlib_rects = detector_hog(img_rgb, 1)

    # 여러 명 인식 가능하게 리스트를 만들어서 반복문
    list_landmarks = []
    for dlib_rect in dlib_rects:
        points = landmark_predictor(img_rgb, dlib_rect)
        list_points = list(map(lambda p: (p.x, p.y), points.parts()))
        list_landmarks.append(list_points)

    # 얼굴마다 스티커 합성
    for dlib_rect, landmark in zip(dlib_rects, list_landmarks):
        # 코 위치 (30번 랜드마크) 기준으로 스티커 위치 계산
        x = landmark[30][0] + sticker_offset_x
        y = landmark[30][1] - dlib_rect.height() // 2 + sticker_offset_y
        w = int(dlib_rect.width() * scaling_factor_width)  # 가로 크기 조절
        h = int(dlib_rect.height() * scaling_factor_height)  # 세로 크기 조절

        # 스티커 이미지 크기 조절
        img_hat_resized = cv2.resize(img_hat, (w, h))

        refined_x = x - w // 2  # 모자 위치 조정
        refined_y = y - h

        # 경계 체크 및 조정
        if refined_x < 0:
            img_hat_resized = img_hat_resized[:, -refined_x:]
            refined_x = 0
        if refined_y < 0:
            img_hat_resized = img_hat_resized[-refined_y:, :]
            refined_y = 0

        # 스티커가 이미지 경계 밖으로 나가지 않도록 조정
        end_x = min(refined_x + img_hat_resized.shape[1], img_show.shape[1])
        end_y = min(refined_y + img_hat_resized.shape[0], img_show.shape[0])

        # 영역 조정
        img_hat_resized = img_hat_resized[:end_y-refined_y, :end_x-refined_x]
        refined_y = max(refined_y, 0)
        refined_x = max(refined_x, 0)

        # 합성할 영역 지정
        hat_area = img_show[refined_y:end_y, refined_x:end_x]

        # 알파 채널 처리하여 합성
        alpha_s = img_hat_resized[:, :, 3] / 255.0
        alpha_l = 1.0 - alpha_s

        for c in range(0, 3):
            hat_area[:, :, c] = (alpha_s * img_hat_resized[:, :, c] +
                                  alpha_l * hat_area[:, :, c])

        img_show[refined_y:end_y, refined_x:end_x] = hat_area

    # 결과 프레임 출력
    cv2.imshow('Webcam', img_show)

    # 사용자 입력을 통해 스티커 크기 조절 및 위치 조절
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    elif key == ord('a'):
        scaling_factor_width = max(0.1, scaling_factor_width - 0.1)  # 가로 크기 감소
    elif key == ord('d'):
        scaling_factor_width += 0.1  # 가로 크기 증가
    elif key == ord('w'):
        scaling_factor_height += 0.1  # 세로 크기 증가
    elif key == ord('s'):
        scaling_factor_height = max(0.1, scaling_factor_height - 0.1)  # 세로 크기 감소
    elif key == ord('g'):
        # 원래 위치로 리셋
        scaling_factor_width = original_scaling_factor_width
        scaling_factor_height = original_scaling_factor_height

    elif key == ord('m'):
        # 현재 프레임 캡처
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'captured_frame_{timestamp}.png'
        cv2.imwrite(filename, img_show)
        print(f"Frame captured as '{filename}'")

cap.release()
cv2.destroyAllWindows()
