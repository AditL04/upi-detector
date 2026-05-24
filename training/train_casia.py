import torch
import torch.nn as nn
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import timm
import os


def main():

    ###########################################
    # DEVICE
    ###########################################

    device = "cpu"
    print("\nTraining on:", device)

    ###########################################
    # TRANSFORM (CPU optimized)
    ###########################################

    transform = transforms.Compose([
        transforms.Resize((128,128)),
        transforms.ToTensor()
    ])

    ###########################################
    # DATASET LOAD
    ###########################################

    dataset = datasets.ImageFolder(
        "datasets/CASIA",
        transform=transform
    )

    print("Classes detected:", dataset.classes)
    print("Total images:", len(dataset))

    ###########################################
    # DATALOADER (Windows safe)
    ###########################################

    loader = DataLoader(
        dataset,
        batch_size=1,
        shuffle=True,
        num_workers=0
    )

    print("\nDataset ready. Starting model...")

    ###########################################
    # MODEL LOAD (NO HF FREEZE)
    ###########################################

    model = timm.create_model(
        "efficientnet_b0",
        pretrained=False,
        num_classes=2
    )

    print("Model initialized.")

    model.to(device)

    ###########################################
    # OPTIMIZER + LOSS
    ###########################################

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=1e-4
    )

    criterion = nn.CrossEntropyLoss()

    ###########################################
    # TRAIN LOOP
    ###########################################

    epochs = 2

    print("\nStarting training loop...\n")

    for epoch in range(epochs):

        running_loss = 0

        for step, (images, labels) in enumerate(loader):

            images = images.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()

            outputs = model(images)

            loss = criterion(outputs, labels)

            loss.backward()

            optimizer.step()

            running_loss += loss.item()

            ###########################################
            # LIVE PROGRESS PRINT
            ###########################################

            if step % 200 == 0:
                print(f"Epoch {epoch+1} | Processed {step}/{len(dataset)} images")

        ###########################################
        # EPOCH LOSS
        ###########################################

        print(f"\nEpoch {epoch+1}/{epochs} Loss: {running_loss:.4f}\n")

    ###########################################
    # SAVE MODEL
    ###########################################

    os.makedirs("cnn_backbone", exist_ok=True)

    torch.save(
        model.state_dict(),
        "cnn_backbone/casia_model.pth"
    )

    print("\nCASIA training complete ✅")


###########################################
# WINDOWS SAFE ENTRY POINT
###########################################

if __name__ == "__main__":
    main()