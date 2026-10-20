# 도파민 보물섬 — 백엔드

수원대학교 캠퍼스 보물찾기 모바일 웹 서비스의 백엔드 레포지토리입니다.

---

## 프로젝트 소개

수원대학교 시험기간에 학생들이 캠퍼스 곳곳에 숨겨진 보물(응원메세지·짤·기프티콘)을 찾는 모바일 웹 MVP입니다. 6일 안에 기획·개발·배포까지 완료한 팀 프로젝트입니다.

| 항목 | 내용 |
| --- | --- |
| 서비스명 | 도파민 보물섬: 수원대에서 보물찾기 |
| 개발 기간 | 2026년 4월 (6일) |
| 팀 구성 | PM/기획 1명, 백엔드 1명, 프론트엔드 1명, QA 보조 1명 |
| 담당 | 백엔드 전체 |
| 배포 URL(현재: 종료)| https://dopamine-treasure-backend-production.up.railway.app |

---

## 기술 스택

| 분류 | 기술 |
| --- | --- |
| 언어 | Python 3.13 |
| 프레임워크 | FastAPI |
| ORM | SQLAlchemy |
| DB | MySQL |
| DB 드라이버 | PyMySQL |
| 이미지 업로드 | python-multipart |
| 환경변수 | python-dotenv |
| 배포 | Railway |

---

## 폴더 구조

```
dopamine-treasure/
│
├── main.py                  # 앱 진입점, 라우터 연결, CORS 설정
├── database.py              # DB 연결 설정 (Unix 소켓 방식)
├── requirements.txt
├── .env
│
├── models/                  # DB 테이블 정의 (SQLAlchemy)
│   ├── location.py
│   ├── treasure.py
│   └── attempt.py
│
├── schemas/                 # 요청/응답 데이터 형식 (Pydantic)
│   ├── location.py
│   ├── treasure.py
│   └── attempt.py
│
├── routers/                 # API 엔드포인트
│   ├── locations.py
│   ├── treasures.py
│   └── admin.py
│
└── uploads/                 # 사진 미션·기프티콘 이미지 저장
```

---

## 로컬 실행 방법

**1. 저장소 클론 및 가상환경 설정**

```bash
git clone <repo-url>
cd dopamine-treasure
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**2. 환경변수 설정**

`.env` 파일을 루트에 생성하고 아래 내용을 입력합니다.

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=비밀번호
DB_NAME=dopamine_treasure
ADMIN_PASSWORD=관리자비밀번호
```

> MySQL 소켓 방식으로 연결하는 경우 `database.py`의 `DATABASE_URL`에 `?unix_socket=/tmp/mysql.sock`이 추가되어 있습니다.

**3. DB 생성**

```sql
CREATE DATABASE dopamine_treasure CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

**4. 서버 실행**

```bash
uvicorn main:app --reload
```

서버 기동 시 `Base.metadata.create_all()`로 테이블이 자동 생성됩니다. 이후 `http://localhost:8000/docs`에서 Swagger UI로 API를 테스트할 수 있습니다.

---

## API 명세서

### 장소 관련

| 메서드 | 엔드포인트 | 설명 |
| --- | --- | --- |
| GET | `/locations` | 장소 목록 + 보물 현황 (treasure_count, max_count) |
| GET | `/locations/{id}` | 장소 상세 + 현재 미션 내용 |

### 보물 찾기

| 메서드 | 엔드포인트 | 설명 |
| --- | --- | --- |
| POST | `/locations/{id}/verify` | 퀴즈 정답 또는 사진 제출 → 인증 성공/실패 (multipart/form-data) |
| POST | `/locations/{id}/claim` | 인증 성공 후 보물 랜덤 획득 (multipart/form-data) |

> **시간제한:** 같은 학번 기준 퀴즈 성공 또는 사진 승인 대기 중이면 30분 동안 미션 참여 불가. 사진 거절 시 재도전 가능.

### 보물 숨기기

