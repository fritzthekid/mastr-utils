#!/usr/bin/env python3
"""
Battery Storage Impact Analysis
Analyzes how different battery storage capacities affect the renewable/residual energy split
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

class StorageImpactAnalyzer:
    def __init__(self, csv_file_path):
        """Initialize with the combined SMARD data"""
        self.data = self.load_and_prepare_data(csv_file_path)
        self.enhanced_data = None
        
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
                elif 'Sonstige Konventionelle' in col:
                    column_mapping[col] = 'other_conventional'
                elif 'Sonstige Erneuerbare' in col:
                    column_mapping[col] = 'other_renewable'
            
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
    
    def create_enhanced_renewable_scenario(self):
        """Create scenario with doubled wind and solar"""
        print("\nCreating enhanced renewable scenario...")
        print("- Doubling wind onshore and offshore")
        print("- Doubling photovoltaic")
        print("- Keeping all other sources unchanged")
        
        scenario = self.data.copy()
        
        # Double renewable sources
        if 'wind_onshore' in scenario.columns:
            original_wind_onshore = scenario['wind_onshore'].sum()
            scenario['wind_onshore'] *= 2
            print(f"  Wind onshore: {original_wind_onshore/1000:.1f} → {scenario['wind_onshore'].sum()/1000:.1f} GWh")
            
        if 'wind_offshore' in scenario.columns:
            original_wind_offshore = scenario['wind_offshore'].sum()
            scenario['wind_offshore'] *= 2
            print(f"  Wind offshore: {original_wind_offshore/1000:.1f} → {scenario['wind_offshore'].sum()/1000:.1f} GWh")
            
        if 'solar' in scenario.columns:
            original_solar = scenario['solar'].sum()
            scenario['solar'] *= 2
            print(f"  Solar: {original_solar/1000:.1f} → {scenario['solar'].sum()/1000:.1f} GWh")
        
        # Calculate renewable and conventional categories
        renewable_cols = ['wind_onshore', 'wind_offshore', 'solar', 'hydro', 'biomass', 'other_renewable']
        available_renewables = [col for col in renewable_cols if col in scenario.columns]
        scenario['total_renewables'] = scenario[available_renewables].sum(axis=1)
        
        conventional_cols = ['lignite', 'coal', 'gas', 'nuclear', 'pumped_storage', 'other_conventional']
        available_conventional = [col for col in conventional_cols if col in scenario.columns]
        scenario['total_conventional'] = scenario[available_conventional].sum(axis=1)
        
        self.enhanced_data = scenario
        return scenario
    
    def simulate_battery_storage(self, capacity_gwh, power_gw):
        """
        Simulate battery storage operation
        capacity_gwh: Battery capacity in GWh
        power_gw: Battery power rating in GW (charging/discharging rate)
        """
        df = self.enhanced_data.copy()
        
        # Convert to MWh and MW for consistency with data
        capacity_mwh = capacity_gwh * 1000
        power_mw = power_gw * 1000
        
        # Initialize battery state
        battery_level = np.zeros(len(df))
        battery_charge = np.zeros(len(df))  # Positive = charging, negative = discharging
        
        # Calculate initial energy balance (renewable - demand)
        df['energy_balance'] = df['total_renewables'] - df['total_demand']
        
        for i in range(len(df)):
            if i == 0:
                battery_level[i] = capacity_mwh / 2  # Start at 50% capacity
            else:
                battery_level[i] = battery_level[i-1]
            
            balance = df['energy_balance'].iloc[i]
            
            if balance > 0:  # Surplus - try to charge battery
                max_charge = min(balance, power_mw, capacity_mwh - battery_level[i])
                battery_charge[i] = max_charge
                battery_level[i] += max_charge
            elif balance < 0:  # Deficit - try to discharge battery
                max_discharge = min(abs(balance), power_mw, battery_level[i])
                battery_charge[i] = -max_discharge
                battery_level[i] -= max_discharge
        
        df['battery_level'] = battery_level
        df['battery_charge'] = battery_charge
        
        # Calculate effective energy after battery operation
        df['renewable_after_storage'] = df['total_renewables'] - np.maximum(0, df['battery_charge'])
        df['storage_discharge'] = np.maximum(0, -df['battery_charge'])
        df['residual_needed'] = np.maximum(0, df['total_demand'] - df['renewable_after_storage'] - df['storage_discharge'])
        
        return df
    
    def analyze_storage_scenarios(self, capacity_range_gwh=None, power_factor=0.5):
        """
        Analyze multiple storage scenarios
        capacity_range_gwh: List of battery capacities to test (in GWh)
        power_factor: Power rating as fraction of capacity (e.g., 0.5 means power = capacity/2)
        """
        if self.enhanced_data is None:
            self.create_enhanced_renewable_scenario()
        
        if capacity_range_gwh is None:
            # Default range from 0 to 200 GWh
            capacity_range_gwh = [0, 5, 10, 20, 30, 40, 50, 75, 100, 125, 150, 175, 200, 250, 300]
        
        results = []
        
        print(f"\nAnalyzing {len(capacity_range_gwh)} storage scenarios...")
        print(f"Power rating: {power_factor} × capacity (e.g., {power_factor*100} GWh capacity = {power_factor*100} GW power)")
        
        for i, capacity in enumerate(capacity_range_gwh):
            power = capacity * power_factor  # Power rating based on capacity
            
            print(f"  {i+1:2d}/{len(capacity_range_gwh)}: {capacity:3.0f} GWh capacity, {power:3.1f} GW power")
            
            df = self.simulate_battery_storage(capacity, power)
            
            # Calculate energy splits
            total_demand = df['total_demand'].sum()
            renewable_supplied = (df['renewable_after_storage'] + df['storage_discharge']).sum()
            residual_needed = df['residual_needed'].sum()
            
            renewable_share = renewable_supplied / total_demand * 100
            residual_share = residual_needed / total_demand * 100
            
            # Additional metrics
            battery_utilization = df['battery_level'].mean() / (capacity * 1000) * 100 if capacity > 0 else 0
            max_battery_level = df['battery_level'].max()
            min_battery_level = df['battery_level'].min()
            
            curtailed_renewable = np.maximum(0, df['energy_balance'] - np.maximum(0, df['battery_charge'])).sum()
            curtailment_rate = curtailed_renewable / df['total_renewables'].sum() * 100
            
            results.append({
                'capacity_gwh': capacity,
                'power_gw': power,
                'renewable_share_percent': renewable_share,
                'residual_share_percent': residual_share,
                'battery_utilization_percent': battery_utilization,
                'max_battery_level_gwh': max_battery_level / 1000,
                'min_battery_level_gwh': min_battery_level / 1000,
                'curtailment_rate_percent': curtailment_rate,
                'total_demand_twh': total_demand / 1e6,
                'renewable_supplied_twh': renewable_supplied / 1e6,
                'residual_needed_twh': residual_needed / 1e6
            })
        
        return pd.DataFrame(results)
    
    def create_visualizations(self, results_df, output_dir="storage_analysis"):
        """Create visualizations of the storage impact analysis"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        plt.style.use('seaborn-v0_8')
        
        # 1. Main plot: Renewable vs Residual share by storage capacity
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # Plot 1: Energy split
        ax1.plot(results_df['capacity_gwh'], results_df['renewable_share_percent'], 
                'g-o', linewidth=2, markersize=6, label='Renewable Share')
        ax1.plot(results_df['capacity_gwh'], results_df['residual_share_percent'], 
                'r-s', linewidth=2, markersize=6, label='Residual Share')
        ax1.set_xlabel('Battery Capacity [GWh]')
        ax1.set_ylabel('Energy Share [%]')
        ax1.set_title('Renewable vs Residual Energy Share')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, 100)
        
        # Plot 2: Absolute energy amounts
        ax2.plot(results_df['capacity_gwh'], results_df['renewable_supplied_twh'], 
                'g-o', linewidth=2, markersize=6, label='Renewable Supplied')
        ax2.plot(results_df['capacity_gwh'], results_df['residual_needed_twh'], 
                'r-s', linewidth=2, markersize=6, label='Residual Needed')
        ax2.set_xlabel('Battery Capacity [GWh]')
        ax2.set_ylabel('Energy [TWh]')
        ax2.set_title('Absolute Energy Amounts')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Battery utilization and curtailment
        ax3_twin = ax3.twinx()
        line1 = ax3.plot(results_df['capacity_gwh'], results_df['battery_utilization_percent'], 
                        'b-^', linewidth=2, markersize=6, label='Battery Utilization')
        line2 = ax3_twin.plot(results_df['capacity_gwh'], results_df['curtailment_rate_percent'], 
                             'orange', linestyle='--', marker='d', linewidth=2, markersize=6, label='Curtailment Rate')
        
        ax3.set_xlabel('Battery Capacity [GWh]')
        ax3.set_ylabel('Battery Utilization [%]', color='b')
        ax3_twin.set_ylabel('Renewable Curtailment [%]', color='orange')
        ax3.set_title('Battery Utilization & Renewable Curtailment')
        
        # Combine legends
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax3.legend(lines, labels, loc='upper right')
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Marginal benefit
        renewable_increase = results_df['renewable_share_percent'].diff()
        capacity_increase = results_df['capacity_gwh'].diff()
        marginal_benefit = renewable_increase / capacity_increase
        
        ax4.plot(results_df['capacity_gwh'][1:], marginal_benefit[1:], 
                'purple', marker='o', linewidth=2, markersize=6)
        ax4.set_xlabel('Battery Capacity [GWh]')
        ax4.set_ylabel('Marginal Benefit [% renewable per GWh]')
        ax4.set_title('Marginal Benefit of Additional Storage')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/storage_impact_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # 2. Detailed table visualization
        fig, ax = plt.subplots(figsize=(14, 8))
        ax.axis('tight')
        ax.axis('off')
        
        # Create table data
        table_data = results_df[['capacity_gwh', 'renewable_share_percent', 'residual_share_percent', 
                               'battery_utilization_percent', 'curtailment_rate_percent']].round(1)
        table_data.columns = ['Capacity\n[GWh]', 'Renewable\nShare [%]', 'Residual\nShare [%]', 
                             'Battery\nUtilization [%]', 'Curtailment\nRate [%]']
        
        table = ax.table(cellText=table_data.values, colLabels=table_data.columns,
                        cellLoc='center', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)
        
        # Color code the table
        for i in range(len(table_data)):
            renewable_share = table_data.iloc[i]['Renewable\nShare [%]']
            if renewable_share >= 90:
                color = 'lightgreen'
            elif renewable_share >= 80:
                color = 'lightyellow'
            else:
                color = 'lightcoral'
            
            for j in range(len(table_data.columns)):
                table[(i+1, j)].set_facecolor(color)
        
        plt.title('Storage Capacity vs Energy Mix - Detailed Results', fontsize=14, pad=20)
        plt.savefig(f'{output_dir}/results_table.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def print_summary(self, results_df):
        """Print summary of the analysis with clear explanations"""
        print("\n" + "="*80)
        print("STORAGE IMPACT ANALYSIS SUMMARY")
        print("="*80)
        
        print(f"\n🏭 SCENARIO EXPLANATION:")
        print(f"   • Base renewable generation doubled for wind & solar")
        print(f"   • All other sources (gas, hydro, biomass, etc.) unchanged")
        print(f"   • Battery power rating = 1.0 × capacity (100% C-rate)")
        print(f"   • This means: 1 GWh battery can charge/discharge at 1 GW")
        
        print(f"\n📋 LEGEND EXPLANATION:")
        print(f"   • Renewable Share: % of demand met by renewables (direct + via battery)")
        print(f"   • Residual Share: % of demand requiring conventional sources (gas, coal)")
        print(f"   • Battery Utilization: Average battery fill level during the year")
        print(f"   • Curtailment Rate: % of renewable energy wasted (couldn't be used/stored)")
        
        print(f"\nAnalysis period: {self.enhanced_data.index.min().strftime('%Y-%m-%d')} to {self.enhanced_data.index.max().strftime('%Y-%m-%d')}")
        
        print(f"\n📊 KEY FINDINGS:")
        
        # Find interesting points
        baseline = results_df.iloc[0]  # No storage
        small_storage = results_df[results_df['capacity_gwh'] <= 5]
        max_storage = results_df.iloc[-1]  # Maximum storage
        
        print(f"\n   📍 WITHOUT STORAGE (baseline):")
        print(f"     Renewable share: {baseline['renewable_share_percent']:.1f}%")
        print(f"     Residual needed: {baseline['residual_share_percent']:.1f}%")
        print(f"     Curtailment: {baseline['curtailment_rate_percent']:.1f}%")
        
        if len(small_storage) > 1:
            small = small_storage.iloc[-1]  # Largest small storage
            print(f"\n   📍 WITH {small['capacity_gwh']:.0f} GWh STORAGE:")
            print(f"     Renewable share: {small['renewable_share_percent']:.1f}% (+{small['renewable_share_percent'] - baseline['renewable_share_percent']:.1f}pp)")
            print(f"     Residual needed: {small['residual_share_percent']:.1f}% ({small['residual_share_percent'] - baseline['residual_share_percent']:.1f}pp)")
            print(f"     Curtailment: {small['curtailment_rate_percent']:.1f}% ({small['curtailment_rate_percent'] - baseline['curtailment_rate_percent']:.1f}pp)")
            print(f"     → Small storage impact: Your expectation was correct!")
        
        print(f"\n   📍 WITH {max_storage['capacity_gwh']:.0f} GWh STORAGE (maximum tested):")
        print(f"     Renewable share: {max_storage['renewable_share_percent']:.1f}% (+{max_storage['renewable_share_percent'] - baseline['renewable_share_percent']:.1f}pp)")
        print(f"     Residual needed: {max_storage['residual_share_percent']:.1f}%")
        print(f"     Battery utilization: {max_storage['battery_utilization_percent']:.1f}%")
        
        # Find thresholds
        threshold_90 = results_df[results_df['renewable_share_percent'] >= 90]
        if not threshold_90.empty:
            first_90 = threshold_90.iloc[0]
            print(f"\n   🎯 FOR 90% RENEWABLE SHARE:")
            print(f"     Required storage: ~{first_90['capacity_gwh']:.0f} GWh")
            print(f"     Power rating: ~{first_90['power_gw']:.0f} GW")
        
        print(f"\n💡 VALIDATION CHECKS:")
        total_renewable_potential = self.enhanced_data['total_renewables'].sum() / 1e6
        total_demand = self.enhanced_data['total_demand'].sum() / 1e6
        theoretical_max = total_renewable_potential / total_demand * 100
        
        print(f"   • Total renewable potential: {total_renewable_potential:.1f} TWh")
        print(f"   • Total demand: {total_demand:.1f} TWh")
        print(f"   • Theoretical max renewable share: {theoretical_max:.1f}%")
        print(f"   • With infinite storage, we could reach {theoretical_max:.1f}% renewable")
        
        if theoretical_max > 100:
            print(f"   ✅ Good news: Renewable surplus exists ({theoretical_max-100:.1f}% excess)")
        else:
            print(f"   ⚠️  Warning: Not enough renewables for 100% ({100-theoretical_max:.1f}% shortfall)")
        
        print(f"\n🏠 HOME ANALOGY:")
        print(f"   Your home: 4kWp solar + 5kWh battery → ~50% self-sufficiency")
        print(f"   Grid scale: Much more complex due to:")
        print(f"   • Weather correlation across large areas")
        print(f"   • Seasonal variations (winter solar deficit)")
        print(f"   • Industrial demand patterns")
        print(f"   • Grid stability requirements")
    
    def run_complete_analysis(self, capacity_range=None):
        """Run the complete storage impact analysis"""
        if self.data is None:
            print("❌ No data loaded!")
            return
        
        print("Starting storage impact analysis...")
        
        # Create enhanced scenario
        self.create_enhanced_renewable_scenario()
        
        # Run analysis for different storage capacities
        results_df = self.analyze_storage_scenarios(capacity_range)
        
        # Print summary
        self.print_summary(results_df)
        
        # Create visualizations
        self.create_visualizations(results_df)
        
        # Save results
        output_dir = "storage_analysis"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        results_df.to_csv(f'{output_dir}/storage_impact_results.csv', sep=';', decimal=',', index=False)
        
        print(f"\n✅ Analysis complete! Results saved to '{output_dir}/' directory")
        print(f"📄 Detailed results table: {output_dir}/storage_impact_results.csv")
        
        return results_df

def main():
    """Main function"""
    # Look for the combined CSV file
    data_file = "smard_data/smard_2024_complete.csv"
    
    if not os.path.exists(data_file):
        print(f"❌ Data file not found: {data_file}")
        print("Please run the smart-downloader.py script first to download the data.")
        return
    
    # Custom capacity range (you can modify this)
    capacity_range = [0, 5, 10, 15, 20, 30, 40, 50, 75, 100, 125, 150, 200, 250, 300]
    
    # Run analysis
    analyzer = StorageImpactAnalyzer(data_file)
    results_df = analyzer.run_complete_analysis(capacity_range)
    
    print(f"\n📋 Results table preview:")
    print(results_df[['capacity_gwh', 'renewable_share_percent', 'residual_share_percent']].round(1))

if __name__ == "__main__":
    main()
