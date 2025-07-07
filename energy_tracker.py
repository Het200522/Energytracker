import streamlit as st
import pandas as pd
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="Energy Consumption Tracker",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .energy-tip {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .stButton>button {
        background: linear-gradient(45deg, #FE6B8B 30%, #FF8E53 90%);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for tracking
if 'daily_consumption' not in st.session_state:
    st.session_state.daily_consumption = []

if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {}

def calculate_base_energy(facility_type):
    """Calculate base energy consumption based on facility type"""
    energy_map = {
        "1bhk": 2 * 0.4 + 2 * 0.8,  # 2.4 kWh
        "2bhk": 3 * 0.4 + 3 * 0.8,  # 3.6 kWh
        "3bhk": 4 * 0.4 + 4 * 0.8,  # 4.8 kWh
        "4bhk": 5 * 0.4 + 5 * 0.8   # 6.0 kWh
    }
    return energy_map.get(facility_type, 0)

def calculate_appliance_energy(appliances):
    """Calculate energy consumption for appliances"""
    appliance_consumption = {
        "AC": 3.0,
        "Refrigerator": 1.5,
        "Washing Machine": 2.0,
        "Dishwasher": 1.8,
        "Water Heater": 2.5,
        "Microwave": 1.2,
        "TV": 0.5,
        "Laptop": 0.3
    }
    
    total = 0
    for appliance in appliances:
        total += appliance_consumption.get(appliance, 0)
    return total

def get_energy_tips(total_consumption):
    """Get energy saving tips based on consumption"""
    if total_consumption > 10:
        return "🔴 High consumption! Consider using AC efficiently, LED bulbs, and unplugging unused devices."
    elif total_consumption > 6:
        return "🟡 Moderate consumption. Try using natural light during day and optimize appliance usage."
    else:
        return "🟢 Great! You're using energy efficiently. Keep up the good work!"

# App Header
st.markdown('<div class="main-header">⚡ Smart Energy Consumption Tracker</div>', unsafe_allow_html=True)

# Sidebar for user profile
st.sidebar.header("📋 User Profile")
with st.sidebar.form("user_profile_form"):
    name = st.text_input("👤 Full Name", value=st.session_state.user_profile.get('name', ''))
    age = st.number_input("🎂 Age", min_value=1, max_value=100, value=st.session_state.user_profile.get('age', 25))
    city = st.text_input("🏙️ City", value=st.session_state.user_profile.get('city', ''))
    area = st.text_input("📍 Area", value=st.session_state.user_profile.get('area', ''))
    
    st.subheader("🏠 Housing Details")
    flat_type = st.selectbox("🏢 Property Type", ["Flat", "Independent House", "Tenement"])
    facility = st.selectbox("🏠 Size", ["1bhk", "2bhk", "3bhk", "4bhk"])
    
    st.subheader("📱 Appliances")
    appliances = st.multiselect(
        "Select your appliances:",
        ["AC", "Refrigerator", "Washing Machine", "Dishwasher", "Water Heater", "Microwave", "TV", "Laptop"],
        default=st.session_state.user_profile.get('appliances', [])
    )
    
    submitted = st.form_submit_button("💾 Save Profile")
    
    if submitted:
        st.session_state.user_profile = {
            'name': name,
            'age': age,
            'city': city,
            'area': area,
            'flat_type': flat_type,
            'facility': facility,
            'appliances': appliances
        }
        st.success("✅ Profile saved successfully!")

# Main content area
if st.session_state.user_profile:
    profile = st.session_state.user_profile
    
    # Calculate energy consumption
    base_energy = calculate_base_energy(profile['facility'])
    appliance_energy = calculate_appliance_energy(profile['appliances'])
    total_energy = base_energy + appliance_energy
    
    # Display current consumption
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🏠 Base Consumption", f"{base_energy:.1f} kWh")
    
    with col2:
        st.metric("📱 Appliances", f"{appliance_energy:.1f} kWh")
    
    with col3:
        st.metric("⚡ Total Daily", f"{total_energy:.1f} kWh")
    
    with col4:
        monthly_cost = total_energy * 30 * 5  # Assuming ₹5 per kWh
        st.metric("💰 Monthly Cost", f"₹{monthly_cost:.0f}")
    
    # Energy saving tips
    tip = get_energy_tips(total_energy)
    st.markdown(f'<div class="energy-tip"><strong>💡 Energy Tip:</strong> {tip}</div>', unsafe_allow_html=True)
    
    # Daily tracking section
    st.subheader("📊 Daily Consumption Tracker")
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.subheader("📅 Log Today's Usage")
        today = st.date_input("Date", value=date.today())
        actual_consumption = st.number_input("Actual consumption (kWh)", min_value=0.0, value=total_energy, step=0.1)
        
        if st.button("➕ Add Entry"):
            entry = {
                'date': today,
                'estimated': total_energy,
                'actual': actual_consumption,
                'difference': actual_consumption - total_energy
            }
            st.session_state.daily_consumption.append(entry)
            st.success("✅ Entry added successfully!")
    
    with col1:
        if st.session_state.daily_consumption:
            df = pd.DataFrame(st.session_state.daily_consumption)
            
            # Create consumption chart
            fig = px.line(df, x='date', y=['estimated', 'actual'], 
                         title='Daily Energy Consumption Trend',
                         labels={'value': 'Energy (kWh)', 'date': 'Date'})
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Show recent entries
            st.subheader("📋 Recent Entries")
            recent_df = df.tail(10).sort_values('date', ascending=False)
            st.dataframe(recent_df, use_container_width=True)
            
            # Statistics
            if len(df) > 1:
                avg_consumption = df['actual'].mean()
                max_consumption = df['actual'].max()
                min_consumption = df['actual'].min()
                
                st.subheader("📈 Statistics")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Average Daily", f"{avg_consumption:.1f} kWh")
                with col2:
                    st.metric("Maximum Day", f"{max_consumption:.1f} kWh")
                with col3:
                    st.metric("Minimum Day", f"{min_consumption:.1f} kWh")
        else:
            st.info("👆 Add your first energy consumption entry to see the tracking chart!")
    
    # Appliance breakdown
    if profile['appliances']:
        st.subheader("🔌 Appliance Energy Breakdown")
        appliance_data = []
        for appliance in profile['appliances']:
            consumption = {
                "AC": 3.0, "Refrigerator": 1.5, "Washing Machine": 2.0,
                "Dishwasher": 1.8, "Water Heater": 2.5, "Microwave": 1.2,
                "TV": 0.5, "Laptop": 0.3
            }.get(appliance, 0)
            appliance_data.append({"Appliance": appliance, "Consumption": consumption})
        
        appliance_df = pd.DataFrame(appliance_data)
        fig_pie = px.pie(appliance_df, values='Consumption', names='Appliance',
                        title='Energy Consumption by Appliance')
        st.plotly_chart(fig_pie, use_container_width=True)

else:
    st.info("👈 Please fill in your profile in the sidebar to start tracking your energy consumption!")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; padding: 1rem;'>"
    "💡 Track your energy consumption daily to reduce costs and environmental impact!"
    "</div>", 
    unsafe_allow_html=True
)