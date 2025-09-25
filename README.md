# 🤖 스마트 홈 IoT 제어 무인 청소 로봇 'SSALIE'
- AGV와 IoT 센서를 연동하여 환경에 자율적으로 반응하고, 수집된 데이터를 AI 리포트로 자동 생성하는 End-to-End 자동화 솔루션

## 📜 프로젝트 개요 (Overview)
- SSALIE는 임베디드 시스템과 클라우드 기술을 융합하여 실제 가정 환경과 유사한 IoT 제어 시나리오를 구현한 프로젝트입니다. Jetson Nano 기반의 AGV(자율 주행 로봇)가 도로를 따라 주행하며 쓰레기를 수거하고, 집안 곳곳에 설치된 ESP32 센서 디바이스는 온도와 공기질 데이터를 수집합니다.

- 모든 데이터는 AWS IoT Core를 통해 클라우드로 전송되며, AWS Lambda가 이를 처리하여 RDS에 저장합니다. 관리자는 Vue.js 기반의 웹 대시보드에서 실시간으로 모든 상황을 모니터링할 수 있으며, OpenAI GPT API와 연동된 자동화 시스템이 주기적으로 심층 분석 리포트를 생성하여 이메일(SES)로 전송합니다.

# ✨ 주요 기능 (Key Features)
## 🚗 AGV 자율 주행 및 임무 수행

- PyTorch ResNet-18 모델 기반의 차선 인식(Road Tracking) 주행

- PID 제어를 통한 안정적인 경로 추종

## 💨 IoT 센서 연동 및 자동화

- ESP32 디바이스를 활용한 실시간 온도 및 공기질 데이터 수집

- 수집된 데이터 임계값(Threshold)에 따라 가상 가전기기(팬, 공기청정기) 자동 제어

## 📊 클라우드 기반 데이터 파이프라인 및 대시보드

- AWS IoT Core, Lambda, RDS를 활용한 안정적인 데이터 수집 및 처리 파이프라인 구축

- Node.js와 Vue.js 기반의 관리자용 웹 대시보드를 통한 실시간 로그 및 차트 시각화

## 📧 AI 기반 자동 리포트 생성

- 수집된 데이터를 바탕으로 OpenAI GPT API가 주간/야간 분석 리포트를 자동 생성

- AWS SES를 통해 지정된 관리자에게 이메일로 리포트 자동 발송

# 🏛️ 시스템 아키텍처 (System Architecture)
코드 스니펫

graph TD

    subgraph Edge Devices
        A[AGV - Jetson Nano]
        B[IoT Sensor - ESP32]
    end

    subgraph Cloud - AWS
        C[AWS IoT Core]
        D[AWS Lambda]
        E[AWS RDS - MySQL]
        F[OpenAI GPT API]
        G[AWS SES]
        H[AWS S3]
    end

    subgraph User Interface
        I[Web Dashboard - Vue.js]
        J[Admin User]
    end

    A -- MQTT --> C
    B -- MQTT --> C
    C -- Trigger --> D
    D -- Preprocessing & Save --> E
    D -- Save Logs/Images --> H
    D -- Request Report --> F
    F -- Generate Report --> D
    D -- Send Email --> G
    G --> J
    I -- Fetches Data --> E
    J -- Monitors --> I
