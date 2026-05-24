import torch
import timm
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
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
        transforms.Resize((224,224)),
        transforms.ToTensor()
    ])

    ###########################################
    # DATASET LOAD
    ###########################################

    dataset = datasets.ImageFolder(
        "datasets/IMD2020_binary",
        transform=transform
    )

    print("Classes detected:", dataset.classes)
    print("Total images:", len(dataset))

    ###########################################
    # DATALOADER
    ###########################################

    loader = DataLoader(
        dataset,
        batch_size=8,
        shuffle=True,
        num_workers=0
    )

    print("\nDataset ready. Loading CASIA backbone...")

    ###########################################
    # LOAD CASIA MODEL
    ###########################################

    model = timm.create_model(
        "efficientnet_b0",
        pretrained=False,
        num_classes=2
    )

    model.load_state_dict(
        torch.load("cnn_backbone/casia_model.pth")
    )

    print("CASIA backbone loaded successfully.")

    model.to(device)

    ###########################################
    # OPTIMIZER + LOSS
    ###########################################

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=1e-5
    )

    criterion = torch.nn.CrossEntropyLoss()

    ###########################################
    # TRAIN LOOP
    ###########################################

    epochs = 5

    print("\nStarting IMD2020 training...\n")

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
        # EPOCH LOSS PRINT
        ###########################################

        print(f"\nEpoch {epoch+1}/{epochs} Loss: {running_loss:.4f}\n")

    ###########################################
    # SAVE MODEL
    ###########################################

    os.makedirs("cnn_backbone", exist_ok=True)

    torch.save(
        model.state_dict(),
        "cnn_backbone/imd_model.pth"
    )

    print("\nIMD2020 training complete ✅")


###########################################
# WINDOWS SAFE ENTRY
###########################################

if __name__ == "__main__":
    main()