import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from config import RESERVOIR_LEVELS, TOTAL_SUPPLIES

class ScenarioSimulator:
    def __init__(self, water_alloc):
        self.water_alloc = water_alloc
        self.simulation_results = None  # Store results between renders
        self.last_params = None  # Store last simulation parameters
        
    def render(self):
        st.subheader("🎯 Scenario Planning & Simulation")
        
        # Create the form
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
            
            # Use form_submit_button instead of button
            submitted = st.form_submit_button("🚀 Run Simulation", use_container_width=True)
            
            if submitted:
                # Store results in session state instead of displaying immediately
                self.last_params = {
                    'drought': sim_drought,
                    'rainfall': sim_rainfall,
                    'temp': sim_temp,
                    'pop_growth': sim_pop_growth,
                    'industrial': sim_industrial,
                    'agricultural': sim_agricultural,
                    'cycles': sim_cycles
                }
                st.session_state['simulation_results'] = self.run_simulation(
                    sim_drought, sim_rainfall, sim_temp,
                    sim_pop_growth, sim_industrial, sim_agricultural,
                    sim_cycles
                )
                st.session_state['show_simulation'] = True
                st.rerun()
        
        # Display simulation results OUTSIDE the form
        if st.session_state.get('show_simulation', False) and st.session_state.get('simulation_results') is not None:
            self.display_simulation_results(st.session_state['simulation_results'])
    
    def run_simulation(self, drought, rainfall, temp, pop_growth, industrial, agricultural, cycles):
        """Run simulation and return results without displaying"""
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
        
        return {
            'dataframe': pd.DataFrame(results),
            'drought': drought,
            'rainfall': rainfall,
            'pop_growth': pop_growth
        }
    
    def display_simulation_results(self, results):
        """Display simulation results with Apply button"""
        df_results = results['dataframe']
        drought = results['drought']
        rainfall = results['rainfall']
        pop_growth = results['pop_growth']
        
        st.subheader("Simulation Results")
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Final Reservoir Level", f"{df_results['region_1_level'].iloc[-1]:.1f}%", 
                     f"{df_results['region_1_level'].iloc[-1] - df_results['region_1_level'].iloc[0]:.1f}%")
        with col2:
            st.metric("Total Allocated", f"{df_results['region_1_allocation'].sum():,.0f} L")
        with col3:
            st.metric("Weeks Simulated", len(df_results))
        
        # Create visualizations
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
        
        # Summary
        summary = f"""
### Simulation Summary
- **Scenario**: {'Drought' if drought else 'Normal'} Conditions
- **Rainfall Reduction**: {rainfall}%
- **Population Growth**: {pop_growth}%

**Recommendation**: {'Implement conservation measures' if drought else 'Normal operations continue'}
        """
        st.markdown(summary)
        
        # Apply button - This is now OUTSIDE any form
        if st.button("✅ Apply This Scenario to Main System", key="apply_scenario", use_container_width=True):
            st.session_state.drought_mode = drought
            st.success(f"✅ Scenario applied to main system! Drought mode is now {'ON' if drought else 'OFF'}")
            # Clear simulation results after applying
            st.session_state['show_simulation'] = False
            st.session_state['simulation_results'] = None
            st.rerun()
        
        # Clear button
        if st.button("🔄 Clear Results", key="clear_simulation", use_container_width=True):
            st.session_state['show_simulation'] = False
            st.session_state['simulation_results'] = None
            st.rerun()
