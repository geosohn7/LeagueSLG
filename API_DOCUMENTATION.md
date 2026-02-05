# LeagueSLG Backend API Documentation

## Base URL
```
http://localhost:8000
```

## Overview
이 API는 LeagueSLG 게임의 백엔드 서버로, Flutter 앱에서 맵 데이터, 유저 정보, 행군 명령 등을 처리합니다.

---

## 📍 Map Endpoints

### 1. GET `/map`
전체 맵 데이터를 조회합니다.

**Response:**
```json
{
  "width": 20,
  "height": 20,
  "tiles": [
    {
      "x": 0,
      "y": 0,
      "category": "RESOURCE",
      "level": 3,
      "owner_id": null,
      "resource_type": "FOOD"
    },
    {
      "x": 1,
      "y": 0,
      "category": "OBSTACLE",
      "level": 1,
      "owner_id": null
    }
  ]
}
```

**Tile Fields:**
- `x`, `y`: 타일의 좌표
- `category`: 타일 종류 (`RESOURCE`, `BUILDING`, `OBSTACLE`)
- `level`: 타일 레벨 (1-8)
- `owner_id`: 점령한 유저 ID (null이면 중립)
- `resource_type`: 자원 타입 (`FOOD`, `WOOD`, `IRON`, `STONE`) - RESOURCE 타일만 해당
- `building`: 건물 정보 (있는 경우)
- `army`: 주둔 중인 부대 정보 (있는 경우)

---

### 2. GET `/map/tile/{x}/{y}`
특정 타일의 상세 정보를 조회합니다.

**Parameters:**
- `x`: X 좌표
- `y`: Y 좌표

**Response:**
```json
{
  "x": 5,
  "y": 5,
  "category": "RESOURCE",
  "resource_type": "IRON",
  "level": 7,
  "owner_id": "Player1",
  "durability": 700,
  "max_durability": 700,
  "production": {
    "IRON": 700
  }
}
```

---

### 3. GET `/map/marches`
현재 진행 중인 모든 행군을 조회합니다.

**Response:**
```json
{
  "marches": [
    {
      "army_id": "army_Player1_Garen",
      "owner_id": "Player1",
      "champion_name": "Garen",
      "from": [0, 0],
      "to": [5, 5],
      "status": "MARCHING",
      "arrival_time": "2026-02-05T10:15:30"
    }
  ]
}
```

---

### 4. POST `/map/march`
부대를 특정 좌표로 행군시킵니다.

**Request Body:**
```json
{
  "user_id": "Player1",
  "champion_key": "Garen",
  "target_x": 5,
  "target_y": 5
}
```

**Response:**
```json
{
  "message": "March started",
  "army_id": "army_Player1_Garen",
  "target": [5, 5],
  "arrival_time": "2026-02-05T10:15:30"
}
```

---

### 5. POST `/map/update`
게임 상태를 업데이트합니다 (행군 도착 처리 등).

Flutter에서 주기적으로 호출해야 합니다 (예: 1초마다).

**Response:**
```json
{
  "message": "Game state updated",
  "active_marches": 2
}
```

---

### 6. POST `/map/building/place`
맵에 건물을 배치합니다.

**Request Body:**
```json
{
  "user_id": "Player1",
  "building_type": "MAIN_CASTLE",
  "x": 1,
  "y": 1
}
```

**Building Types:**
- `MAIN_CASTLE`: 주성 (3x3 크기)
- `BARRACKS`: 막사 (1x1 크기)

**Response:**
```json
{
  "message": "Building placed",
  "building_id": "MAIN_CASTLE_1_1",
  "type": "MAIN_CASTLE",
  "position": [1, 1]
}
```

---

## 👤 User Endpoints

### 7. GET `/user/{user_id}`
유저의 현재 상태를 조회합니다.

