# Voice Note debug exports

이 폴더는 녹음 파일과 전사 파일을 워크스페이스에서 바로 보기 위한 미러 공간입니다.

## 사용 방법
1. 휴대폰/서버에서 원본 파일을 로컬에 먼저 가져옵니다.
2. 아래 스크립트로 이 폴더에 복사합니다.

```bash
python /workspace/AI_Voice_Note/scripts/mirror_debug_artifacts.py \
  --source /path/to/pulled_artifacts \
  --dest /workspace/AI_Voice_Note/debug_exports
```

## 생성 파일
- `INDEX.md`: 미러된 파일 목록과 요약 정보

## 보관 정책
- 운영용 원본 보관이 아니라 개발/검토용입니다.
- 실제 파일은 Git에 올리지 않고, 워크스페이스 로컬에서만 보입니다.
