# 🎮 LeagueSLG - Strategy Game

리그 오브 레전드 챔피언들이 등장하는 전략 시뮬레이션 게임입니다.

## 📖 Project Overview

LeagueSLG는 Python 백엔드(FastAPI)와 Flutter 프론트엔드로 구성된 실시간 전략 게임입니다. 플레이어는 맵 위에서 영토를 확장하고, 챔피언을 육성하며, 다른 플레이어와 전투를 벌입니다.

## 🏗️ Architecture

```
LeagueSLG/
├── src/                    # Python 백엔드
│   ├── api/               # FastAPI 서버
│   ├── models/            # 데이터 모델 (Champion, Tile, Army 등)
│   ├── logic/             # 게임 로직 (Battle, MapManager)
│   ├── factories/         # 객체 생성 팩토리
│   └── common/            # 공통 유틸리티
├── flutter_app/           # Flutter 프론트엔드
│   └── lib/
│       └── main.dart      # 메인 앱
├── data/                  # 게임 데이터 (JSON)
├── db/                    # SQLite 데이터베이스
├── reports/               # 전투 리포트 (HTML)
└── static/                # 정적 파일
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **Flutter 3.38.9+**
- **Dart 3.10.8+**

### 1. 백엔드 설정 및 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# 또는 (Windows)
py -m pip install -r requirements.txt

# 서버 실행
py src/api/server.py
```

서버가 `http://localhost:8000`에서 실행됩니다.

### 2. Flutter 앱 실행

```bash
# Flutter 앱 디렉토리로 이동
cd flutter_app

# 의존성 설치
flutter pub get

# 앱 실행 (Chrome)
flutter run -d chrome

# 또는 Windows 데스크톱
flutter run -d windows
```

## 🎯 Features

### ✅ 현재 구현된 기능

- **맵 시스템**
  - 20x20 그리드 기반 월드 맵
  - 자원 타일 (식량, 목재, 철광, 석재)
  - 장애물 타일
  - 건물 배치 (주성, 막사)

- **전투 시스템**
  - 턴제 전투 (속도 기반 턴 순서)
  - 스킬 시스템
  - 버프/디버프 효과
  - HTML 전투 리포트 생성

- **행군 시스템**
  - 부대 이동
  - 자동 전투 발생
  - 승리 시 점령, 패배 시 후퇴

- **데이터베이스**
  - 유저 정보 저장
  - 챔피언 보유 및 레벨 관리
  - 전투 로그 기록

- **REST API**
  - 맵 데이터 조회
  - 유저 상태 관리
  - 행군 명령
  - 건물 배치
  - 실시간 게임 상태 업데이트

- **Flutter 앱**
  - 실시간 맵 시각화
  - 인터랙티브 타일 선택
  - 자동 게임 상태 갱신

### 🚧 개발 예정 기능

- [ ] 자원 생산 및 채집
- [ ] 챔피언 회복 시스템
- [ ] 건물 업그레이드
- [ ] 멀티 부대 운용
- [ ] 3D 모델 통합 (Blender)
- [ ] 대규모 맵 지원 (100x100+)
- [ ] 실시간 멀티플레이어

## 📚 Documentation

- **[API Documentation](API_DOCUMENTATION.md)** - 백엔드 API 상세 가이드
- **[Flutter App README](flutter_app/README.md)** - Flutter 앱 사용법
- **[FORGEO.md](FORGEO.md)** - 프로젝트 아키텍처 및 엔지니어링 철학

## 🎮 Game Mechanics

### 맵 시스템
- 각 타일은 레벨(1-8)을 가지며, 레벨이 높을수록 강한 수비군이 배치됩니다
- 자원 타일을 점령하면 해당 자원을 생산할 수 있습니다
- 장애물 타일은 통과할 수 없습니다

