# train_model.py
import pandas as pd
import os
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
import joblib

os.makedirs("models", exist_ok=True)

# 1. Load
df = pd.read_csv(os.path.join("data", "hydro_data.csv"))

# 2. Features & target
X = df[["plant","stage","temperature","humidity","light_lux","age_days"]]
y = df[["N","P","K"]]

# 3. Preprocessing: one-hot plant+stage
cat_features = ["plant","stage"]
num_features = ["temperature","humidity","light_lux","age_days"]

preprocessor = ColumnTransformer([
    ("cat", OneHotEncoder(sparse_output=False, handle_unknown="ignore"), cat_features),
], remainder="passthrough")

# 4. Model pipeline
rf = RandomForestRegressor(n_estimators=200, random_state=42)
model = Pipeline([
    ("pre", preprocessor),
    ("reg", MultiOutputRegressor(rf))
])

# 5. Train-test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model.fit(X_train, y_train)

# 6. Save model
joblib.dump(model, os.path.join("models", "npk_model.pkl"))
print("Saved models/npk_model.pkl")

# 7. Compute average NPK ratios per (plant,stage)
df["total_NPK"] = df[["N","P","K"]].sum(axis=1)
df["rN"] = df["N"] / df["total_NPK"]
df["rP"] = df["P"] / df["total_NPK"]
df["rK"] = df["K"] / df["total_NPK"]

ratios = df.groupby(["plant","stage"])[["rN","rP","rK"]].mean().reset_index()
ratios.to_csv(os.path.join("models", "npk_ratios.csv"), index=False)
print("Saved models/npk_ratios.csv")
