import streamlit as st
from config import DROUGHT_THRESHOLD, RESERVOIR_SAFE_LEVEL, RESERVOIR_LEVELS

class AlertSystem:
    def __init__(self, water_alloc):
        self.water_alloc = water_alloc
        
    def check_alerts(self):
        alerts = []
        
        for region, level in RESERVOIR_LEVELS.items():
            if level < DROUGHT_THRESHOLD:
                alerts.append({
                    'severity': '🔴 CRITICAL',
                    'message': f'Region {region} in DROUGHT! Level: {level}%',
                    'action': 'Impose strict conservation measures'
                })
            elif level < RESERVOIR_SAFE_LEVEL:
                alerts.append({
                    'severity': '🟡 WARNING',
                    'message': f'Region {region} below safe level: {level}%',
                    'action': 'Consider voluntary conservation'
                })
        
        for log in self.water_alloc.logs[-5:]:
            if 'requested' in log and log.get('requested', 0) > log['allocated'] * 1.5:
                alerts.append({
                    'severity': '🔵 INFO',
                    'message': f'Large reduction in Region {log["region"]}',
                    'action': 'Check infrastructure capacity'
                })
        
        return alerts
    
    def render_sidebar(self):
        st.sidebar.header("🚨 Active Alerts")
        alerts = self.check_alerts()
        
        if not alerts:
            st.sidebar.success("✅ No active alerts")
        else:
            for alert in alerts[:3]:
                st.sidebar.markdown(f"{alert['severity']} **{alert['message']}**")
                st.sidebar.caption(f"Action: {alert['action']}")
                st.sidebar.divider()
            
            if len(alerts) > 3:
                st.sidebar.caption(f"... and {len(alerts) - 3} more alerts")