### 전투 시스템
- 챔피언의 HP가 곧 병력 수입니다
- 속도(SPD) 스탯이 높은 챔피언이 먼저 행동합니다
- 스킬은 확률적으로 발동되며, 강력한 효과를 발휘합니다
- 전투 승리 시 경험치를 획득합니다

### 행군 시스템
- 부대를 목표 타일로 파견하면 일정 시간 후 도착합니다
- 도착 시 해당 타일의 수비군과 자동으로 전투가 발생합니다
- 승리하면 타일을 점령하고, 패배하면 본진으로 후퇴합니다

## 🛠️ Development

### 백엔드 개발

```bash
# 전투 시뮬레이션 테스트
py main.py

# 맵 점령 데모
py map_demo.py

# 데이터베이스 초기화
py src/init_db.py
```

### API 테스트

```bash
# 맵 데이터 조회
curl http://localhost:8000/map

# 유저 상태 조회
curl http://localhost:8000/user/Player1

# 챔피언 목록 조회
curl http://localhost:8000/champions
```

### Flutter 개발

```bash
cd flutter_app

# Hot Reload (앱 실행 중)
r

# Hot Restart
R

# 종료
q
```

## 🗂️ Database Schema

### Users
- `id`: 유저 고유 ID
- `username`: 유저 이름

### UserChampions
- `id`: 챔피언 고유 ID
- `user_id`: 소유 유저 ID
- `champion_key`: 챔피언 종류
- `level`: 레벨
- `exp`: 경험치

### BattleLogs
- `id`: 로그 ID
- `user_id`: 유저 ID
- `left_champion`: 좌측 챔피언
- `right_champion`: 우측 챔피언
- `winner`: 승자
- `turn_count`: 턴 수
- `history_json`: 전투 상세 기록 (JSON)
- `created_at`: 생성 시간

## 🔧 Configuration

### 백엔드 설정

`src/api/server.py`에서 맵 크기 변경:

```python
world_map = WorldMap(width=20, height=20)  # 원하는 크기로 변경
```

### Flutter 설정

`flutter_app/lib/main.dart`에서 API URL 변경:

```dart
static const String apiBaseUrl = 'http://your-server:port';
```

## 🐛 Troubleshooting

### 백엔드 서버가 시작되지 않음
- Python 버전 확인: `py --version`
- 의존성 재설치: `py -m pip install -r requirements.txt --force-reinstall`

### Flutter 앱이 맵을 로드하지 못함
- 백엔드 서버가 실행 중인지 확인
- 브라우저에서 `http://localhost:8000/map` 접속하여 API 응답 확인
- CORS 설정 확인

### 데이터베이스 에러
- `db/game_data.db` 파일 삭제 후 재시작
- `py src/init_db.py` 실행하여 테이블 재생성

## 📝 Tech Stack

### Backend
- **Python 3.10+**
- **FastAPI** - REST API 프레임워크
- **SQLAlchemy** - ORM
- **SQLite** - 데이터베이스
- **Uvicorn** - ASGI 서버

### Frontend
- **Flutter 3.38.9+**
- **Dart 3.10.8+**
- **http** - HTTP 클라이언트

### Data Format
- **JSON** - 게임 데이터 (챔피언, 스킬, 버프)

## 🎨 Future Enhancements

### Phase 1: 기본 게임플레이 완성
- 자원 생산 시스템
- 건물 업그레이드
- 챔피언 회복

### Phase 2: 3D 그래픽
- Blender 3D 모델 통합
- 타일별 3D 에셋
- 건물 3D 모델

### Phase 3: 대규모 맵
- 100x100 이상 맵 지원
- 뷰포트 기반 로딩
- 델타 업데이트 최적화

### Phase 4: 멀티플레이어
- 실시간 동기화
- PvP 전투
- 길드 시스템

## 👥 Contributing

이 프로젝트는 개인 프로젝트입니다. 버그 리포트나 제안은 환영합니다!

## 📄 License

이 프로젝트는 교육 및 개인 사용 목적으로 제작되었습니다.

---

**Enjoy the game! ⚔️**
