import torch
import torchvision

def load_model(weight_path):
    """
    ResNet18 모델을 로드하고 하프 프리시전 및 평가 모드로 설정
    Args:
        weight_path (str): 저장된 모델 가중치 파일 경로 (예: 'best.pth')
    Returns:
        model (nn.Module): 로드된 모델
        device (torch.device): 모델이 올라간 디바이스
        mean (Tensor): 정규화를 위한 평균
        std (Tensor): 정규화를 위한 표준편차
    """
    model = torchvision.models.resnet18(pretrained=False)
    model.fc = torch.nn.Linear(512, 2)
    state_dict = torch.load(weight_path)
    model.load_state_dict(state_dict)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device).eval().half()

    mean = torch.Tensor([0.485, 0.456, 0.406]).to(device).half()
    std  = torch.Tensor([0.229, 0.224, 0.225]).to(device).half()

    return model, device, mean, std