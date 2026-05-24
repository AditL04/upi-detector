import sys
import os
import random
import numpy as np
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
import timm
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, random_split, WeightedRandomSampler
from PIL import Image, ImageChops, ImageEnhance


def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def make_ela(image, quality=90):
    temp_path = "temp_ela.jpg"
    image.save(temp_path, "JPEG", quality=quality)
    compressed = Image.open(temp_path).convert("RGB")
    ela_image = ImageChops.difference(image, compressed)
    extrema = ela_image.getextrema()
    max_diff = max([ex[1] for ex in extrema])
    if max_diff == 0:
        max_diff = 1
    scale = 255.0 / max_diff
    ela_image = ImageEnhance.Brightness(ela_image).enhance(scale)
    return ela_image


def main():
    set_seed(42)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("\nTraining on:", device)

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    class ELADataset(datasets.ImageFolder):
        def __init__(self, root, transform=None):
            super().__init__(root)
            self.transform = transform

        def __getitem__(self, index):
            path, label = self.samples[index]
            image = Image.open(path).convert("RGB")
            ela_image = make_ela(image, quality=90)
            rgb_tensor = self.transform(image)
            ela_gray = ela_image.convert("L")
            ela_gray = transforms.Resize((224, 224))(ela_gray)
            ela_tensor = transforms.ToTensor()(ela_gray)
            stacked = torch.cat([rgb_tensor, ela_tensor], dim=0)
            return stacked, label

    dataset = ELADataset("datasets/upi", transform=transform)

    print("Classes detected:", dataset.classes)
    print("Class mapping:", dataset.class_to_idx)
    print("Total images:", len(dataset))

    train_size = int(0.85 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])

    train_labels = [dataset.samples[i][1] for i in train_dataset.indices]
    class_counts = np.bincount(train_labels)
    class_weights = 1.0 / class_counts
    sample_weights = [class_weights[label] for label in train_labels]

    sampler = WeightedRandomSampler(
        weights=sample_weights,
        num_samples=len(sample_weights),
        replacement=True
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=8,
        sampler=sampler,
        num_workers=0
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=8,
        shuffle=False,
        num_workers=0
    )

    print("\nLoading EfficientNet backbone...")

    model = timm.create_model(
        "efficientnet_b0",
        pretrained=True,
        in_chans=4,
        num_classes=2
    )

    print("Backbone loaded successfully")
    model.to(device)

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=3e-5,
        weight_decay=1e-4
    )

    criterion = torch.nn.CrossEntropyLoss(
        weight=torch.tensor([1.25, 0.75]).to(device)
    )

    epochs = 15
    best_val_acc = 0.0

    print("\nStarting UPI finetuning...\n")

    for epoch in range(epochs):
        model.train()
        running_loss = 0

        for step, (images, labels) in enumerate(train_loader):
            images = images.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        model.eval()
        correct = 0
        total = 0

        with torch.no_grad():
            for images, labels in val_loader:
                images = images.to(device)
                labels = labels.to(device)

                outputs = model(images)
                preds = torch.argmax(outputs, dim=1)

                total += labels.size(0)
                correct += (preds == labels).sum().item()

        val_acc = 100 * correct / max(total, 1)

        print(
            f"Epoch {epoch+1}/{epochs} "
            f"Loss: {running_loss/len(train_loader):.4f} "
            f"| Val Acc: {val_acc:.2f}%"
        )

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            os.makedirs("cnn_backbone", exist_ok=True)
            torch.save(model.state_dict(), "cnn_backbone/upi_model.pth")
            print("Saved best model")

    print("\nBest Validation Accuracy:", round(best_val_acc, 2), "%")
    print("\nUPI finetuning complete ✅")


if __name__ == "__main__":
    main()