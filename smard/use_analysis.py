from energy_storage_analysis import StorageImpactAnalyzer

# Quick test
analyzer = StorageImpactAnalyzer("smard_data/smard_2024_complete.csv")
analyzer.create_enhanced_renewable_scenario()

# Test small range with debug output
results = analyzer.analyze_storage_scenarios([0, 1, 2, 5, 100, 200, 300])
print("\nQuick results:")
for i, row in results.iterrows():
    print(f"{row['capacity_gwh']:3.0f} GWh → {row['renewable_share_percent']:5.2f}% renewable, {row['residual_share_percent']:5.2f}% residual")

pass