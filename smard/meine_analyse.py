import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
import sys
import logging
from battery_simulation import BatterySimulation

logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)

DEBUG = False


        
class Analyse(BatterySimulation):

    def __init__(self, data, costs=0.24):
        # self.region = None
        self.data = data
        # self.battery_results = None
        # pass

    """
    simulate_battery(self,capacity=20000, power=10000)
       - power [kW]
       - capacity [kWh]
       - given the total_demand values and renewable source values at each timepoint
         - total_demand [kWh]
         - renewable_source [kWh]
       - calculates 
        - storage level (fillstand)
        - residual       
    """
    def simulate_battery_simple(self,capacity=20000, power=10000):        
        container = []
        residual = []
        exflow = []
        battery_exflow= []
        battery_inflow= []
        exflow = []
        fillstand = capacity / 2
        for w,d in zip(self.data["my_renew"],self.data["my_demand"]):
            p = w-d
            diff = max(-power,min(power,p))
            if p > 0:
                battery_inflow.append(diff)
                battery_exflow.append(0)
                fillstand = min(capacity, fillstand+diff)
                if fillstand+diff > capacity:
                    exflow.append(fillstand+diff-capacity)
                else:
                    exflow.append(0)                    
                residual.append(0)
            else:
                battery_inflow.append(0)
                if fillstand <= 0:
                    battery_exflow.append(0)
                    fillstand = 0
                    residual.append(fillstand+diff)
                else:
                    battery_exflow.append(diff)
                    fillstand = fillstand+diff
                    residual.append(0)
                exflow.append(0)
            container.append(fillstand)
        self.data["battery_storage"] = container
        self.data["residual"] = residual
        self.data["exflow"] = exflow
        self.data["battery_inflow"] = battery_inflow
        self.data["battery_exflow"] = battery_exflow
        share = (sum(self.data["my_demand"]) + sum(residual))/sum(self.data["my_demand"])
        spot_price = -sum(residual*self.data["price_per_kwh"])/100
        fix_price = -sum(residual)*self.costs_per_kwh/100
        results = pd.DataFrame([[capacity/1000,f"{(-sum(residual)/1000):.2f}",f"{(sum(exflow)/1000):.2f}", f"{share:.2f}",f"{(spot_price/1000):.2f}",f"{(fix_price/1000):.2f}"]], 
                               columns=["capacity MWh","residual MWh","exflow MWh", "autarky_rate", "spot price [T€]", "fix price [T€]"])
        self.battery_results = pd.concat([self.battery_results, results], ignore_index=True)
        pass

    # def current_price(self, costs, time_point):
    #     for i, t in enumerate(costs["dtime"]):
    #         dt = datetime.strptime(str(t), "%Y-%m-%d %H:%M:%S")
    #         if time_point >= dt:
    #             return costs["price"].iloc[i]
    #     return self.costs_per_kwh

    def prepare_price(self):
        if self.year == None:
            self.data["price_per_kwh"] = self.data["my_demand"]*0+self.costs_per_kwh
        else:
            path = f"{os.path.abspath(os.path.dirname(__file__))}/costs"
            costs = pd.read_csv(f"{path}/{self.year}-hour-price.csv")
            total_average = costs["price"].mean()
            apl = []
            for i, p in enumerate(costs["price"]):
                if i < 24:
                    apl.append(p < total_average)
                else:
                    apl.append(p < costs["price"][-24:].mean())
            costs["load"] = apl
            costs["dtime"] = [datetime.strptime(t, "%Y-%m-%d %H:%M:%S") for t in costs["time"]]
            costs = costs.set_index("dtime")
            if self.data.index[0].year != self.year:
                raise Exception("Year mismatch")
            pl = []
            loadstrategy = []
            i = costs.index[0]
            for t in self.data.index:
                seconds = (t-i).seconds
                # hours = int(seconds/3600)
                if seconds >= 3600 and (i+pd.Timedelta(hours=1)).year == self.year:
                    i += pd.Timedelta(hours=1)
                price = costs["price"].iloc[int((i-costs.index[0]).total_seconds()/3600)]
                pl.append(price)
                loadstrategy.append(costs["load"].iloc[int((i-costs.index[0]).total_seconds()/3600)])
            self.data["price_per_kwh"] = pl
            self.data["loadstrategy"] = loadstrategy
        pass

    # def prepare_price_old(self):
    #             # dt = datetime.strptime(str(t), "%Y-%m-%d %H:%M:%S")
    #             pl.append(self.current_price(costs, t))
    #         self.data["price_per_kwh"] = pl
    #     pass


    def prepare_data(self):
        pos, neg, exflow = [], [], []
        for w,d in zip(self.data['my_renew'],self.data['my_demand']):
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
        share = sum(self.pos)/sum(self.data["my_demand"])
        spot_price = sum(self.neg*self.data["price_per_kwh"])/100
        fix_price = sum(self.pos)*self.costs_per_kwh/100
        spot_price_no = sum(self.data["my_demand"]*self.data["price_per_kwh"])/100
        fix_price_no = self.data["my_demand"].sum()*self.costs_per_kwh/100
        savings_no = "NN"
        savings = f"0.00 €/MWh"
        self.battery_results = pd.DataFrame([["no renewable",f"{(self.data["my_demand"].sum()/1000):.2f}",f"{0:.2f}",f"{0:.2f}",f"{(spot_price_no/1000):.2f}",f"{(fix_price_no/1000):.2f}"],
                                            [0,f"{(sum(self.neg)/1000):.2f}",f"{(sum(self.exflow)/1000):.2f}",f"{share:.2f}",f"{(spot_price/1000):.2f}",f"{(fix_price/1000):.2f}"]], 
                                            columns=["capacity MWh","residual MWh","exflow MWh", "autarky rate", "spot price [T€]", "fix price [T€]"])
        # print(f"wqithout renewables fix_price: {(sum(self.data["my_demand"])*self.costs_per_kwh/100000):.2f} T€, " +
        #       f"spot_price: {((sum(self.data["my_demand"]*self.data["price_per_kwh"])/100000)):.2f} T€")

        self.my_total_demand = self.data["my_demand"].sum()

    def run_analysis(self, capaciy_list=[5000, 10000, 20000], 
                     power_list=[2500,5000,10000],costs_per_kwh=24, year=None):
        """Run the analysis"""
        if self.data is None:
            print("❌ No data loaded!")
            return

        logger.info("Starting analysis...")

        self.year = year
        self.costs_per_kwh = costs_per_kwh
        self.prepare_price()
        self.prepare_data()
        self.print_results()
        for capacity, power in zip(capaciy_list, power_list):
            self.simulate_battery(capacity=capacity, power=power)
            self.print_results_with_battery()
        # self.simulate_battery(capacity=10000, power=5000)
        # self.print_results_with_battery()
        # self.simulate_battery(capacity=20000, power=10000)
        # self.print_results_with_battery()
        print(self.battery_results)
        self.visualise()
        pass


    def print_results(self):
        print(f"reference region: {self.region}, demand: {(sum(self.data["total_demand"])/1000):.2f} GWh, solar: {(sum(self.data['solar'])/1000):.2f} GWh, wind {(sum(self.data["wind_onshore"])/1000):.2f} GWh")
        print(f"total demand: {(sum(self.data["my_demand"])/1e3):.2f} MWh " +
              f"total Renewable_Source: {(sum(self.data["my_renew"])/1e3):.2f} MWh")
        print(f"total renewalbes: {(sum(self.pos)/1000):.2f} MWh, residual: {(sum(self.neg)/1000):.2f} MWh")
        print(f"share without battery {(sum(self.pos)/self.my_total_demand):.2f}")

    def print_results_with_battery(self):
        res = -sum(self.data["residual"])
        print(f"total renewalbes: {(sum(self.pos)/1000):.2f} MWh, residual: {(res/1000):.2f} MWh, export: {(sum(self.data["exflow"])/1000):.2f} MWh")
        print(f"share with battery: {((self.my_total_demand - res)/self.my_total_demand):.2f}")
        pass

    def visualise(self, start=0, end=None):
        if end is None:
            end = len(self.data)        
        fig, [ax1, ax2, ax3, ax4] = plt.subplots(4, 1, sharex=True)
        ax1.plot(self.data.index[start:end], self.data["my_renew"][start:end], color="green")
        ax1.plot(self.data.index[start:end], self.data["my_demand"][start:end], color="red")
        ax1.set_ylabel("[kWh]")
        ax1.set_title(f"Renewable_Source and Demand ({self.region})")
        ax1.legend(["Renewable_Source", "Demand"])
        ax1.grid(True)
        ax2.plot(self.data.index[start:end], np.maximum(0,self.data["my_renew"][start:end]-self.data["my_demand"])[start:end], color="green")
        ax2.plot(self.data.index[start:end], np.minimum(0,self.data["my_renew"][start:end]-self.data["my_demand"][start:end]), color="red")
        ax2.legend(["Renewable_Source-Demand", "Residual"])
        ax2.set_title("Renewable_Source-Demand")
        ax2.set_ylabel("[kWh]")
        ax2.grid(True)
        ax3.plot(self.data.index[start:end], self.data["battery_storage"][start:end], color = "blue")
        # ax3.legend(["battery_storage"])
        ax3.set_title("battery fillstand")
        ax3.set_ylabel("[kWh]")
        ax4.plot(self.data.index[start:end], self.data["residual"][start:end], color="red")
        #ax4.legend(["-Demand"])
        ax4.set_title("Residual")
        ax4.set_xlabel("Date")
        ax4.set_ylabel("[kWh]")
        ax4.grid(True)
        plt.show()

        pass

