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

    def __init__(self, csv_file_path, region = ""):
        """Initialize with German SMARD data"""
        self.region = region
        self.data = self.load_and_prepare_data(csv_file_path)
        share = sum(self.pos)/sum(self.data["my_demand"])
        self.battery_results = pd.DataFrame([[0,f"{(sum(self.neg)/1000):.2f}",f"{(sum(self.exflow)/1000):.2f}",f"{share:.2f}"]], columns=["capacity MWh","residual MWh","exflow MWh", "share"])
        
    def load_and_prepare_data(self, csv_file_path):
        """Load and prepare SMARD data"""
        print("Loading SMARD data for European grid analysis...")
        
        if True:
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

            self.resolution = ((df.index[1]-df.index[0]).seconds)/3600

            total_demand = df["total_demand"].sum()*self.resolution
            my_total_demand = 6*1000*2804
            self.my_total_demand = my_total_demand

            """
            Betrachtung Deutschland

            - 130 GW installierte PV
            - 63 GW installierte Windanlagen
            - 50 GW sonstige

            Betrachtung Luxemburg 2022
            - 317 MWp installierte PV
            - 208 MW installierte Leistung, 280 GWh eingespeiste Energie Wind

            """

            if self.region == "_de":
                total_installed_solar = 130e3
                total_installed_wind = 63e3
            else:
                total_installed_solar = 326
                total_installed_wind = 208

            ### this an extimate (for the time being seems better ...)
            
            total_installed_solar = max(df["solar"])
            total_installed_wind = max(df["wind_onshore"])
            df["my_demand"] = df["total_demand"] * my_total_demand / total_demand * self.resolution
            df["my_renew"] = df["wind_onshore"] * 5000 / total_installed_wind * self.resolution
            df["my_renew"] += df["solar"] * 5000 / total_installed_solar * self.resolution

            pos, neg, exflow = [], [], []
            for w,d in zip(df['my_renew'],df['my_demand']):
                if w > d:
                    pos.append(d)
                    neg.append(0)
                    exflow.append(w-d)
                else:
                    pos.append(w)
                    neg.append(d-w)
            self.pos = pos
            self.neg = neg
            self.exflow = exflow

            # print(my_total_demand, sum(df["my_demand"]), sum(pos)+sum(neg))
            df = df.fillna(0)
            
            print(f"✓ Loaded {len(df)} {(df.index[1]-df.index[0]).seconds/60} minutes records")
            print(f"Date range: {df.index.min()} to {df.index.max()}")

            if DEBUG:
                plt.plot(df["my_renew"])
                plt.plot(df["my_demand"])
                plt.show()
            return df

        else: #ion as e:
            print(f"Error loading data: {e}")
            return None

    def simulate_battery(self,capacity=20000, power=10000):
        container = []
        residual = []
        exflow = []
        fillstand = capacity / 2
        for w,d in zip(self.data["my_renew"],self.data["my_demand"]):
            p = w-d
            diff = max(-power,min(power,p))
            if p > 0:
                fillstand = min(capacity, fillstand+diff)
                if fillstand+diff > capacity:
                    exflow.append(fillstand+diff-capacity)
                else:
                    exflow.append(0)                    
                residual.append(0)
            else:
                if fillstand <= 0:
                    fillstand = 0
                    residual.append(fillstand+diff)
                else:
                    fillstand = fillstand+diff
                    residual.append(0)
                exflow.append(0)
            container.append(fillstand)
        self.data["battery"] = container
        self.data["residual"] = residual
        self.data["exflow"] = exflow
        share = (sum(self.data["my_demand"]) + sum(residual))/sum(self.data["my_demand"])
        results = pd.DataFrame([[capacity/1000,f"{(-sum(residual)/1000):.2f}",f"{(sum(exflow)/1000):.2f}", f"{share:.2f}"]], columns=["capacity MWh","residual MWh","exflow MWh", "share"])
        self.battery_results = pd.concat([self.battery_results, results], ignore_index=True)
        pass

    def run_analysis(self):
        """Run the analysis"""
        if self.data is None:
            print("❌ No data loaded!")
            return
        
        logger.info("Starting analysis...")

        self.print_results()
        self.simulate_battery(capacity=5000, power=2500)
        self.print_results_with_battery()
        self.simulate_battery(capacity=10000, power=5000)
        self.print_results_with_battery()
        self.simulate_battery(capacity=20000, power=10000)
        self.print_results_with_battery()
        print(self.battery_results)
        self.visualise()

    def print_results(self):
        print(f"reference region: {self.region}, demand: {(sum(self.data["total_demand"])/1000):.2f} GWh, solar: {(sum(self.data['solar'])/1000):.2f} GWh, wind {(sum(self.data["wind_onshore"])/1000):.2f} GWh")
        print(f"total demand: {(sum(self.data["my_demand"])/1e6):.2f} GWh " +
              f"total Renewable_Source: {(sum(self.data["my_renew"])/1e6):.2f} GWh")
        print(f"total renewalbes: {(sum(self.pos)/1000):.2f} MWh, residual: {(sum(self.neg)/1000):.2f} MWh")
        print(f"share without battery {(sum(self.pos)/self.my_total_demand):.2f}")

    def print_results_with_battery(self):
        res = -sum(self.data["residual"])
        print(f"total renewalbes: {(sum(self.pos)/1000):.2f} MWh, residual: {(res/1000):.2f} MWh, export: {(sum(self.data["exflow"])/1000):.2f} MWh")
        print(f"share with battery: {((self.my_total_demand - res)/self.my_total_demand):.2f}")
        pass

    def visualise(self):        
        fig, [ax1, ax2, ax3, ax4] = plt.subplots(4, 1, sharex=True)
        ax1.plot(self.data.index, self.data["my_renew"], color="green")
        ax1.plot(self.data.index, self.data["my_demand"], color="red")
        ax1.set_ylabel("[kWh]")
        ax1.set_title(f"Renewable_Source and Demand ({self.region})")
        ax1.legend(["Renewable_Source", "Demand"])
        ax1.grid(True)
        ax2.plot(self.data.index, np.maximum(0,self.data["my_renew"]-self.data["my_demand"]), color="green")
        ax2.plot(self.data.index, np.minimum(0,self.data["my_renew"]-self.data["my_demand"]), color="red")
        ax2.legend(["Renewable_Source-Demand", "Residual"])
        ax2.set_title("Renewable_Source-Demand")
        ax2.set_xlabel("Date")
        ax2.set_ylabel("[kWh]")
        ax2.grid(True)
        ax3.plot(self.data.index, self.data["battery"], color = "blue")
        # ax3.legend(["battery"])
        ax3.set_title("battery fillstand")
        ax3.set_ylabel("[kWh]")
        ax4.plot(self.data.index, self.data["residual"], color="red")
        #ax4.legend(["-Demand"])
        ax4.set_title("Residual")
        ax4.set_xlabel("Date")
        ax4.set_ylabel("[kWh]")
        ax4.grid(True)
        plt.show()

        pass


def main(argv = []):
    """Main function"""
    if len(argv) > 1:
        region = f"_{argv[1]}"
    else:
        region = "_lu"
    data_file = f"quarterly/smard_data{region}/smard_2024_complete.csv"
    
    if not os.path.exists(data_file):
        print(f"❌ Data file not found: {data_file}")
        return
    
    analyzer = MeineAnalyse(data_file, region)
    results = analyzer.run_analysis()

if __name__ == "__main__":
    main(argv = sys.argv)
