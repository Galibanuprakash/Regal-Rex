import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Coupling Selector", layout="wide")
st.title("🔧 Coupling Selection App")

# --- Upload Excel File ---
uploaded_file = st.file_uploader("📤 Upload Coupling Data Excel File", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, skiprows=1)

        # Coupling type categories
        shaft_based = [
            "Marine Type", "REM design", "Coplanar design with Marine Hub",
            "Marine Type with Hydraulic Hub", "Coplaner design with Hydraulic hub (REM)",
            "REM Hydraulic Hub"
        ]
        flange_based = [
            "Adaptor Design", "Double adaptor Design", "Double Adaptor With Coplanar"
        ]
        all_types = shaft_based + flange_based + ["Yoke Design"]

        st.markdown("### 🔧 Select Coupling Configuration")

        # --- Driver Coupling Type ---
        driver_type = st.selectbox("Driver Coupling Type", all_types)
        if driver_type in shaft_based:
            driver_input = st.number_input("Driver End Shaft Diameter (mm)", min_value=0.0)
            driver_col = 'Driver End shaft dia'
        elif driver_type in flange_based:
            driver_input = st.number_input("Driver Side Flange PCD (mm)", min_value=0.0)
            driver_col = 'Driver side Flange size- PCD'
        else:
            driver_input = None
            driver_col = None

        # --- Driven Coupling Type ---
        driven_type = st.selectbox("Driven Coupling Type", all_types)
        if driven_type in shaft_based:
            driven_input = st.number_input("Driven End Shaft Diameter (mm)", min_value=0.0)
            driven_col = 'Driven End shaft dia'
        elif driven_type in flange_based:
            driven_input = st.number_input("Driven Side Flange PCD (mm)", min_value=0.0)
            driven_col = 'Driven side Flange size- PCD'
        else:
            driven_input = None
            driven_col = None

        # --- Power and Speed Inputs (Manual From-To) ---
        col1, col2 = st.columns(2)
        with col1:
            power_min = st.number_input("Power From (kW)", min_value=0.0, value=0.0)
            speed_min = st.number_input("Speed From (RPM)", min_value=0.0, value=0.0)
        with col2:
            power_max = st.number_input("Power To (kW)", min_value=0.0, value=1000.0)
            speed_max = st.number_input("Speed To (RPM)", min_value=0.0, value=10000.0)

        # DBSE
        dbse = st.number_input("DBSE/DBFF (mm)", min_value=0.0)

        if st.button("🔍 Find Matching Couplings"):
            filtered_df = df.copy()

            # Convert columns to numeric for filtering
            cols_to_convert = [
                'Driver End shaft dia', 'Driver side Flange size- PCD',
                'Driven End shaft dia', 'Driven side Flange size- PCD',
                'Power (kW)', 'Speed (RPM)', 'DBSE /DBFF (mm)'
            ]
            for col in cols_to_convert:
                filtered_df[col] = pd.to_numeric(filtered_df[col], errors='coerce')

            # Drop rows with missing critical fields
            filtered_df = filtered_df.dropna(subset=[
                'Power (kW)', 'Speed (RPM)', 'DBSE /DBFF (mm)',
                driver_col if driver_col else 'Power (kW)',
                driven_col if driven_col else 'Power (kW)'
            ])

            # Filter based on power and speed range
            filtered_df = filtered_df[
                (filtered_df['Power (kW)'].between(power_min, power_max)) &
                (filtered_df['Speed (RPM)'].between(speed_min, speed_max))
            ]

            # --- Calculate Match Score ---
            def calc_score(row):
                score = 0
                if driver_col:
                    score += abs(row.get(driver_col, 0) - driver_input)
                if driven_col:
                    score += abs(row.get(driven_col, 0) - driven_input)
                score += abs(row['DBSE /DBFF (mm)'] - dbse)
                return score

            filtered_df['Match Score'] = filtered_df.apply(calc_score, axis=1)

            # Sort and show all matching rows
            matching_df = filtered_df.sort_values(by='Match Score')

            if not matching_df.empty:
                st.success(f"✅ {len(matching_df)} Matching Couplings Found:")
                st.dataframe(matching_df.drop(columns=["Match Score"]).reset_index(drop=True), use_container_width=True)
            else:
                st.warning("❌ No matching couplings found.")

    except Exception as e:
        st.error(f"❗ Error processing file: {e}")
else:
    st.info("📁 Please upload an Excel file to begin.")
