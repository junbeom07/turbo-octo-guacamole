import cv2
import numpy as np
import dlib
from datetime import datetime

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.sticker_path = 'static/kkkk.png'
        self.img_hat = cv2.imread(self.sticker_path, cv2.IMREAD_UNCHANGED)
        self.detector_hog = dlib.get_frontal_face_detector()
        self.model_path = 'shape_predictor_68_face_landmarks.dat'
        self.landmark_predictor = dlib.shape_predictor(self.model_path)
        self.scaling_factor_width = 1.0
        self.scaling_factor_height = 1.0
        self.sticker_offset_x = 0
        self.sticker_offset_y = 0
        self.original_scaling_factor_width = 1.0
        self.original_scaling_factor_height = 1.0
        self.original_sticker_offset_x = 0
        self.original_sticker_offset_y = 0

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, frame = self.video.read()
        if not success:
            return None

        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_show = frame.copy()

        dlib_rects = self.detector_hog(img_rgb, 1)

        list_landmarks = []
        for dlib_rect in dlib_rects:
            points = self.landmark_predictor(img_rgb, dlib_rect)
            list_points = list(map(lambda p: (p.x, p.y), points.parts()))
            list_landmarks.append(list_points)

        for dlib_rect, landmark in zip(dlib_rects, list_landmarks):
            x = landmark[30][0] + self.sticker_offset_x
            y = landmark[30][1] - dlib_rect.height() // 2 + self.sticker_offset_y
            w = int(dlib_rect.width() * self.scaling_factor_width)
            h = int(dlib_rect.height() * self.scaling_factor_height)

            img_hat_resized = cv2.resize(self.img_hat, (w, h))

            refined_x = x - w // 2
            refined_y = y - h

            if refined_x < 0:
                img_hat_resized = img_hat_resized[:, -refined_x:]
                refined_x = 0
            if refined_y < 0:
                img_hat_resized = img_hat_resized[-refined_y:, :]
                refined_y = 0

            end_x = min(refined_x + img_hat_resized.shape[1], img_show.shape[1])
            end_y = min(refined_y + img_hat_resized.shape[0], img_show.shape[0])

            img_hat_resized = img_hat_resized[:end_y-refined_y, :end_x-refined_x]
            refined_y = max(refined_y, 0)
            refined_x = max(refined_x, 0)

            hat_area = img_show[refined_y:end_y, refined_x:end_x]

            alpha_s = img_hat_resized[:, :, 3] / 255.0
            alpha_l = 1.0 - alpha_s

            for c in range(0, 3):
                hat_area[:, :, c] = (alpha_s * img_hat_resized[:, :, c] +
                                      alpha_l * hat_area[:, :, c])

            img_show[refined_y:end_y, refined_x:end_x] = hat_area

        ret, jpeg = cv2.imencode('.jpg', img_show)
        return jpeg.tobytes()

    def reset_sticker(self):
        self.scaling_factor_width = self.original_scaling_factor_width
        self.scaling_factor_height = self.original_scaling_factor_height
        self.sticker_offset_x = self.original_sticker_offset_x
        self.sticker_offset_y = self.original_sticker_offset_y

    def set_sticker(self, sticker_path):
        self.sticker_path = sticker_path
        self.img_hat = cv2.imread(self.sticker_path, cv2.IMREAD_UNCHANGED)
        # 스티커 변경 시 크기와 위치를 초기화합니다
        self.scaling_factor_width = 1.0
        self.scaling_factor_height = 1.0
        self.sticker_offset_x = 0
        self.sticker_offset_y = 0