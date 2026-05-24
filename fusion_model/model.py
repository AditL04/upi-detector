from sklearn.ensemble import RandomForestClassifier
import pickle

model = RandomForestClassifier()

# placeholder training
# actual vector generation already exists in pipeline

pickle.dump(model,open("fusion_model/fusion.pkl","wb"))