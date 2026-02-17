import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

class Analytics:
    def __init__(self, water_alloc):
        self.water_alloc = water_alloc
        
    def get_dataframe(self):
        if not self.water_alloc.logs:
            return pd.DataFrame()
        return pd.DataFrame(self.water_alloc.logs)
    
    def forecast_demand(self, cycles_ahead=2):
        df = self.get_dataframe()
        if len(df) < 3:
            return {}
            
        predictions = {}
        for region in df['region'].unique():
            region_data = df[df['region'] == region].groupby('cycle')['allocated'].sum()
            if len(region_data) > 1:
                X = np.array(region_data.index).reshape(-1, 1)
                y = region_data.values
                model = LinearRegression()
                model.fit(X, y)
                next_cycle = max(region_data.index) + cycles_ahead
                predictions[region] = max(0, model.predict([[next_cycle]])[0])
        return predictions
    
    def detect_anomalies(self, threshold=2.5):
        df = self.get_dataframe()
        if len(df) < 5:
            return pd.DataFrame()
            
        anomalies = []
        for sector in df['sector'].unique():
            sector_data = df[df['sector'] == sector]['allocated']
            if len(sector_data) > 2:
                mean = sector_data.mean()
                std = sector_data.std()
                if std > 0:
                    sector_anomalies = df[
                        (df['sector'] == sector) & 
                        (np.abs(df['allocated'] - mean) > threshold * std)
                    ]
                    if not sector_anomalies.empty:
                        anomalies.append(sector_anomalies)
        
        return pd.concat(anomalies) if anomalies else pd.DataFrame()
    
    def get_statistics(self):
        df = self.get_dataframe()
        if df.empty:
            return {}
            
        return {
            'total_allocated': df['allocated'].sum(),
            'avg_allocation': df['allocated'].mean(),
            'total_requests': len(df),
            'approval_rate': (df['decision'] == 'Approved').mean() * 100,
            'sector_breakdown': df.groupby('sector')['allocated'].sum().to_dict(),
            'region_breakdown': df.groupby('region')['allocated'].sum().to_dict()
        }