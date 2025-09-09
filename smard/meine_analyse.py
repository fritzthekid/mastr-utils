import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
import sys
import logging

logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)

DEBUG = False

class MeineAnalyse:
    def __init__(self, csv_file_path):
        """Initialize with German SMARD data"""
        self.data = self.load_and_prepare_data(csv_file_path)

    def load_and_prepare_data(self, csv_file_path):
        """Load and prepare SMARD data"""
        print("Loading SMARD data for European grid analysis...")
        
        try:
            df = pd.read_csv(csv_file_path, sep=';', decimal=',')
            
            # Create datetime column
            df['DateTime'] = pd.to_datetime(df['Datum'] + ' ' + df['Uhrzeit'])
            df = df.set_index('DateTime')
            
            # Remove non-energy columns
            energy_cols = [col for col in df.columns if '[MWh]' in col]
            df = df[energy_cols]
            
            # Rename columns for easier handling
            column_mapping = {}
            for col in df.columns:
                if 'Wind Onshore' in col:
                    column_mapping[col] = 'wind_onshore'
                elif 'Wind Offshore' in col:
                    column_mapping[col] = 'wind_offshore'
                elif 'Photovoltaik' in col:
                    column_mapping[col] = 'solar'
                elif 'Wasserkraft' in col:
                    column_mapping[col] = 'hydro'
                elif 'Biomasse' in col:
                    column_mapping[col] = 'biomass'
                elif 'Gesamtverbrauch' in col or 'Netzlast' in col:
                    column_mapping[col] = 'total_demand'
                # Keep other columns with original names for now

            df = df.rename(columns=column_mapping)

            total_demand = df["total_demand"].sum() * 0.25
            my_total_demand = 1000*2804

            df["my_demand"] = df["total_demand"] * my_total_demand / total_demand
            df["my_wind"] = df["wind_onshore"] * 5000 / max(df["wind_onshore"])

            df = df.fillna(0)
            
            print(f"✓ Loaded {len(df)} hourly records")
            print(f"Date range: {df.index.min()} to {df.index.max()}")

            if DEBUG:
                plt.plot(df["my_wind"])
                plt.plot(df["my_demand"])
                plt.show()
            return df

        except Exception as e:
            print(f"Error loading data: {e}")
            return None

    def simulate_battery(self,capacity=10000, power=5000):
        container = []
        residual = []
        fillstand = capacity / 2
        for w,d in zip(self.data["my_wind"],self.data["my_demand"]):
            p = w-d
            diff = max(-power,min(power,p))
            if p > 0:
                fillstand = min(capacity, fillstand+diff)
                residual.append(0)
            else:
                if fillstand <= 0:
                    fillstand = 0
                    residual.append(fillstand+diff)
                else:
                    fillstand = fillstand+diff
                    residual.append(0)
            container.append(fillstand)
        self.data["battery"] = container
        self.data["residual"] = residual

    def run_analysis(self):
        """Run the analysis"""
        if self.data is None:
            print("❌ No data loaded!")
            return
        
        logger.warn("Starting analysis...")

        self.simulate_battery()
        self.print_results()
        self.visualise()

    def print_results(self):
        diff = self.data['my_wind']-self.data['my_demand']
        pos = [d for w,d in zip(self.data['my_wind'],self.data['my_demand']) if w>=d]
        neg = [d-w for w,d in zip(self.data['my_wind'],self.data['my_demand']) if w<d]
        print(f"share without battery {(1-sum(neg)/sum(pos)):.2f}")
        res = [-r for b,r in zip(self.data['battery'],self.data['residual']) if r < 0]
        print(f"share with battery: {(1-sum(res)/sum(pos)):.2f}")
        pass

    def visualise(self):        
        fig, [ax1, ax2, ax3, ax4] = plt.subplots(4, 1, sharex=True)
        ax1.plot(self.data.index, self.data["my_wind"], color="green")
        ax1.plot(self.data.index, self.data["my_demand"], color="red")
        ax1.set_ylabel("Power [kWh]")
        ax1.set_title("Wind and Demand")
        ax1.legend(["Wind", "Demand"])
        ax1.grid(True)
        ax2.plot(self.data.index, np.maximum(0,self.data["my_wind"]-self.data["my_demand"]), color="green")
        ax2.plot(self.data.index, np.minimum(0,self.data["my_wind"]-self.data["my_demand"]), color="red")
        ax2.legend(["Wind-Demand"])
        ax2.set_title("Wind-Demand")
        ax2.set_xlabel("Date")
        ax2.set_ylabel("Power [kW]")
        ax2.grid(True)
        ax3.plot(self.data.index, self.data["battery"], color = "blue")
        ax3.legend(["battery"])
        ax3.set_title("battery fillstand")
        ax3.set_ylabel("Power [kW]")
        ax4.plot(self.data.index, self.data["residual"], color="red")
        ax4.legend(["Wind-Demand"])
        ax4.set_title("Wind-Demand")
        ax4.set_xlabel("Date")
        ax4.set_ylabel("Power [kW]")
        ax4.grid(True)
        plt.show()

        pass


def main(argv = []):
    """Main function"""
    data_file = "smard_data/smard_2024_complete.csv"
    
    if not os.path.exists(data_file):
        print(f"❌ Data file not found: {data_file}")
        return
    
    analyzer = MeineAnalyse(data_file)
    results = analyzer.run_analysis()

if __name__ == "__main__":
    main(argv = sys.argv)
