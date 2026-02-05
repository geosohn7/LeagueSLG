# 🎨 LeagueSLG 에셋 창고 (Asset Warehouse)

이 디렉토리는 게임의 모든 비주얼 에셋을 체계적으로 관리하기 위한 창고입니다.

## 📁 폴더 구조

```
assets/
├── models/              # 3D 모델 파일 (.glb, .obj 등)
│   ├── champions/       # 챔피언 3D 모델
│   ├── buildings/       # 건물 3D 모델
│   └── tiles/           # 타일/지형 3D 모델
│
├── textures/            # 텍스처 이미지
│   ├── champions/       # 챔피언 텍스처
│   ├── buildings/       # 건물 텍스처
│   └── tiles/           # 타일 텍스처
│
├── images/              # 2D 이미지 파일
│   ├── champions/       # 챔피언 아이콘, 초상화
│   ├── buildings/       # 건물 아이콘
│   ├── tiles/           # 타일 아이콘
│   ├── backgrounds/     # 배경 이미지
│   └── ui/              # UI 요소 이미지
│
├── animations/          # 애니메이션 파일
│
├── effects/             # 이펙트 파일
│   └── particles/       # 파티클 이펙트
│
└── sounds/              # 사운드 파일
    └── effects/         # 효과음
```

## 🎯 에셋 추가 방법

### 1. 3D 모델 추가하기

**예시: 가렌 챔피언 모델 추가**

1. Blender에서 모델을 `.glb` 형식으로 익스포트합니다.
2. 파일을 `assets/models/champions/garen.glb`에 저장합니다.
3. `data/assets_registry.json`에서 해당 경로가 이미 정의되어 있는지 확인합니다.
4. 서버를 재시작하면 자동으로 새 모델이 적용됩니다!

### 2. 챔피언 이미지 추가하기

**예시: 다리우스 초상화 추가**

1. 이미지 파일을 준비합니다 (권장: PNG, 512x512 이상).
2. 파일을 `assets/images/champions/darius_portrait.png`에 저장합니다.
3. Flutter 앱에서는 `AssetRegistry`가 자동으로 이 이미지를 찾아 사용합니다.

### 3. 건물 모델 추가하기 (레벨별)

**예시: 주성 레벨 1~5 모델**

```
assets/models/buildings/
├── main_castle_lv1.glb
├── main_castle_lv2.glb
├── main_castle_lv3.glb
├── main_castle_lv4.glb
└── main_castle_lv5.glb
```

레지스트리에서 `{level}` 플레이스홀더를 사용하면 자동으로 레벨에 맞는 파일을 로드합니다.

## 🔧 에셋 레지스트리 수정

`data/assets_registry.json` 파일을 편집하여 에셋 경로를 관리합니다.

**새 챔피언 추가 예시:**

```json
"Ahri": {
  "id": "ahri",
  "name": "아리",
  "assets": {
    "model_3d": "models/champions/ahri.glb",
    "texture": "textures/champions/ahri_base.png",
    "icon": "images/champions/ahri_icon.png",
    "portrait": "images/champions/ahri_portrait.png",
    "animations": {
      "idle": "animations/ahri_idle.anim",
      "attack": "animations/ahri_attack.anim"
    }
  },
  "fallback": {
    "color": "#FF69B4",
    "icon_text": "A"
  }
}
```

## 🎨 Fallback 시스템

에셋 파일이 아직 없을 때는 자동으로 대체 표시가 사용됩니다:

- **3D 모델 없음** → 단색 원형 아바타 표시
- **이미지 없음** → fallback 색상 사용
- **애니메이션 없음** → 기본 애니메이션 사용

이를 통해 **에셋이 완성되기 전에도 게임을 테스트**할 수 있습니다!

## 📝 권장 파일 형식

| 에셋 타입 | 권장 형식 | 해상도/사이즈 |
|----------|----------|--------------|
| 3D 모델 | `.glb` | 10,000 폴리곤 이하 |
| 텍스처 | `.png` | 1024x1024 또는 2048x2048 |
| 아이콘 | `.png` (투명) | 256x256 |
| 초상화 | `.png` | 512x512 |
| 배경 | `.jpg` 또는 `.png` | 1920x1080 이상 |
| 효과음 | `.mp3` | 128kbps |

## 🚀 사용 예시

### 백엔드 (Python)

```python
from src.common.asset_registry import get_asset_registry

registry = get_asset_registry()

# 챔피언 에셋 조회
garen_assets = registry.get_champion_assets("Garen")
print(garen_assets["assets"]["model_3d"])  # "models/champions/garen.glb"

# 건물 에셋 조회 (레벨 3)
castle_assets = registry.get_building_assets("MAIN_CASTLE", level=3)
print(castle_assets["assets"]["model_3d"])  # "models/buildings/main_castle_lv3.glb"
```

### 프론트엔드 (Flutter)

```dart
import 'asset_registry.dart';

final registry = AssetRegistry.instance;
await registry.initialize();

// 챔피언 에셋 조회
final garenAssets = registry.getChampionAssets('Garen');
if (garenAssets?.model3d != null) {
  // 3D 모델 로드
  load3DModel(garenAssets!.model3d!);
} else {
  // Fallback 색상 사용
  showColorAvatar(garenAssets!.fallbackColor);
}
```

## 🎯 다음 단계

1. **Blender에서 3D 모델 제작**
2. **모델을 `.glb` 형식으로 익스포트**
3. **해당 폴더에 파일 저장**
4. **게임 실행하여 확인!**

코드 수정 없이 파일만 추가하면 자동으로 게임에 반영됩니다.

---

**Happy Asset Management! 🎨**
