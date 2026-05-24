import os
import shutil

SOURCE_DIR = "datasets/IMD2020"
REAL_DIR = "datasets/IMD2020_real"
FAKE_DIR = "datasets/IMD2020_fake"

os.makedirs(REAL_DIR, exist_ok=True)
os.makedirs(FAKE_DIR, exist_ok=True)

real_count = 0
fake_count = 0

for folder in os.listdir(SOURCE_DIR):

    folder_path = os.path.join(SOURCE_DIR, folder)

    if not os.path.isdir(folder_path):
        continue

    for file in os.listdir(folder_path):

        file_path = os.path.join(folder_path, file)

        # skip masks
        if "_mask" in file:
            continue

        # REAL image
        if "_orig" in file:

            dst = os.path.join(REAL_DIR, file)

            if not os.path.exists(dst):
                shutil.copy(file_path, dst)
                real_count += 1


        # FAKE image
        elif "_0" in file:

            dst = os.path.join(FAKE_DIR, file)

            if not os.path.exists(dst):
                shutil.copy(file_path, dst)
                fake_count += 1


print(f"Real images copied: {real_count}")
print(f"Fake images copied: {fake_count}")
print("IMD2020 dataset prepared successfully ✅")