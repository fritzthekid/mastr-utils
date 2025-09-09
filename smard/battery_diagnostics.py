#!/usr/bin/env python3
"""
Battery Storage Diagnostics
Deep dive analysis to understand why large batteries still leave 13% residual
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

def load_smard_data(csv_file_path):
    """Load and prepare SMARD data with detailed inspection"""
    print("Loading and inspecting SMARD data...")
    
    df = pd.read_csv(csv_file_path, sep=';', decimal=',')
    
    print(f"Raw data shape: {df.shape}")
    print(f"Date range: {df['Datum'].min()} to {df['Datum'].max()}")
    print(f"\nColumn inspection:")
    
    # Create datetime column
    df['DateTime'] = pd.to_datetime(df['Datum'] + ' ' + df['Uhrzeit'])
    df = df.set_index('DateTime')
    
    # Find energy columns
    energy_cols = [col for col in df.columns if '[MWh]' in col]
    print(f"Found {len(energy_cols)} energy columns:")
    
    for col in energy_cols:
        non_null = df[col].notna().sum()
        total_energy = df[col].sum()
        print(f"  {col}: {non_null:,} non-null values, {total_energy/1000:.0f} GWh total")
    
    return df[energy_cols].fillna(0), energy_cols

def create_enhanced_scenario(df):
    """Create doubled renewable scenario with detailed tracking"""
    print(f"\n" + "="*60)
    print("CREATING ENHANCED RENEWABLE SCENARIO")
    print("="*60)
    
    scenario = df.copy()
    
    # Map columns
    renewables = {}
    conventional = {}
    demand = None
    
    for col in df.columns:
        if 'Wind Onshore' in col:
            renewables['wind_onshore'] = col
        elif 'Wind Offshore' in col:
            renewables['wind_offshore'] = col
        elif 'Photovoltaik' in col:
            renewables['solar'] = col
        elif 'Wasserkraft' in col:
            renewables['hydro'] = col
        elif 'Biomasse' in col:
            renewables['biomass'] = col
        elif 'Braunkohle' in col:
            conventional['lignite'] = col
        elif 'Steinkohle' in col:
            conventional['coal'] = col
        elif 'Erdgas' in col:
            conventional['gas'] = col
        elif 'Kernenergie' in col:
            conventional['nuclear'] = col
        elif 'Gesamtverbrauch' in col or 'Netzlast' in col:
            demand = col
        elif 'Sonstige' in col:
            if 'Erneuerbare' in col:
                renewables['other_renewable'] = col
            elif 'Konventionelle' in col:
                conventional['other_conventional'] = col
    
    print(f"\nMapped renewables: {list(renewables.keys())}")
    print(f"Mapped conventional: {list(conventional.keys())}")
    print(f"Demand column: {demand}")
    
    # Calculate original totals
    original_renewable_total = 0
    original_conventional_total = 0
    
    print(f"\nORIGINAL ENERGY BREAKDOWN:")
    for name, col in renewables.items():
        if col in scenario.columns:
            total = scenario[col].sum() / 1000  # Convert to GWh
            original_renewable_total += total
            print(f"  {name}: {total:.0f} GWh")
    
    for name, col in conventional.items():
        if col in scenario.columns:
            total = scenario[col].sum() / 1000
            original_conventional_total += total
            print(f"  {name}: {total:.0f} GWh")
    
    total_demand_energy = scenario[demand].sum() / 1000 if demand else 0
    print(f"\nTotal demand: {total_demand_energy:.0f} GWh")
    print(f"Original renewable: {original_renewable_total:.0f} GWh ({original_renewable_total/total_demand_energy*100:.1f}%)")
    print(f"Original conventional: {original_conventional_total:.0f} GWh ({original_conventional_total/total_demand_energy*100:.1f}%)")
    
    # Double wind and solar
    enhanced_renewable_total = original_renewable_total
    
    print(f"\nDOUBLING WIND AND SOLAR:")
    for name, col in renewables.items():
        if name in ['wind_onshore', 'wind_offshore', 'solar'] and col in scenario.columns:
            original = scenario[col].sum() / 1000
            scenario[col] *= 2
            doubled = scenario[col].sum() / 1000
            enhancement = doubled - original
            enhanced_renewable_total += enhancement
            print(f"  {name}: {original:.0f} → {doubled:.0f} GWh (+{enhancement:.0f} GWh)")
    
    print(f"\nENHANCED TOTALS:")
    print(f"Enhanced renewable: {enhanced_renewable_total:.0f} GWh ({enhanced_renewable_total/total_demand_energy*100:.1f}%)")
    print(f"Conventional unchanged: {original_conventional_total:.0f} GWh ({original_conventional_total/total_demand_energy*100:.1f}%)")
    
    theoretical_max = enhanced_renewable_total / total_demand_energy * 100
    print(f"\nTHEORETICAL MAXIMUM RENEWABLE SHARE: {theoretical_max:.1f}%")
    
    if theoretical_max < 100:
        print(f"⚠️  WARNING: Even with infinite storage, max renewable share is {theoretical_max:.1f}%")
        print(f"   This means {100-theoretical_max:.1f}% will always need conventional sources!")
    else:
        print(f"✅ Good: Sufficient renewables for >100% coverage ({theoretical_max:.1f}%)")
        print(f"   Excess renewable capacity: {theoretical_max-100:.1f}%")
    
    return scenario, renewables, conventional, demand, theoretical_max

def analyze_seasonal_patterns(df, renewables, conventional, demand):
    """Analyze seasonal and daily patterns"""
    print(f"\n" + "="*60)
    print("SEASONAL & TEMPORAL ANALYSIS")
    print("="*60)
    
    # Calculate totals
    renewable_cols = [col for col in renewables.values() if col in df.columns]
    conventional_cols = [col for col in conventional.values() if col in df.columns]
    
    df['total_renewables'] = df[renewable_cols].sum(axis=1)
    df['total_conventional'] = df[conventional_cols].sum(axis=1)
    df['total_demand'] = df[demand]
    df['energy_balance'] = df['total_renewables'] - df['total_demand']
    
    # Monthly analysis
    monthly = df.resample('M').agg({
        'total_renewables': 'sum',
        'total_demand': 'sum',
        'energy_balance': 'sum'
    })
    
    monthly['renewable_share'] = monthly['total_renewables'] / monthly['total_demand'] * 100
    monthly['deficit'] = np.maximum(0, -monthly['energy_balance'])
    
    print(f"\nMONTHLY RENEWABLE SHARE:")
    for month, row in monthly.iterrows():
        print(f"  {month.strftime('%Y-%m')}: {row['renewable_share']:5.1f}% renewable, {row['deficit']/1000:6.0f} GWh deficit")
    
    # Find worst periods
    daily = df.resample('D').agg({
        'total_renewables': 'sum',
        'total_demand': 'sum',
        'energy_balance': 'sum'
    })
    daily['renewable_share'] = daily['total_renewables'] / daily['total_demand'] * 100
    
    worst_days = daily.nsmallest(10, 'renewable_share')
    print(f"\nWORST 10 DAYS FOR RENEWABLES:")
    for date, row in worst_days.iterrows():
        deficit = max(0, -row['energy_balance'])
        print(f"  {date.strftime('%Y-%m-%d')}: {row['renewable_share']:5.1f}% renewable, {deficit:.0f} MWh deficit")
    
    # Check for long deficit periods
    deficit_streaks = []
    current_streak = 0
    current_deficit = 0
    
    for balance in df['energy_balance']:
        if balance < 0:
            current_streak += 1
            current_deficit += abs(balance)
        else:
            if current_streak > 0:
                deficit_streaks.append((current_streak, current_deficit))
            current_streak = 0
            current_deficit = 0
    
    if current_streak > 0:
        deficit_streaks.append((current_streak, current_deficit))
    
    deficit_streaks.sort(key=lambda x: x[1], reverse=True)  # Sort by total deficit
    
    print(f"\nLONGEST DEFICIT PERIODS:")
    for i, (hours, total_deficit) in enumerate(deficit_streaks[:5]):
        days = hours / 24
        print(f"  {i+1}. {hours} hours ({days:.1f} days): {total_deficit/1000:.0f} GWh total deficit")
    
    return df

def test_extreme_battery(df):
    """Test what happens with extremely large battery"""
    print(f"\n" + "="*60)
    print("EXTREME BATTERY TEST")
    print("="*60)
    
    # Test with massive battery capacity
    extreme_capacity = 1000  # 1000 GWh = 1 TWh
    extreme_power = 200  # 200 GW
    
    print(f"Testing {extreme_capacity} GWh battery with {extreme_power} GW power...")
    
    battery_level = np.zeros(len(df))
    battery_charge = np.zeros(len(df))
    
    capacity_mwh = extreme_capacity * 1000
    power_mw = extreme_power * 1000
    
    for i in range(len(df)):
        if i == 0:
            battery_level[i] = capacity_mwh / 2  # Start at 50%
        else:
            battery_level[i] = battery_level[i-1]
        
        balance = df['energy_balance'].iloc[i]
        
        if balance > 0:  # Surplus
            max_charge = min(balance, power_mw, capacity_mwh - battery_level[i])
            battery_charge[i] = max_charge
            battery_level[i] += max_charge
        elif balance < 0:  # Deficit
            max_discharge = min(abs(balance), power_mw, battery_level[i])
            battery_charge[i] = -max_discharge
            battery_level[i] -= max_discharge
    
    # Calculate remaining deficits
    remaining_deficits = []
    for i, balance in enumerate(df['energy_balance']):
        after_battery = balance + battery_charge[i]  # Charge is negative when discharging
        if after_battery < 0:
            remaining_deficits.append((df.index[i], abs(after_battery)))
    
    total_remaining_deficit = sum([deficit for _, deficit in remaining_deficits])
    total_demand = df['total_demand'].sum()
    remaining_residual_share = total_remaining_deficit / total_demand * 100
    
    print(f"\nRESULTS WITH {extreme_capacity} GWh BATTERY:")
    print(f"Remaining deficits: {len(remaining_deficits)} hours")
    print(f"Total remaining deficit: {total_remaining_deficit/1000:.0f} GWh")
    print(f"Remaining residual share: {remaining_residual_share:.1f}%")
    
    if remaining_residual_share > 5:
        print(f"\n⚠️  Even with {extreme_capacity} GWh battery, {remaining_residual_share:.1f}% residual remains!")
        print("This suggests fundamental renewable shortage, not battery limitation.")
        
        print(f"\nWORST REMAINING DEFICITS:")
        remaining_deficits.sort(key=lambda x: x[1], reverse=True)
        for i, (timestamp, deficit) in enumerate(remaining_deficits[:10]):
            print(f"  {timestamp.strftime('%Y-%m-%d %H:%M')}: {deficit:.0f} MWh deficit")
    
    return remaining_residual_share

def main():
    """Run complete diagnostics"""
    data_file = "smard_data/smard_2024_complete.csv"
    
    if not os.path.exists(data_file):
        print(f"❌ Data file not found: {data_file}")
        return
    
    # Load and inspect data
    df, energy_cols = load_smard_data(data_file)
    
    # Create enhanced scenario
    enhanced_df, renewables, conventional, demand, theoretical_max = create_enhanced_scenario(df)
    
    # Analyze patterns
    analyzed_df = analyze_seasonal_patterns(enhanced_df, renewables, conventional, demand)
    
    # Test extreme battery
    remaining_residual = test_extreme_battery(analyzed_df)
    
    print(f"\n" + "="*60)
    print("DIAGNOSTIC SUMMARY")
    print("="*60)
    print(f"Theoretical max renewable share: {theoretical_max:.1f}%")
    print(f"With 1000 GWh battery: {100-remaining_residual:.1f}% renewable")
    print(f"Fundamental limitation: {remaining_residual:.1f}% always needs conventional")
    
    if theoretical_max < 100:
        print(f"\n💡 CONCLUSION: The 13% residual is likely correct!")
        print(f"   Even with doubled renewables, Germany has {100-theoretical_max:.1f}% structural deficit")
        print(f"   This is due to seasonal patterns and renewable intermittency")
    else:
        print(f"\n🔍 CONCLUSION: There might be a simulation bug")
        print(f"   Theoretical max is {theoretical_max:.1f}%, but extreme battery still leaves {remaining_residual:.1f}%")

if __name__ == "__main__":
    main()
