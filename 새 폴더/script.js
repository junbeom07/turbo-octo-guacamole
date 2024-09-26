document.addEventListener('DOMContentLoaded', async () => {
    const video = document.getElementById('webcam');
    const canvas = document.getElementById('output-canvas');
    const ctx = canvas.getContext('2d');
    const stickerUpload = document.getElementById('sticker-upload');
    const applySticker = document.getElementById('apply-sticker');
    const resetSticker = document.getElementById('reset-sticker');
    const captureFrame = document.getElementById('capture-frame');

    // 모달 관련 요소
    const usageBtn = document.getElementById('usage-btn');
    const contactBtn = document.getElementById('contact-btn');
    const usageModal = document.getElementById('usage-modal');
    const contactModal = document.getElementById('contact-modal');
    const closeBtns = document.getElementsByClassName('close');

    // 스티커 위치 및 크기 조절 변수
    let stickerX = 0;
    let stickerY = 0;
    let stickerScale = 1;
    let stickerImg = null;

    // 웹캠 시작
    async function startWebcam() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = stream;

            // 비디오가 로드된 후 캔버스 크기를 비디오 크기와 맞춤
            video.addEventListener('loadeddata', () => {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
            });
        } catch (err) {
            console.error('웹캠 접근 오류:', err);
        }
    }

    startWebcam();

    // face-api.js 모델 로드
    await faceapi.nets.tinyFaceDetector.loadFromUri('/models');
    await faceapi.nets.faceLandmark68Net.loadFromUri('/models');

    // 스티커 적용 (얼굴 랜드마크 사용)
    applySticker.addEventListener('click', async () => {
        const file = stickerUpload.files[0];
        if (file) {
            // 파일 형식 확인
            const validImageTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp'];
            if (!validImageTypes.includes(file.type)) {
                alert('지원되지 않는 파일 형식입니다. JPEG, PNG, GIF, BMP, WebP 형식의 이미지를 업로드해주세요.');
                return;
            }

            stickerImg = new Image();
            stickerImg.onload = async () => {
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

                // 얼굴 인식 및 랜드마크 추출
                const detections = await faceapi.detectAllFaces(video, new faceapi.TinyFaceDetectorOptions()).withFaceLandmarks();
                if (detections.length > 0) {
                    const landmarks = detections[0].landmarks;
                    const forehead = landmarks.getNose()[0]; // 코의 첫 번째 점을 이마 위치로 사용

                    // 스티커 위치 초기화
                    stickerX = forehead.x - 50; // 스티커 너비의 절반
                    stickerY = forehead.y - 70; // 이마 위에 스티커를 배치하기 위해 약간 위로 이동
                    stickerScale = 1;

                    drawSticker();
                } else {
                    alert('얼굴을 인식하지 못했습니다.');
                }
            };
            stickerImg.onerror = () => {
                alert('스티커 이미지를 로드하는 중 오류가 발생했습니다.');
            };
            stickerImg.src = URL.createObjectURL(file);
        } else {
            alert('스티커 파일을 선택해주세요.');
        }
    });

    // 스티커 그리기 함수
    function drawSticker() {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        if (stickerImg) {
            const stickerWidth = 100 * stickerScale;
            const stickerHeight = 50 * stickerScale;
            ctx.drawImage(stickerImg, stickerX, stickerY, stickerWidth, stickerHeight);
        }
    }

    // 스티커 위치 및 크기 조절 이벤트
    document.addEventListener('keydown', (e) => {
        switch (e.key) {
            case 'ArrowUp':
                stickerY -= 5;
                break;
            case 'ArrowDown':
                stickerY += 5;
                break;
            case 'ArrowLeft':
                stickerX -= 5;
                break;
            case 'ArrowRight':
                stickerX += 5;
                break;
            case '+':
                stickerScale += 0.1;
                break;
            case '-':
                stickerScale -= 0.1;
                break;
        }
        drawSticker();
    });

    // 스티커 리셋
    resetSticker.addEventListener('click', () => {
        stickerX = 0;
        stickerY = 0;
        stickerScale = 1;
        drawSticker();
    });

    // 프레임 캡처 기능 추가
    captureFrame.addEventListener('click', () => {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const dataURL = canvas.toDataURL('image/png');
        const link = document.createElement('a');
        link.href = dataURL;
        link.download = 'captured_frame.png';
        link.click();
    });

    // 모달 열기
    usageBtn.onclick = () => usageModal.style.display = "block";
    contactBtn.onclick = () => contactModal.style.display = "block";

    // 모달 닫기
    document.querySelectorAll('.close').forEach(btn => {
        btn.onclick = function() {
            usageModal.style.display = "none";
            contactModal.style.display = "none";
        }
    });

    // 모달 외부 클릭 시 닫기
    window.onclick = (event) => {
        if (event.target == usageModal) {
            usageModal.style.display = "none";
        }
        if (event.target == contactModal) {
            contactModal.style.display = "none";
        }
    }

    // 연락처 폼 제출
    const contactForm = document.getElementById('contact-form');
    contactForm.addEventListener('submit', (e) => {
        e.preventDefault();
        alert('메시지가 전송되었습니다!'); // 실제로는 서버로 데이터를 보내야 합니다
        contactModal.style.display = "none";
    });
});