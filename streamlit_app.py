# streamlit_app.py
import streamlit as st
import serial
import serial.tools.list_ports
import time
import joblib
import pandas as pd

st.set_page_config(page_title="Hydroponics Fertilizer Calculator", layout="wide")

# Load ML Model & Dataset
@st.cache_resource
def load_model():
    return joblib.load("models/npk_model.pkl")

@st.cache_data
def load_data():
    df = pd.read_csv("data/hydro_data.csv")
    df.columns = ["plant", "stage", "temperature", "humidity", "light_lux", "age_days", "N", "P", "K"]
    return df

model = load_model()
data_df = load_data()

# Serial Port Handling
def get_serial_ports():
    return [p.device for p in serial.tools.list_ports.comports()]

# Session State
if "ser" not in st.session_state:
    st.session_state.ser = None
if "serial_ready" not in st.session_state:
    st.session_state.serial_ready = False
if "loop_counter" not in st.session_state:
    st.session_state.loop_counter = 0

def open_serial(port):
    if st.session_state.ser is None:
        try:
            st.session_state.ser = serial.Serial(port, 9600, timeout=1)
            time.sleep(2)
            st.session_state.serial_ready = True
            return True
        except:
            st.session_state.serial_ready = False
            return False
    return st.session_state.serial_ready

# Sidebar Settings
with st.sidebar:
    st.title("Settings")
    
    ports = get_serial_ports()
    if not ports:
        st.error("No serial ports found")
        st.stop()
    
    port = st.selectbox("Arduino Port", ports)
    
    plant = st.selectbox("Plant Type", sorted(data_df["plant"].unique()))
    
    stages = sorted(data_df[data_df["plant"] == plant]["stage"].unique())
    stage = st.selectbox("Growth Stage", stages)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        water_amount = st.number_input("Water Level in Tank", min_value=0.1, max_value=100000.0, value=10.0, step=0.1)
    with col2:
        water_unit = st.selectbox("Unit", ["L", "mL"], index=0)
    
    # Convert to liters
    if water_unit == "mL":
        water_level = water_amount / 1000.0
    else:
        water_level = water_amount
    
    st.markdown("---")
    st.caption("Using NPK 19-19-19 fertilizer")

# Parse Arduino Data
def parse_arduino_block(block):
    data = {}
    try:
        for line in block.split("\n"):
            line = line.strip()
            if line.startswith("TDS:"):
                data["tds"] = float(line.split(":")[1].replace("ppm", "").strip())
            elif line.startswith("pH:"):
                data["ph"] = float(line.split(":")[1].strip())
            elif line.startswith("Water Level:"):
                data["water_level"] = float(line.split(":")[1].strip())
            elif line.startswith("Light:"):
                data["light"] = float(line.split(":")[1].strip())
            elif line.startswith("Temperature:"):
                data["temperature"] = float(line.split(":")[1].strip())
        return data if len(data) == 5 else None
    except:
        return None

# Read Serial
def read_serial():
    if not open_serial(port):
        return None
    try:
        raw = ""
        for _ in range(6):
            raw += st.session_state.ser.readline().decode(errors="ignore")
        return parse_arduino_block(raw)
    except:
        return None

# Custom CSS for modern look
st.markdown("""
    <style>
    .main-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
    }
    .fertilizer-amount {
        font-size: 4rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    .tank-info {
        font-size: 1.5rem;
        opacity: 0.9;
        margin-top: 1rem;
    }
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.5rem;
        font-weight: 600;
    }
    .status-good {
        background-color: #10b981;
    }
    .status-warning {
        background-color: #f59e0b;
    }
    .notification {
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        display: flex;
        align-items: center;
        gap: 1rem;
        font-weight: 500;
    }
    .notification-success {
        background-color: #d1fae5;
        color: #065f46;
        border-left: 4px solid #10b981;
    }
    .notification-warning {
        background-color: #fef3c7;
        color: #92400e;
        border-left: 4px solid #f59e0b;
    }
    .notification-info {
        background-color: #dbeafe;
        color: #1e40af;
        border-left: 4px solid #3b82f6;
    }
    </style>
""", unsafe_allow_html=True)

# Main UI
st.title("Hydroponics Monitor")

# Placeholders
main_placeholder = st.empty()
notification_placeholder = st.empty()
advanced_placeholder = st.empty()

