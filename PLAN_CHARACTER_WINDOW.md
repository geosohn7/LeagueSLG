
# 캐릭터 정보 창 (Character Window) 구현 계획서

## 1. 개요
플레이어가 보유한 장수를 직관적으로 확인하고, 상세 정보를 관리할 수 있는 시스템입니다. 
뽑기(Gacha) 및 맵(Map)과 함께 핵심 기능으로 자리잡습니다.

## 2. 화면 구성 (UI Specs)

### A. 보유 장수 목록 (Roster)
*   **레이아웃**: 그리드 형태의 카드 리스트.
*   **카드 정보**: 장수 초상화, 등급(배경색), 레벨, 이름.
*   **동작**: 카드 터치 시 상세 화면으로 진입.

### B. 장수 상세 화면 (Detail View)
*   **배경**: 해당 장수의 전신 일러스트(Full Body Illustration).
*   **네비게이션**: 상단에 뒤로가기, 하단에 3개의 탭 버튼.
*   **탭 구성**:
    1.  **능력치 (Stats)**:
        *   레벨, 경험치 바.
        *   주요 스탯(ATK, DEF, INT 등) 표시 (숫자 + 그래프 권장).
    2.  **아이템 (Items)**:
        *   3개의 장비 슬롯.
        *   장비 장착/해제 및 아이템 상세 팝업.
    3.  **인연/설명 (Bonds & Lore)**:
        *   **열전(Lore)**: 장수의 역사적 배경 설명 텍스트.
        *   **인연(Bonds)**: 이 장수가 포함된 인연 목록.
            *   활성화된 인연: 밝게 표시 + 효과 설명.
            *   비활성화된 인연: 어둡게 표시 + 필요한 파트너 장수 표시.

## 3. 개발 단계 (Roadmap)

### [Phase 1] 백엔드 및 데이터 (Backend)
1.  **데이터 확장**: `champions.json`에 `description` 필드 추가.
2.  **인연 조회 로직**: `BondManager`에 '특정 장수 관련 인연 검색' 기능 추가.
3.  **API 개발**:
    *   `GET /user/champions`: 보유 목록 조회.
    *   `GET /user/champion/{id}`: 장수 상세 정보 조회.

### [Phase 2] 프론트엔드 - 목록 (Frontend List)
1.  장수 카드 위젯 (`ChampionCard`) 개발.
2.  그리드 뷰 화면 (`ChampionListScreen`) 개발.
3.  API 연동.

### [Phase 3] 프론트엔드 - 상세 (Frontend Detail)
1.  탭 컨트롤러 및 배경 이미지 처리.
2.  각 탭(`Stats`, `Items`, `Bonds`) 별 위젯 구현.
3.  인연 데이터 시각화 로직 구현.

## 4. 데이터 예시
```json
// GET /user/champion/123 Response
{
  "name": "계백",
  "stats": {"HP": 700, "ATK": 150, "DEF": 200, ...},
  "description": "백제의 마지막 충신...",
  "active_bonds": ["황산벌의 영웅들"],
  "potential_bonds": [
    {
      "name": "황산벌의 영웅들",
      "required": ["계백", "김유신", "관창", "반굴"],
      "description": "4명 중 3명 이상..."
    }
  ]
}
```
