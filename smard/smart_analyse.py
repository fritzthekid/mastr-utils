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

    def __init__(self, data=None, basic_data_set={}):
        self.data = data
        self.basic_data_set = basic_data_set
        self.costs_per_kwh = None
        self.battery_results = None

    def prepare_price(self):
        if self.year == None:
            self.data["price_per_kwh"] = self.data["my_demand"]*0+self.costs_per_kwh
        else:
            path = f"{os.path.abspath(os.path.dirname(__file__))}/costs"
            costs = pd.read_csv(f"{path}/{self.year}-hour-price.csv")
            costs["price"] /= 100
            total_average = costs["price"].mean()
            apl = []
            for i, p in enumerate(costs["price"]):
                if i < 12 or i > len(costs["price"])-12:
                    apl.append(total_average)
                else:
                    apl.append(costs["price"][i-12:i+12].mean())
            costs["avrgprice"] = apl
            costs["dtime"] = [datetime.strptime(t, "%Y-%m-%d %H:%M:%S") for t in costs["time"]]
            costs = costs.set_index("dtime")
            if self.data.index[0].year != self.year:
                raise Exception("Year mismatch")
            pl = []
            lstl = []
            i = costs.index[0]
            for t in self.data.index:
                seconds = (t-i).seconds
                # hours = int(seconds/3600)
                if seconds >= 3600 and (i+pd.Timedelta(hours=1)).year == self.year:
                    i += pd.Timedelta(hours=1)
                price = costs["price"].iloc[int((i-costs.index[0]).total_seconds()/3600)]
                pl.append(price)
                lstl.append(costs["avrgprice"].iloc[int((i-costs.index[0]).total_seconds()/3600)])
            self.data["price_per_kwh"] = pl
            self.data["avrgprice"] = lstl
        pass

    # def prepare_price_old(self):
    #             # dt = datetime.strptime(str(t), "%Y-%m-%d %H:%M:%S")
    #             pl.append(self.current_price(costs, t))
    #         self.data["price_per_kwh"] = pl
    #     pass


    def prepare_data(self):
        if "battery_discharge" in self.basic_data_set:
            self.battery_discharge = max(0,min(1,self.basic_data_set["battery_discharge"]))*self.resolution
        else:
            self.battery_discharge = 0
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
        spot_price = sum(self.neg*self.data["price_per_kwh"])
        fix_price = sum(self.neg)*self.costs_per_kwh
        spot_price_no = sum(self.data["my_demand"]*self.data["price_per_kwh"])
        fix_price_no = self.data["my_demand"].sum()*self.costs_per_kwh
        savings_no = "NN"
        savings = f"0.00 €/MWh"
        self.battery_results = pd.DataFrame([[-1,self.data["my_demand"].sum(),0,0,spot_price_no,fix_price_no],
                                            [0,sum(self.neg),sum(self.exflow),share,spot_price,fix_price]], 
                                            columns=["capacity kWh","residual kWh","exflow kWh", "autarky rate", "spot price [€]", "fix price [€]"])
        # print(f"wqithout renewables fix_price: {(sum(self.data["my_demand"])*self.costs_per_kwh/100000):.2f} T€, " +
        #       f"spot_price: {((sum(self.data["my_demand"]*self.data["price_per_kwh"])/100000)):.2f} T€")

        self.my_total_demand = self.data["my_demand"].sum()

    def run_analysis(self, capacity_list=[5000, 10000, 20000], 
                     power_list=[2500,5000,10000]):
        """Run the analysis"""
        if self.data is None:
            print("❌ No data loaded!")
            return

        logger.info("Starting analysis...")

        self.year = self.basic_data_set["year"]
        self.costs_per_kwh = self.basic_data_set["fix_costs_per_kwh"]/100
        self.prepare_price()
        self.prepare_data()
        self.print_results()
        for capacity, power in zip(capacity_list, power_list):
            self.simulate_battery(capacity=capacity*1000, power=power*1000)
            # self.print_results_with_battery()
        self.print_battery_results()
        self.visualise()
        pass


    def print_results(self):
        print(f"reference region: {self.region}, demand: {(sum(self.data["total_demand"])/1000):.2f} GWh, solar: {(sum(self.data['solar'])/1000):.2f} GWh, wind {(sum(self.data["wind_onshore"])/1000):.2f} GWh")
        print(f"total demand: {(sum(self.data["my_demand"])/1e3):.2f} MWh " +
              f"total Renewable_Source: {(sum(self.data["my_renew"])/1e3):.2f} MWh")
        print(f"total renewalbes: {(sum(self.pos)/1000):.2f} MWh, residual: {(sum(self.neg)/1000):.2f} MWh")
        print(f"share without battery {(sum(self.pos)/self.my_total_demand):.2f}")

    def print_battery_results(self):
        # print(self.battery_results)
        sp0 = self.battery_results["spot price [€]"].iloc[1]
        fp0 = self.battery_results["fix price [€]"].iloc[1]
        spotprice_gain = [f"{0:.2f}",f"{0:.2f}",f"{0:.2f}"] + [f"{((sp0-s)/max(1e-10,c)):.2f}" for s,c in zip(self.battery_results["spot price [€]"][3:],self.battery_results["capacity kWh"][3:])]
        fixprice_gain = [f"{0:.2f}",f"{0:.2f}",f"{0:.2f}"] + [f"{((fp0-f)/max(1e-10,c)):.2f}" for f,c in zip(self.battery_results["spot price [€]"][3:],self.battery_results["capacity kWh"][3:])]
        capacity_l = ["no renew","no bat"] + [f"{(c/1000)}" for c in self.battery_results["capacity kWh"][2:]]
        residual_l = [f"{(r/1000):.1f}" for r in self.battery_results["residual kWh"]]
        exflowl = [f"{(e/1000):.1f}" for e in self.battery_results["exflow kWh"]]
        autarky_rate_l = [f"{a:.2f}" for a in self.battery_results["autarky rate"]]
        spot_price_l = [f"{(s/1000):.1f}" for s in self.battery_results["spot price [€]"]]
        fix_price_l = [f"{(f/1000):.1f}" for f in self.battery_results["fix price [€]"]]
        values = np.array([capacity_l, residual_l, exflowl, autarky_rate_l, spot_price_l, fix_price_l, spotprice_gain, fixprice_gain]).T
        battery_results_norm = pd.DataFrame(values,
                                            columns=["cap MWh","resi MWh","exfl MWh", "autarky", "spp [T€]", "fixp [T€]", "sp €/kWh", "fp €/kWh"])
        with pd.option_context('display.max_columns', None):
            print(battery_results_norm)
        pass

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

    def __init__(self, csv_file_path, region = "", basic_data_set = {}):
        """Initialize with German SMARD data"""

        self.region = region
        
        self.basic_data_set = basic_data_set
        data = self.load_and_prepare_data(csv_file_path)
        super().__init__(data, basic_data_set)

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
        my_total_demand = self.basic_data_set["year_demand"]
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
        df["my_renew"] = df["wind_onshore"] * self.basic_data_set["wind_nominal_power"] / total_installed_wind * self.resolution
        df["my_renew"] += df["solar"] * self.basic_data_set["solar_max_power"] / total_installed_solar * self.resolution

        # print(my_total_demand, sum(df["my_demand"]), sum(pos)+sum(neg))
        df = df.fillna(0)
        
        print(f"✓ Loaded {len(df)} {(df.index[1]-df.index[0]).seconds/60} minutes records")
        print(f"Date range: {df.index.min()} to {df.index.max()}")

        if DEBUG:
            plt.plot(df["my_renew"])
            plt.plot(df["my_demand"])
            plt.show()
        return df

basic_data_set = {
    "year": 2024,
    "fix_costs_per_kwh": 11,
    "year_demand":2804 * 1000 * 6,
    "solar_max_power":5000,
    "wind_nominal_power":5000,
    "fix_contract" : False,
    "battery_discharge": 0.005,
}

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
    
    analyzer = MeineAnalyse(data_file, region, basic_data_set=basic_data_set)
    analyzer.run_analysis(capacity_list=[0,  0.1, 1.0,    5, 20, 100], 
                          power_list=   [0, 0.05, 0.5, 0.25, 10,  50])
    
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
"""
def calc_mean_cost_gain(costs):
    cal = []
    for i in range(int(min(356,len(costs["price"])/24))):
        lc = []
        for j,c in enumerate((costs["price"].iloc[i*24:(i+1)*24])):
            lc.append(c)
        cal.append(np.max(np.array(lc))-np.min(np.array(lc)))
    return np.mean(np.array(cal))
"""