# Main Loop
while True:
    sensor_data = read_serial()
    
    if sensor_data:
        # Get predicted NPK values
        df_input = pd.DataFrame([{
            "plant": plant,
            "stage": stage,
            "temperature": sensor_data["temperature"],
            "humidity": 65,  # Default if not measured
            "light_lux": sensor_data["light"],
            "age_days": 30  # Default age value
        }])
        
        pred_N, pred_P, pred_K = model.predict(df_input)[0]
        
        # Calculate current NPK from TDS (simple approximation)
        # Assuming TDS roughly represents total dissolved nutrients
        total_pred = pred_N + pred_P + pred_K
        current_N = (pred_N / total_pred) * sensor_data["tds"]
        current_P = (pred_P / total_pred) * sensor_data["tds"]
        current_K = (pred_K / total_pred) * sensor_data["tds"]
        
        # Calculate deficiencies
        deficit_N = max(0, pred_N - current_N)
        deficit_P = max(0, pred_P - current_P)
        deficit_K = max(0, pred_K - current_K)
        
        # Calculate fertilizer needed (NPK 19-19-19)
        # Each gram of fertilizer provides 190mg N, 190mg P, 190mg K per liter
        # Find the limiting nutrient
        grams_for_N = (deficit_N / 190) if deficit_N > 0 else 0
        grams_for_P = (deficit_P / 190) if deficit_P > 0 else 0
        grams_for_K = (deficit_K / 190) if deficit_K > 0 else 0
        
        # Use the maximum to ensure all needs are met
        grams_needed = max(grams_for_N, grams_for_P, grams_for_K)
        
        # Determine notifications
        notifications = []
        
        # pH notifications
        if sensor_data["ph"] < 5.5:
            notifications.append(("warning", "pH is too low. Add pH Up solution to raise acidity."))
        elif sensor_data["ph"] > 7.0:
            notifications.append(("warning", "pH is too high. Add pH Down solution to lower acidity."))
        
        # TDS notifications
        if sensor_data["tds"] < 200:
            notifications.append(("warning", "Nutrient concentration is low. Plants may not get enough food."))
        elif sensor_data["tds"] > 1100:
            notifications.append(("warning", "Nutrient concentration is too high. This may damage plant roots."))
        
        # Temperature notifications
        if sensor_data["temperature"] < 18:
            notifications.append(("info", "Temperature is below optimal range. Consider warming the environment."))
        elif sensor_data["temperature"] > 28:
            notifications.append(("info", "Temperature is above optimal range. Consider cooling the environment."))
        
        # Fertilizer notifications
        if grams_needed >= 0.1:
            notifications.append(("info", f"Fertilizer needed: Add {grams_needed:.2f}g per liter of NPK 19-19-19."))
        
        # All good notification
        if not notifications:
            notifications.append(("success", "All parameters are within optimal range. System is healthy."))
        
        # Display Main Card
        with main_placeholder.container():
            if grams_needed < 0.1:
                st.markdown(f"""
                    <div class="main-card">
                        <h2>System Status</h2>
                        <div class="fertilizer-amount">All Good</div>
                        <p style="font-size: 1.2rem;">No fertilizer needed</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                total_grams = grams_needed * water_level
                # Display in the unit the user selected
                display_amount = water_amount
                display_unit = water_unit
                
                st.markdown(f"""
                    <div class="main-card">
                        <h2>Add Fertilizer</h2>
                        <div class="fertilizer-amount">{total_grams:.2f}g</div>
                        <p style="font-size: 1.2rem;">NPK 19-19-19 for {display_amount:.1f}{display_unit} tank</p>
                        <div class="tank-info">{grams_needed:.2f}g per liter</div>
                    </div>
                """, unsafe_allow_html=True)
            
            # Status badges
            ph_status = "good" if 5.5 <= sensor_data["ph"] <= 7.0 else "warning"
            ph_text = "pH Good" if ph_status == "good" else ("pH Too Low" if sensor_data["ph"] < 5.5 else "pH Too High")
            
            tds_status = "good" if 200 <= sensor_data["tds"] <= 1100 else "warning"
            tds_text = "Nutrients Good" if tds_status == "good" else ("Nutrients Low" if sensor_data["tds"] < 200 else "Nutrients High")
            
            st.markdown(f"""
                <div style="text-align: center; margin: 2rem 0;">
                    <span class="status-badge status-{ph_status}">{ph_text}</span>
                    <span class="status-badge status-{tds_status}">{tds_text}</span>
                </div>
            """, unsafe_allow_html=True)
        
        # Display Notifications
        with notification_placeholder.container():
            for notif_type, notif_message in notifications:
                st.markdown(f"""
                    <div class="notification notification-{notif_type}">
                        <span>{'✓' if notif_type == 'success' else '⚠' if notif_type == 'warning' else 'ℹ'}</span>
                        <span>{notif_message}</span>
                    </div>
                """, unsafe_allow_html=True)
        
        # Advanced Details (Collapsible)
        with advanced_placeholder.container():
            with st.expander("Advanced Details"):
                st.markdown("### Sensor Readings")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Temperature", f"{sensor_data['temperature']:.1f} °C")
                col2.metric("pH", f"{sensor_data['ph']:.1f}")
                col3.metric("TDS", f"{sensor_data['tds']:.0f} ppm")
                col4.metric("Light", f"{sensor_data['light']:.0f} lux")
                
                st.markdown("---")
                st.markdown("### NPK Analysis")
                
                # Show what this will provide
                will_provide_N = grams_needed * 190
                will_provide_P = grams_needed * 190
                will_provide_K = grams_needed * 190
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Nitrogen (N)", f"{current_N:.0f} mg/L", f"Target: {pred_N:.0f}")
                col2.metric("Phosphorus (P)", f"{current_P:.0f} mg/L", f"Target: {pred_P:.0f}")
                col3.metric("Potassium (K)", f"{current_K:.0f} mg/L", f"Target: {pred_K:.0f}")
                
                if grams_needed >= 0.1:
                    st.markdown("---")
                    st.markdown("### Fertilizer Addition Impact")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("N Addition", f"+{will_provide_N:.0f} mg/L")
                    col2.metric("P Addition", f"+{will_provide_P:.0f} mg/L")
                    col3.metric("K Addition", f"+{will_provide_K:.0f} mg/L")
                
                st.markdown("---")
                st.markdown("### Deficiencies")
                col1, col2, col3 = st.columns(3)
                col1.metric("N Deficit", f"{deficit_N:.0f} mg/L")
                col2.metric("P Deficit", f"{deficit_P:.0f} mg/L")
                col3.metric("K Deficit", f"{deficit_K:.0f} mg/L")
    
    else:
        with main_placeholder.container():
            st.error("Unable to read sensor data. Check Arduino connection.")
    
    time.sleep(1)# streamlit_app.py