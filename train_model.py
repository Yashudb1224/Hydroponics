# train_model.py
import pandas as pd
import joblib
import os
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.pipeline import Pipeline

# Try different encodings
encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
df = None

for encoding in encodings:
    try:
        df = pd.read_csv("data/hydro_data.csv", encoding=encoding)
        print(f"✅ Successfully loaded with {encoding} encoding")
        break
    except UnicodeDecodeError:
        continue

if df is None:
    print("❌ Could not load CSV with any encoding. Please recreate the file.")
    exit(1)

# Rename columns if needed
if "Temperature (°C)" in df.columns:
    df.columns = ["plant", "stage", "temperature", "humidity", "light_lux", "age_days", "N", "P", "K"]

print(f"✅ Loaded dataset with {len(df)} rows")
print(f"Columns: {list(df.columns)}")

# Features and target
X = df[["plant", "stage", "temperature", "humidity", "light_lux", "age_days"]]
y = df[["N", "P", "K"]]

# Preprocessing
preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), ["plant", "stage"])
    ],
    remainder="passthrough"
)

# Model
model = Pipeline([
    ("pre", preprocessor),
    ("rf", MultiOutputRegressor(
        RandomForestRegressor(
            n_estimators=400,
            random_state=42,
            n_jobs=-1
        )
    ))
])

# Train
print("🔄 Training model...")
model.fit(X, y)

# Save model
os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/npk_model.pkl")

print("✅ Model saved: models/npk_model.pkl")

# Calculate and save NPK ratios
df["total"] = df["N"] + df["P"] + df["K"]
df["rN"] = df["N"] / df["total"]
df["rP"] = df["P"] / df["total"]
df["rK"] = df["K"] / df["total"]

ratios = (
    df.groupby(["plant", "stage"])[["rN", "rP", "rK"]]
    .mean()
    .reset_index()
)

ratios.to_csv("models/npk_ratios.csv", index=False, encoding='utf-8')
print("✅ Ratios saved: models/npk_ratios.csv")