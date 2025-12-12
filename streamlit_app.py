import streamlit as st
import serial
import serial.tools.list_ports
import time
import joblib
import pandas as pd

# -----------------------------
# Load ML Model
# -----------------------------
model = joblib.load("models/npk_model.pkl")

# -----------------------------
# Serial Port Handling
# -----------------------------
def get_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [p.device for p in ports]

# -----------------------------
# Sidebar Inputs
# -----------------------------
with st.sidebar:
    st.title("Hydroponics Settings")
    available_ports = get_serial_ports()
    port = st.selectbox("Select Arduino Port", available_ports, key="port_select")
    plant = st.selectbox("Plant Type", [
        "Tomato", "Cucumber", "Lettuce", "Spinach", "Sprouts",
        "Chilli", "Capsicum", "Beans", "Peas",
        "Coriander", "Mint", "Onion", "Garlic", "Radish"
    ], key="plant_select")
    stage = st.selectbox("Growth Stage", [
        "Seedling", "Vegetative", "Flowering", "Fruiting",
        "Harvest", "Bulbing", "Rooting", "Early", "Mid", "Ready"
    ], key="stage_select")

    if st.button("🔄 Refresh Ports"):
        st.experimental_rerun()
    
    if st.button("🔌 Reconnect Arduino"):
        if "ser" in st.session_state:
            try: st.session_state.ser.close()
            except: pass
        st.session_state.serial_ready = False
        st.success("Attempting to reconnect Arduino...")

baud = 9600

# -----------------------------
# Initialize Serial in Session
# -----------------------------
if "serial_ready" not in st.session_state:
    st.session_state.serial_ready = False
if "ser" not in st.session_state:
    st.session_state.ser = None

def open_serial():
    if st.session_state.ser is None or not st.session_state.serial_ready:
        try:
            st.session_state.ser = serial.Serial(port, baud, timeout=1)
            time.sleep(2)  # Arduino reset
            st.session_state.serial_ready = True
        except:
            st.session_state.serial_ready = False

# -----------------------------
# Parse Arduino Data
# -----------------------------
def parse_arduino_block(block: str):
    lines = block.split("\n")
    data = {}
    for line in lines:
        line = line.strip()
        if line.startswith("TDS:"):
            data["TDS"] = float(line.split(":")[1].replace("ppm", "").strip())
        elif line.startswith("pH:"):
            data["pH"] = float(line.split(":")[1].strip())
        elif line.startswith("Water Level:"):
            data["water_level"] = float(line.split(":")[1].strip())
        elif line.startswith("Light:"):
            data["light"] = float(line.split(":")[1].strip())
        elif line.startswith("Temperature:"):
            data["temperature"] = float(line.split(":")[1].strip())
    return data if len(data.keys()) == 5 else None

# -----------------------------
# Read Serial (Keep Port Open)
# -----------------------------
def read_serial_block():
    open_serial()
    if not st.session_state.serial_ready:
        return None
    try:
        raw = ""
        for _ in range(8):
            line = st.session_state.ser.readline().decode(errors="ignore")
            raw += line
        return parse_arduino_block(raw)
    except:
        return None

# -----------------------------
# Placeholders
# -----------------------------
placeholder_sensors = st.empty()
placeholder_alerts = st.empty()
placeholder_comparison = st.empty()
placeholder_metrics = st.empty()

if "chart_data" not in st.session_state:
    st.session_state.chart_data = pd.DataFrame(columns=["time", "TDS", "pH", "Temp"])

st.write("📡 Real-time sensor updates every second...")

# -----------------------------
# MAIN LOOP
# -----------------------------
while True:
    real_data = read_serial_block()

    if real_data:
        # --- Sensor Table ---
        sensor_table = pd.DataFrame({
            "Metric": ["TDS (ppm)", "pH", "Water Level", "Light", "Temperature (°C)"],
            "Value": [
                real_data["TDS"],
                real_data["pH"],
                real_data["water_level"],
                real_data["light"],
                real_data["temperature"]
            ]
        })
        placeholder_sensors.dataframe(sensor_table, use_container_width=True)

        # --- Alerts ---
        alerts = []
        if real_data["pH"] > 7:
            alerts.append("⚠️ pH is too high! Add acid regulator.")
        elif real_data["pH"] < 5.5:
            alerts.append("⚠️ pH is too low! Add base regulator.")
        else:
            alerts.append("✓ pH is healthy.")

        if real_data["TDS"] < 200:
            alerts.append("⚠️ TDS is low — nutrients are insufficient.")
        elif real_data["TDS"] > 1100:
            alerts.append("⚠️ TDS is too high — dilute solution.")
        else:
            alerts.append("✓ TDS is within ideal range.")

        with placeholder_alerts.container():
            for alert in alerts:
                if "⚠️" in alert:
                    st.warning(alert)
                else:
                    st.success(alert)

        # --- Model Prediction ---
        df_in = pd.DataFrame([{
            "plant": plant,
            "stage": stage,
            "temperature": real_data["temperature"],
            "humidity": 60,
            "light_lux": real_data["light"],
            "age_days": 20
        }])
        pred_N, pred_P, pred_K = model.predict(df_in)[0]

        # --- Approx Real-Time NPK ---
        total_pred = pred_N + pred_P + pred_K
        rN = pred_N / total_pred
        rP = pred_P / total_pred
        rK = pred_K / total_pred

        approx_N = rN * real_data["TDS"]
        approx_P = rP * real_data["TDS"]
        approx_K = rK * real_data["TDS"]

        # --- Comparison Table ---
        comparison_table = pd.DataFrame({
            "Parameter": ["N", "P", "K"],
            "Predicted": [pred_N, pred_P, pred_K],
            "Real-Time (approx)": [approx_N, approx_P, approx_K],
            "Difference": [
                pred_N - approx_N,
                pred_P - approx_P,
                pred_K - approx_K
            ]
        })
        placeholder_comparison.dataframe(comparison_table, use_container_width=True)

        # --- Metric Cards ---
        tds_target = (pred_N + pred_P + pred_K) * 3
        tds_diff = tds_target - real_data["TDS"]

        with placeholder_metrics.container():
            c1, c2, c3 = st.columns(3)
            c1.metric("Current TDS", f"{real_data['TDS']:.2f} ppm")
            c2.metric("Ideal NPK", f"{pred_N:.1f} / {pred_P:.1f} / {pred_K:.1f}")
            c3.metric("TDS Difference", f"{tds_diff:.1f} ppm")

        # --- Update History ---
        st.session_state.chart_data = pd.concat([
            st.session_state.chart_data,
            pd.DataFrame([{
                "time": time.time(),
                "TDS": real_data["TDS"],
                "pH": real_data["pH"],
                "Temp": real_data["temperature"]
            }])
        ], ignore_index=True)
        st.session_state.chart_data = st.session_state.chart_data.tail(50)

    time.sleep(1)
