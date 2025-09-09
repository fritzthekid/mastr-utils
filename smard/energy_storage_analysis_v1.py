#!/usr/bin/env python3
"""
Energy Storage Analysis for Germany's Renewable Transition
Analyzes battery storage requirements for a high-renewable scenario
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
import sys

if len(sys.argv) > 1:
    expansion = int(sys.argv[1])
else:
    expansion = 2

class EnergyStorageAnalyzer:
    def __init__(self, csv_file_path):
        """Initialize with the combined SMARD data"""
        self.data = self.load_and_prepare_data(csv_file_path)
        self.scenario_data = None
        
    def load_and_prepare_data(self, csv_file_path):
        """Load and prepare the SMARD data"""
        print("Loading SMARD data...")
        
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
                elif 'Braunkohle' in col:
                    column_mapping[col] = 'lignite'
                elif 'Steinkohle' in col:
                    column_mapping[col] = 'coal'
                elif 'Erdgas' in col:
                    column_mapping[col] = 'gas'
                elif 'Kernenergie' in col:
                    column_mapping[col] = 'nuclear'
                elif 'Gesamtverbrauch' in col or 'Netzlast' in col:
                    column_mapping[col] = 'total_demand'
                elif 'Pumpspeicher' in col and 'Verbrauch' not in col:
                    column_mapping[col] = 'pumped_storage'
            
            df = df.rename(columns=column_mapping)
            
            # Fill NaN values with 0 for energy generation
            df = df.fillna(0)
            
            print(f"✓ Loaded {len(df)} hourly records")
            print(f"Date range: {df.index.min()} to {df.index.max()}")
            print(f"Available columns: {list(df.columns)}")
            
            return df
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return None
    
    def create_renewable_scenario(self):
        """Create the high-renewable scenario as specified"""
        print("\nCreating renewable scenario...")
        print("- Doubling wind onshore and offshore")
        print("- Doubling photovoltaic")
        print("- Keeping hydro and biomass unchanged")
        print("- Setting coal/lignite to 0")
        print("- Limiting gas to max 5% of total demand")
        
        scenario = self.data.copy()
        
        # Double renewable sources
        if 'wind_onshore' in scenario.columns:
            scenario['wind_onshore'] *= expansion
        if 'wind_offshore' in scenario.columns:
            scenario['wind_offshore'] *= expansion
        if 'solar' in scenario.columns:
            scenario['solar'] *= expansion
        
        # Remove coal and nuclear
        if 'lignite' in scenario.columns:
            scenario['lignite'] = 0
        if 'coal' in scenario.columns:
            scenario['coal'] = 0
        if 'nuclear' in scenario.columns:
            scenario['nuclear'] = 0
        
        # Limit gas to 5% of demand
        if 'gas' in scenario.columns and 'total_demand' in scenario.columns:
            max_gas = scenario['total_demand'] * 0.05
            scenario['gas'] = np.minimum(scenario['gas'], max_gas)
        
        self.scenario_data = scenario
        return scenario
    
    def calculate_energy_balance(self):
        """Calculate the energy balance and required storage"""
        if self.scenario_data is None:
            self.create_renewable_scenario()
        
        df = self.scenario_data.copy()
        
        # Calculate total renewable generation
        renewable_cols = ['wind_onshore', 'wind_offshore', 'solar', 'hydro', 'biomass']
        available_renewables = [col for col in renewable_cols if col in df.columns]
        
        df['total_renewable_generation'] = df[available_renewables].sum(axis=1)
        
        # Add conventional generation (limited gas + pumped storage)
        conventional_cols = ['gas', 'pumped_storage']
        available_conventional = [col for col in conventional_cols if col in df.columns]
        
        if available_conventional:
            df['total_conventional_generation'] = df[available_conventional].sum(axis=1)
        else:
            df['total_conventional_generation'] = 0
        
        # Total generation
        df['total_generation'] = df['total_renewable_generation'] + df['total_conventional_generation']
        
        # Energy balance (positive = surplus, negative = deficit)
        df['energy_balance'] = df['total_generation'] - df['total_demand']
        
        # Calculate cumulative energy balance (battery state simulation)
        df['cumulative_balance'] = df['energy_balance'].cumsum()
        
        return df
    
    def calculate_storage_requirements(self):
        """Calculate the required battery storage capacity"""
        df = self.calculate_energy_balance()
        
        # Find the range of cumulative balance to determine storage needs
        min_cumulative = df['cumulative_balance'].min()
        max_cumulative = df['cumulative_balance'].max()
        
        # Required storage capacity is the difference between max and min
        required_capacity = max_cumulative - min_cumulative
        
        # Also calculate some additional metrics
        total_surplus = df[df['energy_balance'] > 0]['energy_balance'].sum()
        total_deficit = abs(df[df['energy_balance'] < 0]['energy_balance'].sum())
        
        surplus_hours = len(df[df['energy_balance'] > 0])
        deficit_hours = len(df[df['energy_balance'] < 0])
        
        renewable_share = df['total_renewable_generation'].sum() / df['total_generation'].sum() * 100
        
        results = {
            'required_capacity_MWh': required_capacity,
            'required_capacity_GWh': required_capacity / 1000,
            'total_surplus_MWh': total_surplus,
            'total_deficit_MWh': total_deficit,
            'surplus_hours': surplus_hours,
            'deficit_hours': deficit_hours,
            'total_hours': len(df),
            'renewable_share_percent': renewable_share,
            'max_continuous_deficit': self.find_max_continuous_deficit(df),
            'max_continuous_surplus': self.find_max_continuous_surplus(df),
        }
        
        return results, df
    
    def find_max_continuous_deficit(self, df):
        """Find the longest continuous period of energy deficit"""
        deficit_periods = []
        current_deficit = 0
        
        for balance in df['energy_balance']:
            if balance < 0:
                current_deficit += abs(balance)
            else:
                if current_deficit > 0:
                    deficit_periods.append(current_deficit)
                current_deficit = 0
        
        if current_deficit > 0:
            deficit_periods.append(current_deficit)
        
        return max(deficit_periods) if deficit_periods else 0
    
    def find_max_continuous_surplus(self, df):
        """Find the longest continuous period of energy surplus"""
        surplus_periods = []
        current_surplus = 0
        
        for balance in df['energy_balance']:
            if balance > 0:
                current_surplus += balance
            else:
                if current_surplus > 0:
                    surplus_periods.append(current_surplus)
                current_surplus = 0
        
        if current_surplus > 0:
            surplus_periods.append(current_surplus)
        
        return max(surplus_periods) if surplus_periods else 0
    
    def create_visualizations(self, results, df, output_dir="analysis_output"):
        """Create visualizations of the analysis"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        plt.style.use('seaborn-v0_8')
        
        # 1. Energy balance over time
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(15, 12))
        
        # Plot 1: Generation vs Demand
        ax1.plot(df.index, df['total_demand'], label='Total Demand', color='red', alpha=0.7)
        ax1.plot(df.index, df['total_renewable_generation'], label='Renewable Generation', color='green', alpha=0.7)
        ax1.plot(df.index, df['total_generation'], label='Total Generation', color='blue', alpha=0.7)
        ax1.set_ylabel('Energy [MWh]')
        ax1.set_title('Energy Generation vs Demand (Renewable Scenario)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Energy balance
        colors = ['red' if x < 0 else 'green' for x in df['energy_balance']]
        ax2.bar(df.index, df['energy_balance'], color=colors, alpha=0.6, width=0.04)
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        ax2.set_ylabel('Energy Balance [MWh]')
        ax2.set_title('Hourly Energy Balance (Green=Surplus, Red=Deficit)')
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Cumulative balance (battery state)
        ax3.plot(df.index, df['cumulative_balance'], color='purple', linewidth=2)
        ax3.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        ax3.fill_between(df.index, df['cumulative_balance'], alpha=0.3, color='purple')
        ax3.set_ylabel('Cumulative Balance [MWh]')
        ax3.set_xlabel('Date')
        ax3.set_title('Required Battery Storage Range')
        ax3.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/energy_balance_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # 2. Monthly aggregation
        monthly_data = df.resample('M').agg({
            'total_demand': 'sum',
            'total_renewable_generation': 'sum',
            'total_generation': 'sum',
            'energy_balance': 'sum'
        })
        
        fig, ax = plt.subplots(figsize=(12, 6))
        x = range(len(monthly_data))
        width = 0.35
        
        ax.bar([i - width/2 for i in x], monthly_data['total_demand'], width, 
               label='Demand', color='red', alpha=0.7)
        ax.bar([i + width/2 for i in x], monthly_data['total_renewable_generation'], width,
               label='Renewable Generation', color='green', alpha=0.7)
        
        ax.set_xlabel('Month')
        ax.set_ylabel('Energy [MWh]')
        ax.set_title('Monthly Energy Balance')
        ax.set_xticks(x)
        ax.set_xticklabels([d.strftime('%Y-%m') for d in monthly_data.index])
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'{output_dir}/monthly_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def print_results(self, results):
        """Print the analysis results"""
        print("\n" + "="*60)
        print("ENERGY STORAGE ANALYSIS RESULTS")
        print("="*60)
        
        print(f"\n🔋 REQUIRED BATTERY STORAGE:")
        print(f"   Capacity needed: {results['required_capacity_GWh']:.1f} GWh")
        print(f"                   ({results['required_capacity_MWh']:.0f} MWh)")
        
        print(f"\n📊 ENERGY BALANCE SUMMARY:")
        print(f"   Renewable share: {results['renewable_share_percent']:.1f}%")
        print(f"   Total surplus:   {results['total_surplus_MWh']/1000:.0f} GWh")
        print(f"   Total deficit:   {results['total_deficit_MWh']/1000:.0f} GWh")
        
        print(f"\n⏰ TIME ANALYSIS:")
        print(f"   Hours with surplus: {results['surplus_hours']:,} ({results['surplus_hours']/results['total_hours']*100:.1f}%)")
        print(f"   Hours with deficit: {results['deficit_hours']:,} ({results['deficit_hours']/results['total_hours']*100:.1f}%)")
        
        print(f"\n📈 EXTREME PERIODS:")
        print(f"   Max continuous deficit: {results['max_continuous_deficit']/1000:.1f} GWh")
        print(f"   Max continuous surplus: {results['max_continuous_surplus']/1000:.1f} GWh")
        
        # Put results in perspective
        print(f"\n🏭 PERSPECTIVE:")
        print(f"   Tesla Gigafactory Nevada: ~35 GWh/year production")
        print(f"   Required storage = {results['required_capacity_GWh']/35:.1f}x Tesla Gigafactory annual production")
        
        german_car_batteries = results['required_capacity_GWh'] * 1000 / 75  # Assuming 75 kWh per EV
        print(f"   Equivalent to ~{german_car_batteries/1000:.0f}k electric car batteries (75kWh each)")
        
    def run_complete_analysis(self):
        """Run the complete analysis"""
        if self.data is None:
            print("❌ No data loaded!")
            return
        
        print("Starting complete energy storage analysis...")
        
        # Run analysis
        results, df = self.calculate_storage_requirements()
        
        # Print results
        self.print_results(results)
        
        # Create visualizations
        self.create_visualizations(results, df)
        
        # Save detailed results
        output_dir = "analysis_output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Save the scenario data
        df.to_csv(f'{output_dir}/renewable_scenario_data.csv', sep=';', decimal=',')
        
        # Save summary
        with open(f'{output_dir}/analysis_summary.txt', 'w') as f:
            f.write("ENERGY STORAGE ANALYSIS SUMMARY\n")
            f.write("="*50 + "\n\n")
            f.write(f"Required Battery Storage: {results['required_capacity_GWh']:.1f} GWh\n")
            f.write(f"Renewable Share: {results['renewable_share_percent']:.1f}%\n")
            f.write(f"Total Hours Analyzed: {results['total_hours']:,}\n")
            f.write(f"Hours with Surplus: {results['surplus_hours']:,}\n")
            f.write(f"Hours with Deficit: {results['deficit_hours']:,}\n")
        
        print(f"\n✅ Analysis complete! Results saved to '{output_dir}/' directory")
        
        return results, df

def main():
    """Main function"""
    # Look for the combined CSV file
    data_file = "smard_data/smard_2024_complete.csv"
    
    if not os.path.exists(data_file):
        print(f"❌ Data file not found: {data_file}")
        print("Please run the smart-downloader.py script first to download the data.")
        return
    
    # Run analysis
    analyzer = EnergyStorageAnalyzer(data_file)
    results, df = analyzer.run_complete_analysis()

if __name__ == "__main__":
    main()
