import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from config import RESERVOIR_LEVELS, TOTAL_SUPPLIES

class ScenarioSimulator:
    def __init__(self, water_alloc):
        self.water_alloc = water_alloc
        
    def render(self):
        st.subheader("🎯 Scenario Planning & Simulation")
        
        with st.form("scenario_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Climate Conditions")
                sim_drought = st.checkbox("Enable Drought Conditions")
                sim_rainfall = st.slider("Rainfall Reduction %", 0, 100, 20)
                sim_temp = st.slider("Temperature Increase °C", 0, 5, 2)
                
            with col2:
                st.markdown("### Demand Factors")
                sim_pop_growth = st.slider("Population Growth %", -20, 50, 10)
                sim_industrial = st.slider("Industrial Growth %", -20, 50, 15)
                sim_agricultural = st.slider("Agricultural Change %", -30, 30, 0)
            
            sim_cycles = st.slider("Simulation Cycles (Weeks)", 1, 12, 4)
            
            if st.form_submit_button("🚀 Run Simulation", use_container_width=True):
                self.run_simulation(
                    sim_drought, sim_rainfall, sim_temp,
                    sim_pop_growth, sim_industrial, sim_agricultural,
                    sim_cycles
                )
    
    def run_simulation(self, drought, rainfall, temp, pop_growth, industrial, agricultural, cycles):
        st.subheader("Simulation Results")
        
        results = []
        current_levels = RESERVOIR_LEVELS.copy()
        current_supply = TOTAL_SUPPLIES.copy()
        
        for cycle in range(1, cycles + 1):
            cycle_results = {'cycle': cycle}
            
            for region in [1, 2]:
                if drought:
                    current_levels[region] = max(10, current_levels[region] - rainfall/10)
                    current_supply[region] = current_supply[region] * (1 - rainfall/100)
                
                base_demand = 100000 * (1 + pop_growth/100)
                
                if current_levels[region] < 30:
                    allocation = base_demand * 0.5
                elif current_levels[region] < 50:
                    allocation = base_demand * 0.75
                else:
                    allocation = base_demand
                
                cycle_results[f'region_{region}_level'] = current_levels[region]
                cycle_results[f'region_{region}_allocation'] = allocation
                cycle_results[f'region_{region}_supply'] = current_supply[region]
            
            results.append(cycle_results)
        
        df_results = pd.DataFrame(results)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Final Reservoir Level", f"{df_results['region_1_level'].iloc[-1]:.1f}%", 
                     f"{df_results['region_1_level'].iloc[-1] - df_results['region_1_level'].iloc[0]:.1f}%")
        with col2:
            st.metric("Total Allocated", f"{df_results['region_1_allocation'].sum():,.0f} L")
        with col3:
            st.metric("Weeks Simulated", cycles)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_results['cycle'],
            y=df_results['region_1_level'],
            mode='lines+markers',
            name='Region 1 Level'
        ))
        fig.add_trace(go.Scatter(
            x=df_results['cycle'],
            y=df_results['region_2_level'],
            mode='lines+markers',
            name='Region 2 Level'
        ))
        fig.update_layout(
            title="Reservoir Levels Over Time",
            xaxis_title="Cycle",
            yaxis_title="Level %"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=df_results['cycle'],
            y=df_results['region_1_allocation'],
            name='Region 1',
            marker_color='blue'
        ))
        fig2.add_trace(go.Bar(
            x=df_results['cycle'],
            y=df_results['region_2_allocation'],
            name='Region 2',
            marker_color='green'
        ))
        fig2.update_layout(
            title="Projected Allocations by Region",
            xaxis_title="Cycle",
            yaxis_title="Liters",
            barmode='group'
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        summary = f"""
### Simulation Summary
- **Scenario**: {'Drought' if drought else 'Normal'} Conditions
- **Rainfall Reduction**: {rainfall}%
- **Population Growth**: {pop_growth}%
- **Industrial Growth**: {industrial}%
- **Agricultural Change**: {agricultural}%

**Recommendation**: {'Implement conservation measures' if drought else 'Normal operations continue'}
        """
        st.markdown(summary)
        
        if st.button("Apply This Scenario to Main System"):
            st.session_state.drought_mode = drought
            st.success("Scenario applied to main system!")