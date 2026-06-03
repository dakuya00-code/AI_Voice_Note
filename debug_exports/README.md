# Voice Note debug exports

이 폴더는 녹음 파일과 전사 파일을 워크스페이스에서 바로 보기 위한 미러 공간입니다.

## 사용 방법

### 1) 휴대폰에서 가져오기
앱에서 **디버그 내보내기**를 실행하면 기기 내부 외부저장소에 파일이 쌓입니다.
그다음 아래 스크립트로 워크스페이스로 가져옵니다.

```bash
python /workspace/AI_Voice_Note/scripts/pull_debug_artifacts_adb.py \
  --package com.hermes.aivoiceassistant \
  --dest /workspace/AI_Voice_Note/debug_exports \
  --clear
```

### 2) 서버에서 가져오기
서버 아티팩트 루트가 있으면 아래처럼 복사합니다.

```bash
python /workspace/AI_Voice_Note/scripts/sync_server_debug_artifacts.py \
  --source /path/to/server_data \
  --dest /workspace/AI_Voice_Note/debug_exports \
  --clear
```

### 3) 일반 미러
이미 로컬에 있는 아티팩트도 다음 스크립트로 통합할 수 있습니다.

```bash
python /workspace/AI_Voice_Note/scripts/mirror_debug_artifacts.py \
  --source /path/to/pulled_artifacts \
  --dest /workspace/AI_Voice_Note/debug_exports
```

## 생성 파일
- `INDEX.md`: 미러된 파일 목록과 요약 정보

## 복사 대상
- `*.wav`
- `*.m4a`
- `*.json`
- `*.txt`
- `*.log`

## 보관 정책
- 운영용 저장이 아니라 개발/검토용입니다.
- 실제 파일은 Git에 올리지 않고, 워크스페이스 로컬에서만 보입니다.
