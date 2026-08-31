import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "123456")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "instance", "placement.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ML_MODEL_PATH = os.path.join(BASE_DIR, "ml", "model.pkl")
    ML_SCALER_PATH = os.path.join(BASE_DIR, "ml", "scaler.pkl")
    ML_META_PATH = os.path.join(BASE_DIR, "ml", "meta.pkl")
    DATASET_PATH = os.path.join(BASE_DIR, "ml", "dataset", "placement_data.csv")