class MeineAnalyse(Analyse):

    def __init__(self, csv_file_path, region = ""):
        """Initialize with German SMARD data"""
        self.region = region
        data = self.load_and_prepare_data(csv_file_path)
        super().__init__(data)

    def load_and_prepare_data(self, csv_file_path):
        """Load and prepare SMARD data"""
        print("Loading SMARD data for European grid analysis...")
        
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

        # print(my_total_demand, sum(df["my_demand"]), sum(pos)+sum(neg))
        df = df.fillna(0)
        
        print(f"✓ Loaded {len(df)} {(df.index[1]-df.index[0]).seconds/60} minutes records")
        print(f"Date range: {df.index.min()} to {df.index.max()}")

        if DEBUG:
            plt.plot(df["my_renew"])
            plt.plot(df["my_demand"])
            plt.show()
        return df

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
    analyzer.run_analysis(capaciy_list=[1000, 5000, 20000, 100000], power_list=[500,2500,10000,50000], costs_per_kwh=7.9, year=2024)
    pass

    # # Einzelne Simulation

    # result = analyzer.simulate_battery(capacity=20000, power=10000)

    # # Batterie-Vergleich
    # comparison = analyzer.run_battery_comparison(
    #     capacities=[1000, 5000, 20000], 
    #     power_factor=0.5)

if __name__ == "__main__":
    main(argv = sys.argv)


"""
von Claude gerechnet.
Batterie    Autarkie    Verbesserung    €/MWh Verbesserung
   0 MWh      71%         -              -
   1 MWh      73%        +2pp           ~28€/MWh*
   5 MWh      77%        +6pp           ~19€/MWh
  20 MWh      84%       +13pp           ~13€/MWh
 100 MWh      92%       +21pp            ~6€/MWh
"""
"""
Ladestrategie anpassen:

# Statt: einfach Überschuss → laden
if renewable_surplus > 0:
    if current_spot_price < daily_average_price:
        battery_charge()
    else:
        sell_to_grid()  # Bei hohen Preisen direkt verkaufen
"""