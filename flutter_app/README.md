# LeagueSLG Flutter App

LeagueSLG 게임의 Flutter 프론트엔드 애플리케이션입니다.

## 🎮 Features

- **실시간 맵 시각화**: 20x20 그리드 맵을 실시간으로 표시
- **타일 색상 구분**: 자원 타입별로 다른 색상으로 표시
  - 🟢 식량 (FOOD) - 녹색
  - 🟤 목재 (WOOD) - 갈색
  - ⚫ 철광 (IRON) - 회색
  - 🔵 석재 (STONE) - 파란색
  - ⛰️ 장애물 (OBSTACLE) - 진한 회색
- **인터랙티브 맵**: 확대/축소 및 드래그 가능
- **타일 선택**: 타일 클릭 시 상세 정보 표시
- **실시간 업데이트**: 1초마다 게임 상태 자동 갱신

## 📋 Prerequisites

- Flutter SDK 3.38.9 이상
- Dart 3.10.8 이상
- 백엔드 서버가 `http://localhost:8000`에서 실행 중이어야 함

## 🚀 Getting Started

### 1. 의존성 설치

```bash
cd flutter_app
flutter pub get
```

### 2. 백엔드 서버 실행

먼저 백엔드 서버를 실행해야 합니다:

```bash
# 프로젝트 루트 디렉토리에서
cd ..
py src/api/server.py
```

서버가 `http://localhost:8000`에서 실행되는지 확인하세요.

### 3. Flutter 앱 실행

#### Chrome (웹)에서 실행:
```bash
flutter run -d chrome
```

#### Windows 데스크톱에서 실행:
```bash
flutter run -d windows
```

#### 모바일 에뮬레이터에서 실행:
```bash
flutter emulators  # 사용 가능한 에뮬레이터 확인
flutter emulators --launch <emulator_id>  # 에뮬레이터 실행
flutter run  # 앱 실행
```

## 🎯 Usage

### 맵 탐색
- **확대/축소**: 마우스 휠 또는 핀치 제스처
- **이동**: 드래그

### 타일 선택
- 타일을 클릭하면 오른쪽 사이드바에 상세 정보가 표시됩니다
- 좌표, 카테고리, 레벨, 소유주 정보 확인 가능

### 맵 새로고침
- 상단 우측의 새로고침 버튼 클릭

## 📁 Project Structure

```
flutter_app/
├── lib/
│   └── main.dart          # 메인 애플리케이션 코드
├── pubspec.yaml           # 의존성 설정
└── README.md             # 이 파일
```

## 🔧 Configuration

### API 엔드포인트 변경

`lib/main.dart`의 `apiBaseUrl` 상수를 수정하세요:

```dart
static const String apiBaseUrl = 'http://your-server-url:port';
```

### 업데이트 주기 변경

게임 상태 업데이트 주기를 변경하려면 `_MapScreenState.initState()`의 Timer 설정을 수정하세요:

```dart
updateTimer = Timer.periodic(const Duration(seconds: 2), (timer) {
  updateGameState();
});
```

## 🎨 Customization

### 타일 색상 변경

`TileWidget.getTileColor()` 메서드에서 자원 타입별 색상을 변경할 수 있습니다:

```dart
Color getTileColor() {
  if (tile.category == 'OBSTACLE') {
    return Colors.grey[700]!;
  } else if (tile.category == 'RESOURCE') {
    switch (tile.resourceType) {
      case 'FOOD':
        return Colors.green[400]!;  // 여기를 수정
      // ...
    }
  }
  // ...
}
```

### 타일 크기 변경

`MapGrid.build()` 메서드의 `tileSize` 상수를 변경하세요:

```dart
const double tileSize = 50.0;  // 기본값: 40.0
```

## 🐛 Troubleshooting

### "Failed to load map" 에러
- 백엔드 서버가 실행 중인지 확인하세요
- `http://localhost:8000/map`에 브라우저로 접속하여 API가 응답하는지 확인하세요

### CORS 에러 (웹에서 실행 시)
- 백엔드 서버의 CORS 설정이 올바른지 확인하세요
- `src/api/server.py`에서 CORS 미들웨어가 활성화되어 있어야 합니다

### 타일이 표시되지 않음
- 브라우저 개발자 도구(F12)의 콘솔에서 에러 메시지 확인
- 네트워크 탭에서 API 요청이 성공했는지 확인

## 🚧 Upcoming Features

- [ ] 행군 명령 기능
- [ ] 건물 배치 기능
- [ ] 유저 자원 표시
- [ ] 전투 애니메이션
- [ ] 3D 모델 렌더링 (Blender 통합)

## 📝 Notes

- 현재는 프로토타입 버전으로 20x20 맵을 사용합니다
- 향후 Blender로 제작한 3D 모델과 더 큰 맵으로 확장 예정
- 실시간 업데이트는 현재 전체 맵을 다시 로드하는 방식이며, 향후 델타 업데이트로 최적화 예정

## 📚 API Documentation

백엔드 API에 대한 자세한 정보는 프로젝트 루트의 `API_DOCUMENTATION.md`를 참조하세요.