# 🛠️ 기술 스택 (Tech Stack)
| 분야 (Field) | 사용 기술 (Technology) | 선택 이유 (Reason) |
| :--- | :--- | :--- |
| **임베디드** | `ESP32` | 저전력/저비용 MCU로 MQTT 통신에 적합하고 GPIO 제어가 용이하여 Edge Device로 활용 |
| | `Jetson Nano` | GPU 가속 기반으로 딥러닝 추론을 효율적으로 수행할 수 있는 NVIDIA 임베디드 보드 |
| **AI/ML** | `PyTorch (ResNet-18)` | Transfer Learning이 용이하고 Jetson과의 호환성이 우수하여 자율 주행 모델로 채택 |
| | `PID 제어` | 경로 추종 시 발생하는 실시간 오차 보정을 위한 직관적이고 안정적인 제어 기법 |
| **네트워크** | `MQTT` | 경량 메시지 프로토콜로, 저사양 Edge Device와 AGV 간의 실시간 통신에 최적 |
| | `AWS IoT Core` | MQTT 메시지를 클라우드로 안전하게 중계하며 Lambda 등 다른 AWS 서비스와 쉽게 연동 가능 |
| **클라우드** | `AWS Lambda` | 서버리스 환경에서 GPT 리포트 생성 및 데이터 전처리 등 이벤트 기반 작업을 자동화하는 데 적합 |
| | `AWS RDS (MySQL)` | 센서 데이터 저장 및 프론트엔드와의 안정적인 연동을 위한 RDB |
| | `AWS S3` | 로그 파일, 이미지 등 비정형 데이터를 저장하고 관리하기 위한 스토리지 |
| | `AWS SES` | 자동화된 이메일 보고서를 관리자에게 안정적으로 발송하기 위해 구성 |
| **백엔드** | `Node.js (Express)` | 경량 REST API 서버를 빠르게 구축하고, MQTT 및 RDS 통신을 효율적으로 처리 |
| **프론트엔드** | `Vue.js` | 컴포넌트 기반 구조로 대시보드와 디바이스 상태 UI를 반응형으로 구현하는 데 효율적 |

# 💡 문제 해결 사례 (Problem Solving)
### 1. 자율 주행 모델의 낮은 정확도 개선
- 겪었던 문제:
    - 초기 Road Tracking 모델 학습에 사용된 약 500장의 데이터로는 방향 예측의 정확도와 일관성이 매우 부족했습니다. AGV가 경로를 자주 이탈하는 현상이 발생했습니다.

- 해결 과정:
    - 데이터 증강 (Augmentation): 추가로 500장의 도로 이미지를 직접 수집하고, 좌우 반전 기법을 적용하여 데이터의 양과 다양성을 2배로 확보했습니다.
    - 학습 심화: Epoch 수를 기존 20에서 100으로 늘려 모델이 데이터의 특징을 더 깊이 학습하도록 유도하여 예측 안정성을 크게 향상시켰습니다.

### 2. AWS Lambda 환경 종속성 불일치 문제
- 겪었던 문제:
    - OpenAI API 연동을 위해 Lambda Layer를 구성하는 과정에서, 로컬 개발 환경과 Lambda의 실제 실행 환경 간의 라이브러리 종속성 불일치로 인해 module import 에러가 지속적으로 발생했습니다.
- 해결 과정:
    - 실행 환경 통일: Lambda의 실행 환경과 동일한 Amazon Linux 2 기반 Docker 컨테이너를 로컬에 구축했습니다.
    - Layer 재구성: 컨테이너 내부에서 필요한 모든 패키지를 설치하고 압축하여 Layer를 구성함으로써, 실행 환경 간의 호환성 문제를 근본적으로 해결하고 GPT 리포트 자동화 기능을 안정적으로 운영할 수 있었습니다.

# 🚀 프로젝트 성과 및 회고 (Achievements & Retrospective)
## 성과
- 안정적인 Road Tracking 모델 구현 및 PID 제어를 통한 경로 추종 성능 확보

- 디바이스 제어 → 데이터 수집 → 자동 분석 → 시각화까지 이어지는 End-to-End 자동화 파이프라인 구축

- 임베디드, AI, 클라우드, 웹 개발 등 다양한 기술 도메인을 융합한 실무형 프로젝트 경험 축적

## 아쉬웠던 점 및 개선 방안
### SLAM의 부재
- 현재는 Road Tracking 기반 주행만 가능하여, 실제 환경에서 범용적으로 사용되기 위한 SLAM(동시적 위치 추정 및 지도 작성) 기능이 미흡합니다.

- 개선 방안: LiDAR 또는 ToF 거리 센서를 추가하여 SLAM 기반의 맵핑 기능을 구현하고, A* 알고리즘을 적용한 최적 경로 계획 로직을 개발.

### 임무 수행 안정성
- Trash Picking 기능의 기구적 한계와 인식률 문제로 성공률이 100%에 미치지 못합니다.

- 개선 방안: 그리퍼 등 기구 설계를 보완하고, 더 다양한 환경에서 수집된 데이터로 객체 인식 모델의 정확도를 향상.