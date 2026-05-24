import torch
import timm
from torchvision import transforms
from PIL import Image, ImageChops, ImageEnhance


device = "cpu"


class UPIDetector:

    def __init__(self):

        self.model = timm.create_model(
            "efficientnet_b0",
            pretrained=False,
            in_chans=4,
            num_classes=2
        )

        self.model.load_state_dict(
            torch.load("cnn_backbone/upi_model.pth", map_location=device)
        )

        self.model.eval()
        self.model.to(device)

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485,0.456,0.406],
                std=[0.229,0.224,0.225]
            )
        ])


    def make_ela(self, image, quality=90):

        temp_path = "temp_ela.jpg"
        image.save(temp_path, "JPEG", quality=quality)

        compressed = Image.open(temp_path).convert("RGB")

        ela = ImageChops.difference(image, compressed)

        extrema = ela.getextrema()

        max_diff = max([ex[1] for ex in extrema])

        if max_diff == 0:
            max_diff = 1

        scale = 255.0 / max_diff

        ela = ImageEnhance.Brightness(ela).enhance(scale)

        return ela


    def predict(self, image_path):

        image = Image.open(image_path).convert("RGB")

        ela = self.make_ela(image, quality=90)

        rgb_tensor = self.transform(image)

        ela_gray = ela.convert("L")
        ela_gray = transforms.Resize((224,224))(ela_gray)
        ela_tensor = transforms.ToTensor()(ela_gray)

        stacked = torch.cat([rgb_tensor, ela_tensor], dim=0).unsqueeze(0).to(device)

        with torch.no_grad():

            output = self.model(stacked)
            probs = torch.softmax(output, dim=1)
            prediction = torch.argmax(output, dim=1).item()

        if prediction == 0:
            return "FAKE", float(probs[0][0].item())
        else:
            return "REAL", float(probs[0][1].item())