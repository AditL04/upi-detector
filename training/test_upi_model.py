import torch
import timm
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
from PIL import Image, ImageChops, ImageEnhance


device = "cpu"

transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485,0.456,0.406],
        std=[0.229,0.224,0.225]
    )
])

def make_ela(image, quality=90):
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

class ELATestDataset(datasets.ImageFolder):
    def __getitem__(self, index):
        path, label = self.samples[index]
        image = Image.open(path).convert("RGB")
        ela = make_ela(image, quality=90)

        rgb_tensor = transform(image)

        ela_gray = ela.convert("L")
        ela_gray = transforms.Resize((224,224))(ela_gray)
        ela_tensor = transforms.ToTensor()(ela_gray)

        stacked = torch.cat([rgb_tensor, ela_tensor], dim=0)

        return stacked, label, path

dataset = ELATestDataset("datasets/upi/test")

loader = DataLoader(
    dataset,
    batch_size=1,
    shuffle=False
)

model = timm.create_model(
    "efficientnet_b0",
    pretrained=False,
    in_chans=4,
    num_classes=2
)

model.load_state_dict(
    torch.load("cnn_backbone/upi_model.pth", map_location=device)
)

model.eval()
model.to(device)

correct = 0
total = 0

fake_correct = 0
real_correct = 0

fake_total = 0
real_total = 0

false_fake = 0
false_real = 0

with torch.no_grad():
    for images, labels, paths in loader:
        images = images.to(device)
        labels = labels.to(device)

        outputs = model(images)
        probs = torch.softmax(outputs, dim=1)
        prediction = torch.argmax(outputs, dim=1)

        total += 1

        if prediction.item() == labels.item():
            correct += 1

        if labels.item() == 0:
            fake_total += 1
            if prediction.item() == labels.item():
                fake_correct += 1
            else:
                false_real += 1

        if labels.item() == 1:
            real_total += 1
            if prediction.item() == labels.item():
                real_correct += 1
            else:
                false_fake += 1

        print(
            f"{paths[0]} | "
            f"True: {dataset.classes[labels.item()]} | "
            f"Pred: {dataset.classes[prediction.item()]} | "
            f"FakeProb: {probs[0][0].item():.4f} | "
            f"RealProb: {probs[0][1].item():.4f}"
        )

fake_precision = fake_correct / max(fake_correct + false_fake, 1)
fake_recall = fake_correct / max(fake_total, 1)

real_precision = real_correct / max(real_correct + false_real, 1)
real_recall = real_correct / max(real_total, 1)

print("\nOverall Accuracy:", round(correct / max(total,1) * 100, 2), "%")
print("Fake Accuracy:", round(fake_correct / max(fake_total,1) * 100, 2), "%")
print("Real Accuracy:", round(real_correct / max(real_total,1) * 100, 2), "%")
print("Fake Precision:", round(fake_precision * 100, 2), "%")
print("Fake Recall:", round(fake_recall * 100, 2), "%")
print("Real Precision:", round(real_precision * 100, 2), "%")
print("Real Recall:", round(real_recall * 100, 2), "%")
print("False Fake Count:", false_fake)
print("False Real Count:", false_real)