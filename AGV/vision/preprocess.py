import PIL.Image
import torchvision.transforms as transforms
import torch
import numpy as np

def preprocess(img, device, mean, std):
    """
    BGR 이미지(Numpy) → 전처리된 텐서
    Args:
        img (np.ndarray): 카메라에서 받은 BGR 이미지
        device (torch.device): 모델 디바이스 (cuda or cpu)
        mean (Tensor): 이미지 정규화를 위한 평균값
        std (Tensor): 이미지 정규화를 위한 표준편차
    Returns:
        torch.Tensor: (1, 3, 224, 224) 형태의 전처리된 텐서
    """
    img = PIL.Image.fromarray(img)
    t = transforms.functional.to_tensor(img).to(device).half()
    t.sub_(mean[:, None, None]).div_(std[:, None, None])
    return t[None, ...]