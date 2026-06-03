# AI Voice Note

안드로이드 음성 노트 앱입니다.

## 현재 구조
- **모바일 앱**: VAD 기반 자동 녹음, WAV 세그먼트 생성, n8n 업로드
- **서버**: n8n이 업로드된 음성을 Whisper/Ollama로 분석
- **결과 전달**: 분석 결과를 Telegram 등으로 다시 전송

## 동작 흐름
1. 앱에서 **시작**을 누르면 마이크를 감시합니다.
2. 음성이 감지되면 짧은 WAV 세그먼트를 만듭니다.
3. 세그먼트를 `serverUrl + uploadPath` 로 multipart 업로드합니다.
4. n8n이 업로드된 음성을 받아 전사/요약/액션 아이템을 처리합니다.
5. 서버 결과는 Telegram 또는 후속 워크플로우로 전달됩니다.

## 기본 설정
- 서버 URL: 외부 VPS 주소
- 업로드 경로: `/webhook/voice-note/upload`
- 세션 이름: 선택 입력

## 제거된 항목
- 로컬 Vosk STT
- 텍스트 업로드 큐
- Gemini 모바일 전사
- Python 서버/스크립트 번들
- FFmpeg 대용량 배포 파일

## 빌드
Debug APK는 Android Gradle로 빌드합니다.

```bash
gradle assembleDebug
```

## 참고
이 저장소는 앱 코드와 최소한의 운영 문서만 유지합니다.
