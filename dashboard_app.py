import streamlit as st
import pandas as pd
import numpy as np
import time

# ==========================================
# DASHBOARD PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Real-Time Patient Data Dashboard",
    page_icon="🏥",
    layout="wide" 
)

st.title("🏥 Real-Time Patient Data & Outcomes Dashboard")
st.markdown(
    "Consolidating fragmented hospital metrics to isolate operational bottlenecks, "
    "track treatment effectiveness, and monitor patient recovery trends in real time."
)

# Initialize tracking variables safely
if "update_tick" not in st.session_state:
    st.session_state.update_tick = 0

# Sidebar configuration layout
st.sidebar.header("🕹️ Dashboard Control Center")
auto_refresh = st.sidebar.checkbox("Enable Real-Time Data Streaming", value=False)
department_filter = st.sidebar.selectbox(
    "Filter View by Department",
    options=["All Departments", "Emergency Room (ER)", "Intensive Care (ICU)", "General Ward", "Outpatient Clinic"]
)

# ==========================================
# MOCK REAL-TIME DATA STREAM GENERATOR
# ==========================================
def generate_live_patient_data():
    np.random.seed(42 + st.session_state.update_tick) 
    departments = ["Emergency Room (ER)", "Intensive Care (ICU)", "General Ward", "Outpatient Clinic"]
    genders = ["Male", "Female", "Other"]
    
    records = []
    for i in range(150):
        records.append({
            "Patient_ID": f"PT-{1000 + i}",
            "Department": np.random.choice(departments),
            "Age": np.random.randint(18, 90),
            "Gender": np.random.choice(genders),
            "Treatment_Effectiveness_Rate": np.random.uniform(75.0, 98.5),
            "Recovery_Time_Days": np.random.randint(2, 21),
            "Discharge_Status": np.random.choice(["Fully Recovered", "Discharged Home", "Transferred"], p=[0.6, 0.3, 0.1])
        })
    return pd.DataFrame(records)

# Load current snapshot array
raw_data = generate_live_patient_data()

if department_filter != "All Departments":
    filtered_data = raw_data[raw_data["Department"] == department_filter]
else:
    filtered_data = raw_data

# ==========================================
# ROW 1: KEY PERFORMANCE INDICATORS (KPIs)
# ==========================================
st.markdown("### 📊 Active Patient Care & Outcome Metrics")
kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

avg_effectiveness = filtered_data["Treatment_Effectiveness_Rate"].mean()
avg_recovery = filtered_data["Recovery_Time_Days"].mean()
active_patients = len(filtered_data)
bottleneck_count = int(filtered_data[filtered_data["Recovery_Time_Days"] > 14].shape[0])

kpi_col1.metric(
    label="Total Monitored Patients", 
    value=f"{active_patients}", 
    delta=f"+{np.random.randint(1, 5)} vs last hour"
)
kpi_col2.metric(
    label="Avg Treatment Effectiveness", 
    value=f"{avg_effectiveness:.1f}%", 
    delta=f"+{(np.random.uniform(-0.5, 0.8)):.2f}%"
)
kpi_col3.metric(
    label="Avg Recovery Timeline", 
    value=f"{avg_recovery:.1f} Days", 
    delta=f"{(np.random.uniform(-0.4, 0.2)):.1f} Days"
)
kpi_col4.metric(
    label="Flagged Care Bottlenecks", 
    value=f"{bottleneck_count}", 
    delta=f"{np.random.randint(-2, 3)} patients"
)

st.markdown("---")

# ==========================================
# ROW 2: CHARTS
# ==========================================
graph_col1, graph_col2 = st.columns(2)

with graph_col1:
    st.markdown("#### ⏳ Distribution of Recovery Times by Patient Age")
    chart_data = filtered_data.sort_values("Age").set_index("Age")[["Recovery_Time_Days"]]
    st.area_chart(chart_data)

with graph_col2:
    st.markdown("#### 🔬 Avg Treatment Effectiveness by Department")
    dept_effectiveness = filtered_data.groupby("Department")["Treatment_Effectiveness_Rate"].mean()
    st.bar_chart(dept_effectiveness)

st.markdown("---")

# ==========================================
# ROW 3: DATAFRAME MATRIX VIEW
# ==========================================
st.markdown("### 📋 Active Patient Outcomes Registry")
# Removed advanced column_config features to maintain maximum backwards compatibility
st.dataframe(filtered_data, use_container_width=True)

# ==========================================
# UNIVERSAL BACKWARDS COMPATIBLE RERUN LOOP
# ==========================================
if auto_refresh:
    time.sleep(2) 
    st.session_state.update_tick += 1
    
    # Safely switches between new and old fallback execution commands
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()