**Response:**
```json
{
  "user_id": "Player1",
  "db_id": 1,
  "gold": 1000,
  "champions": [
    {
      "id": 1,
      "user_id": 1,
      "champion_key": "Garen",
      "level": 5,
      "exp": 250
    }
  ]
}
```

---

### 8. POST `/user/{user_id}/champion/add`
유저에게 챔피언을 추가합니다.

**Query Parameters:**
- `champion_key`: 챔피언 키 (예: "Garen", "Darius")

**Response:**
```json
{
  "message": "Champion Garen added to user Player1"
}
```

---

## ⚔️ Champion & Battle Endpoints

### 9. GET `/champions`
사용 가능한 모든 챔피언 목록을 조회합니다.

**Response:**
```json
[
  {
    "id": "Garen",
    "name": "가렌",
    "base_stat": {
      "HP": 616,
      "ATK": 66,
      "DEF": 36,
      "SPATK": 0,
      "SPDEF": 32,
      "SPD": 340
    }
  }
]
```

---

### 10. POST `/simulate`
두 챔피언 간의 전투를 시뮬레이션합니다.

**Request Body:**
```json
{
  "left_id": "Garen",
  "right_id": "Darius"
}
```

**Response:**
```json
{
  "winner": "Garen",
  "logs": [
    {
      "turn": 1,
      "actor": "Garen",
      "target": "Darius",
      "action": "일반 공격",
      "damage": 120.5,
      "message": "Garen의 일반 공격! (120.5 데미지)",
      "left_hp": 616,
      "right_hp": 495.5
    }
  ],
  "left": {
    "name": "Garen",
    "max_hp": 616
  },
  "right": {
    "name": "Darius",
    "max_hp": 616
  }
}
```

---

## 🔄 Flutter Integration Guide

### 1. 초기화 시퀀스
```dart
// 1. 맵 데이터 로드
final mapData = await http.get(Uri.parse('http://localhost:8000/map'));

// 2. 유저 상태 로드
final userData = await http.get(Uri.parse('http://localhost:8000/user/Player1'));

// 3. 챔피언 목록 로드
final champions = await http.get(Uri.parse('http://localhost:8000/champions'));
```

### 2. 주기적 업데이트
```dart
Timer.periodic(Duration(seconds: 1), (timer) async {
  // 게임 상태 업데이트
  await http.post(Uri.parse('http://localhost:8000/map/update'));
  
  // 맵 다시 로드
  final mapData = await http.get(Uri.parse('http://localhost:8000/map'));
  setState(() {
    // UI 업데이트
  });
});
```

### 3. 행군 명령
```dart
Future<void> sendMarch(int targetX, int targetY) async {
  final response = await http.post(
    Uri.parse('http://localhost:8000/map/march'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({
      'user_id': 'Player1',
      'champion_key': 'Garen',
      'target_x': targetX,
      'target_y': targetY,
    }),
  );
  
  if (response.statusCode == 200) {
    print('March started!');
  }
}
```

---

## 🎮 Game Flow

1. **앱 시작**: `/map`, `/user/{user_id}` 호출하여 초기 데이터 로드
2. **맵 렌더링**: 받은 타일 데이터를 기반으로 Grid 형태로 맵 표시
3. **타일 클릭**: 특정 타일 클릭 시 `/map/tile/{x}/{y}`로 상세 정보 조회
4. **행군 시작**: 유저가 목표 타일 선택 후 `/map/march` 호출
5. **실시간 업데이트**: 1초마다 `/map/update` 호출하여 게임 상태 갱신
6. **전투 결과**: 행군이 도착하면 자동으로 전투 발생, 맵 상태 업데이트

---

## 📝 Notes

- 현재 서버는 **인메모리 상태**를 사용하므로 서버 재시작 시 모든 데이터가 초기화됩니다.
- 프로덕션 환경에서는 맵 상태를 데이터베이스에 저장해야 합니다.
- CORS가 모든 origin에 대해 열려있으므로 개발 환경에서만 사용하세요.
