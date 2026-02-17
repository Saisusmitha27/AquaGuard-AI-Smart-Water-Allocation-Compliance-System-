import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

class Dashboard:
    def __init__(self, analytics, water_alloc):
        self.analytics = analytics
        self.water_alloc = water_alloc
        
    def render(self, drought_mode):
        df = self.analytics.get_dataframe()
        
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Trends", "🗺️ Regions", "🔍 Anomalies"])
        
        with tab1:
            self.render_overview(df, drought_mode)
        
        with tab2:
            self.render_trends(df)
            
        with tab3:
            self.render_regions(df)
            
        with tab4:
            self.render_anomalies()
    
    def render_overview(self, df, drought_mode):
        if df.empty:
            st.info("No data available yet")
            return
            
        stats = self.analytics.get_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Water", f"{stats['total_allocated']:,.0f} L", 
                     delta="Drought" if drought_mode else "Normal")
        with col2:
            st.metric("Active Regions", stats['region_breakdown'].__len__())
        with col3:
            st.metric("Approval Rate", f"{stats['approval_rate']:.1f}%")
        with col4:
            st.metric("Total Requests", stats['total_requests'])
        
        col_left, col_right = st.columns(2)
        with col_left:
            fig = px.pie(
                values=list(stats['sector_breakdown'].values()),
                names=list(stats['sector_breakdown'].keys()),
                title="Allocation by Sector"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col_right:
            fig = px.bar(
                x=list(stats['region_breakdown'].keys()),
                y=list(stats['region_breakdown'].values()),
                title="Allocation by Region",
                labels={'x': 'Region', 'y': 'Liters'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def render_trends(self, df):
        if df.empty:
            st.info("No trend data available")
            return
            
        df['time_str'] = pd.to_datetime(df['timestamp'], unit='s')
        time_df = df.groupby('time_str')['allocated'].sum().reset_index()
        
        fig = px.line(
            time_df, 
            x='time_str', 
            y='allocated',
            title="Allocation Trends Over Time",
            labels={'allocated': 'Liters', 'time_str': 'Time'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        forecasts = self.analytics.forecast_demand()
        if forecasts:
            st.subheader("📈 Demand Forecast")
            for region, forecast in forecasts.items():
                st.metric(f"Region {region} Forecast", f"{forecast:,.0f} L")
    
    def render_regions(self, df):
        if df.empty:
            st.info("No region data available")
            return
            
        from config import RESERVOIR_LEVELS
        
        for region in df['region'].unique():
            with st.expander(f"Region {region} Details"):
                region_data = df[df['region'] == region]
                level = RESERVOIR_LEVELS.get(region, 100)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Reservoir Level", f"{level}%")
                    st.metric("Total Used", f"{region_data['allocated'].sum():,.0f} L")
                with col2:
                    st.metric("Requests", len(region_data))
                    st.metric("Avg Allocation", f"{region_data['allocated'].mean():,.0f} L")
                
                fig = px.pie(
                    values=region_data.groupby('sector')['allocated'].sum().values,
                    names=region_data.groupby('sector')['allocated'].sum().index,
                    title=f"Region {region} Sector Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    def render_anomalies(self):
        anomalies = self.analytics.detect_anomalies()
        if anomalies.empty:
            st.success("✅ No anomalies detected")
        else:
            st.warning(f"⚠️ {len(anomalies)} anomalies detected")
            st.dataframe(
                anomalies[['timestamp', 'region', 'sector', 'allocated', 'decision']]
                .assign(timestamp=lambda x: pd.to_datetime(x['timestamp'], unit='s'))
            )