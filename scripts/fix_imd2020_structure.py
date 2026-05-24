import os
import shutil

src_real = "datasets/IMD2020_real"
src_fake = "datasets/IMD2020_fake"

dst_real = "datasets/IMD2020_binary/real"
dst_fake = "datasets/IMD2020_binary/fake"

os.makedirs(dst_real, exist_ok=True)
os.makedirs(dst_fake, exist_ok=True)

for f in os.listdir(src_real):
    shutil.move(os.path.join(src_real, f),
                os.path.join(dst_real, f))

for f in os.listdir(src_fake):
    shutil.move(os.path.join(src_fake, f),
                os.path.join(dst_fake, f))

print("IMD2020 folder structure fixed ✅")