| 메서드 | 엔드포인트 | 설명 |
| --- | --- | --- |
| POST | `/treasures` | 보물 등록 (메세지·짤·기프티콘) — multipart/form-data |

> `treasure_type`: `message`·`meme` → 즉시 approved / `gifticon` → pending (관리자 승인 필요). 장소별 최대 10개 제한.
>
> `mission_answer`: 정답 여러 개일 경우 쉼표로 구분 (예: `"66,67,68"`)

### 관리자

| 메서드 | 엔드포인트 | 설명 |
| --- | --- | --- |
| POST | `/admin/login` | 비밀번호 인증 |
| GET | `/admin/locations` | 장소 목록 |
| GET | `/admin/treasures` | 보물 목록 (`?status=pending`·`approved`·전체) |
| GET | `/admin/attempts` | 사진 미션 승인 대기 목록 |
| GET | `/admin/claims` | 보물 획득 내역 (최신순) |
| GET | `/admin/stats` | 학번별 획득 개수 통계 |
| PATCH | `/admin/attempts/{id}` | 사진 미션 승인/거절 |
| PATCH | `/admin/treasures/{id}` | 기프티콘 승인/내용 수정 |

---

## DB 스키마

### locations

| 컬럼 | 타입 | 설명 |
| --- | --- | --- |
| id | INT PK | 장소 ID |
| name | VARCHAR(100) | 장소명 |

### treasures

| 컬럼 | 타입 | 설명 |
| --- | --- | --- |
| id | INT PK | 보물 ID |
| location_id | INT FK | 장소 참조 |
| name | VARCHAR(100) | 숨긴 사람 닉네임 |
| student_id | VARCHAR(100) | 학번 |
| department | VARCHAR(100) | 학과 |
| treasure_type | VARCHAR(20) | message·meme·gifticon |
| mission_type | VARCHAR(20) | quiz·photo |
| mission_content | VARCHAR(500) | 미션 내용 |
| mission_answer | VARCHAR(100) | 퀴즈 정답 (쉼표 구분 다중 정답 가능) |
| content | VARCHAR(1000) | 보물 내용 (응원메세지 등) |
| image_path | VARCHAR(500) | 이미지 경로 |
| is_claimed | BOOLEAN | 획득 여부 |
| status | VARCHAR(20) | pending·approved |
| claimed_by | VARCHAR(100) | 획득자 학번 |
| claimed_at | DATETIME | 획득 시간 |

### attempts

| 컬럼 | 타입 | 설명 |
| --- | --- | --- |
| id | INT PK | 인증 시도 ID |
| location_id | INT FK | 장소 참조 |
| name | VARCHAR(100) | 이름 |
| student_id | VARCHAR(100) | 학번 |
| department | VARCHAR(100) | 학과 |
| phone | VARCHAR(20) | 전화번호 (사진 미션 시) |
| agreed | BOOLEAN | 개인정보 수집 동의 |
| mission_type | VARCHAR(20) | quiz·photo |
| answer | VARCHAR(100) | 퀴즈 제출 답 |
| image_path | VARCHAR(500) | 사진 미션 이미지 경로 |
| is_correct | BOOLEAN | 정답 여부 |
| status | VARCHAR(20) | pending·approved·rejected |
| attempt_time | DATETIME | 시도 시각 |

---

## 배포

Railway를 통해 배포합니다.

**배포 URL:** `https://dopamine-treasure-backend-production.up.railway.app`

**배포 절차**

1. Railway에서 새 프로젝트 생성 후 GitHub 저장소 연결
2. Railway MySQL 플러그인 추가 후 환경변수 설정
3. 아래 환경변수를 Railway 대시보드에 등록

```env
DB_HOST=
DB_PORT=
DB_USER=
DB_PASSWORD=
DB_NAME=
ADMIN_PASSWORD=
```

4. 배포 후 `uploads/` 폴더 static 파일 서빙 확인 (`main.py`에 포함됨)

```python
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
```

> **CORS 허용 오리진:** `https://0601sunny-spec.github.io`, `http://127.0.0.1:5500`, `http://localhost:5500`
