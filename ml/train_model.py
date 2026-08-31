import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
#from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

HERE = os.path.dirname(__file__)
DATASET_PATH = os.path.join(HERE, "dataset", "placement_data.csv")
MODEL_PATH = os.path.join(HERE, "model.pkl")
SCALER_PATH = os.path.join(HERE, "scaler.pkl")
META_PATH = os.path.join(HERE, "meta.pkl")

FEATURE_COLUMNS = [
    "cgpa", "backlogs", "internships", "technical_skills_count",
    "communication_score", "ssc_percentage", "hsc_percentage",
]


def main():
    if not os.path.exists(DATASET_PATH):
        raise SystemExit(
            f"Dataset not found at {DATASET_PATH}.\n"
            f"Run python generate_sample_dataset.py first"
            f"check placement_data.csv for column names"
        )

    df = pd.read_csv(DATASET_PATH)

    missing = [c for c in FEATURE_COLUMNS if c not in df.columns]
    if missing:
        raise SystemExit(f"Dataset is missing required columns: {missing}")

    df = df.dropna(subset=FEATURE_COLUMNS + ["placement_status"])

    X = df[FEATURE_COLUMNS].copy()  #features/inputs
    y = (df["placement_status"].str.strip().str.lower() == "placed").astype(int) #target/label

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    rf = RandomForestClassifier(n_estimators=300) #model creation
    rf.fit(X_train_s, y_train) #training the model

    # log_reg = LogisticRegression(max_iter=1000, class_weight="balanced")
    # log_reg.fit(X_train_s, y_train)

    model = rf  #change to log_reg to use Logistic Regression

    y_pred = model.predict(X_test_s)  #prediction part
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)

    print("Model Evaluation (RandomForestClassifier)")
    print(f"Accuracy : {acc:.3f}")
    print(f"Precision: {prec:.3f}")
    print(f"Recall   : {rec:.3f}")
    print(f"F1-score : {f1:.3f}")
    print("Confusion Matrix:")
    print(cm)

    importances = sorted(zip(FEATURE_COLUMNS, model.feature_importances_), key=lambda x: -x[1])
    print("\nFeature importances:")
    for name, imp in importances:
        print(f"  {name:28s} {imp:.3f}")

    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    joblib.dump({
        "feature_columns": FEATURE_COLUMNS,
        "model_name": type(model).__name__,
        "accuracy": acc,
    }, META_PATH)

    print(f"\nSaved model  -> {MODEL_PATH}")
    print(f"Saved scaler -> {SCALER_PATH}")
    print(f"Saved meta   -> {META_PATH}")


if __name__ == "__main__":
    main()
