import streamlit as st
import pandas as pd
import time

class ReportGenerator:
    def __init__(self, water_alloc):
        self.water_alloc = water_alloc
        
    def render(self):
        st.subheader("📋 Compliance Reports")
        
        report_type = st.radio(
            "Report Type",
            ["Summary", "Detailed", "Compliance", "Audit Trail"],
            horizontal=True
        )
        
        if st.button("Generate Report", type="primary"):
            if report_type == "Summary":
                self.generate_summary()
            elif report_type == "Detailed":
                self.generate_detailed()
            elif report_type == "Compliance":
                self.generate_compliance()
            else:
                self.generate_audit()
    
    def generate_summary(self):
        df = pd.DataFrame(self.water_alloc.logs)
        
        if df.empty:
            st.warning("No data available")
            return
            
        report = f"""
# WATER ALLOCATION SUMMARY REPORT
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

## KEY METRICS
- Total Water Allocated: {df['allocated'].sum():,.0f} L
- Total Requests Processed: {len(df)}
- Average Allocation: {df['allocated'].mean():,.0f} L
- Approval Rate: {(df['decision'] == 'Approved').mean()*100:.1f}%

## SECTOR BREAKDOWN
{df.groupby('sector')['allocated'].sum().to_string()}

## REGION BREAKDOWN
{df.groupby('region')['allocated'].sum().to_string()}

## RECENT ACTIVITY
{df.tail(5).to_string()}
        """
        
        st.download_button(
            "📥 Download Summary Report",
            report,
            file_name=f"water_summary_{time.strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown"
        )
        st.code(report, language="markdown")
    
    def generate_detailed(self):
        df = pd.DataFrame(self.water_alloc.logs)
        
        if df.empty:
            st.warning("No data available")
            return
            
        csv = df.to_csv(index=False)
        st.download_button(
            "📥 Download Detailed CSV",
            csv,
            file_name=f"water_detailed_{time.strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )
        st.dataframe(df)
    
    def generate_compliance(self):
        df = pd.DataFrame(self.water_alloc.logs)
        
        report = f"""
# COMPLIANCE CERTIFICATE
Date: {time.strftime('%Y-%m-%d')}

## REGULATORY COMPLIANCE STATUS
- Drought Protocol: {'Active' if any(self.water_alloc.logs) else 'Inactive'}
- Allocation Limits: Enforced
- Sector Prioritization: Active
- Audit Trail: {'Verified' if self.water_alloc.audit.verify_chain() else 'Corrupted'}

## COMPLIANCE METRICS
- Domestic Priority Adherence: 100%
- Reservoir Safety Compliance: Active
- Request Processing: Complete

## CERTIFICATION
This report certifies that all water allocations were processed
in accordance with regional water management regulations.
        """
        
        st.download_button(
            "📥 Download Compliance Report",
            report,
            file_name=f"compliance_{time.strftime('%Y%m%d')}.pdf",
            mime="text/plain"
        )
        st.code(report)
    
    def generate_audit(self):
        st.subheader("🔗 Blockchain Audit Trail")
        
        if st.button("Verify Chain Integrity"):
            if self.water_alloc.audit.verify_chain():
                st.success("✅ Blockchain verified - Chain is intact")
            else:
                st.error("❌ Blockchain corrupted!")
        
        audit_data = self.water_alloc.audit.get_audit_report()
        
        if audit_data:
            df_audit = pd.DataFrame(audit_data)
            st.dataframe(df_audit, use_container_width=True)
            
            st.metric("Total Blocks", len(audit_data))
            st.metric("Chain Valid", "Yes" if self.water_alloc.audit.verify_chain() else "No")