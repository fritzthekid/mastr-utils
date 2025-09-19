#!/usr/bin/env python3
"""
Korrigierte Batterie-Simulation
Behebt logische Probleme der ursprünglichen Funktion
"""

import pandas as pd
import numpy as np
# from meine_analyse import Analyse, MeineAnalyse

class BatterySimulation:

    def __init__():
        pass

    def load_strategie(self, energy_balance, current_storage, capacity, avrgprice, price):
        if not self.basic_data_set["fix_contract"]:
            if price < 0 or price < 0.5*avrgprice or (price < avrgprice and energy_balance > 0):
                return True
            else:
                return False
        return energy_balance > 0
    
    def unload_strategie(self, energy_balance, current_storage, capacity, avrgprice, price):
        if not self.basic_data_set["fix_contract"]:
            if price > 0 and price > 1.5*avrgprice or (price > avrgprice and energy_balance < 0):
                return True
            else:
                return False
        return energy_balance < 0

    def simulate_battery(self, capacity=20000, power=10000):
        """
        Simuliere Batterie (Kapazität in kWh, power in kW pro Stunde).
        Erwartet:
          self.data["my_renew"], self.data["my_demand"], self.data["price_per_kwh"], self.data["avrgprice"]
          self.costs_per_kwh (€/kWh)
        Ergebnis: füllt self.data mit battery_storage/residual/exflow und aktualisiert self.battery_results
        """
        # Checks
        if not hasattr(self, 'data'):
            raise ValueError("self.data existiert nicht")
        for col in ("my_renew", "my_demand", "price_per_kwh", "avrgprice"):
            if col not in self.data:
                raise ValueError(f"{col} fehlt in self.data")

        n = len(self.data["my_renew"])
        renew = np.array(self.data["my_renew"], dtype=float)
        demand = np.array(self.data["my_demand"], dtype=float)
        price = np.array(self.data["price_per_kwh"], dtype=float)   # €/kWh
        avrgprice = np.array(self.data["avrgprice"], dtype=float)   # €/kWh

        storage_levels = np.zeros(n, dtype=float)
        residuals = np.zeros(n, dtype=float)
        exflows = np.zeros(n, dtype=float)
        battery_inflows = np.zeros(n, dtype=float)
        battery_outflows = np.zeros(n, dtype=float)

        current_storage = capacity * 0.5  # Start 50% of capacity

        power_per_step = power * self.resolution
        # battery_discharge: fraction per hour (0..1). Default 0 (kein Verlust).
        bd = getattr(self, "battery_discharge", 0.0)
        bd = float(bd) if bd is not None else 0.0
        # Begrenze auf 0..1
        bd = max(0.0, min(1.0, bd))

        for i in range(n):
            energy_balance = renew[i] - demand[i]   # kWh (positiv = Überschuss)
            inflow = 0.0
            outflow = 0.0
            residual = 0.0
            exflow = 0.0

            # Ladevorgang
            if energy_balance > 0:
                if self.load_strategie(energy_balance, current_storage, capacity, avrgprice[i], price[i]):
                    max_charge = min(power_per_step, capacity - current_storage)   # power_per_step ~ kW / 1h => kWh
                    actual_charge = min(energy_balance, max_charge)
                    if actual_charge > 0:
                        inflow = actual_charge
                        current_storage += actual_charge
                    exflow = energy_balance - actual_charge
                else:
                    # nicht laden, alles überschüssige wird abgegeben
                    exflow = energy_balance

            # Entladevorgang
            elif energy_balance < 0:
                if self.unload_strategie(energy_balance, current_storage, capacity, avrgprice[i], price[i]):
                    needed = abs(energy_balance)
                    max_discharge = min(power_per_step, current_storage)
                    actual_discharge = min(needed, max_discharge)
                    if actual_discharge > 0:
                        outflow = actual_discharge
                        current_storage -= actual_discharge
                        residual = needed - actual_discharge
                    else:
                        residual = needed
                else:
                    residual = abs(energy_balance)

            # Verluste / Selbstentladung am Ende des Schritts
            if bd > 0:
                current_storage = max(0.0, current_storage * (1.0 - bd))
            current_storage = min(capacity, current_storage)

            storage_levels[i] = current_storage
            residuals[i] = residual
            exflows[i] = exflow
            battery_inflows[i] = inflow
            battery_outflows[i] = outflow

        # Ergebnisse speichern (arrays in DataFrame/Series)
        self.data["battery_storage"] = storage_levels
        self.data["residual"] = residuals
        self.data["exflow"] = exflows
        self.data["battery_inflow"] = battery_inflows
        self.data["battery_outflow"] = battery_outflows

        # Aggregationen
        total_demand_kwh = demand.sum()
        autarky_rate = 1.0 - (residuals.sum() / total_demand_kwh) if total_demand_kwh > 0 else 1.0

        # Preise: Preisfelder sind €/kWh; resultate in Euro
        spot_total_eur = float((residuals * price).sum())      # Euro
        fix_total_eur = float(residuals.sum() * self.costs_per_kwh)  # Euro

        # Für Ausgabe in T€ (tausend €)
        spot_tk = spot_total_eur
        fix_tk = fix_total_eur

        results = pd.DataFrame([[
            capacity,
            residuals.sum(),
            exflows.sum(),
            autarky_rate,
            spot_tk,
            fix_tk
        ]], columns=["capacity kWh","residual kWh","exflow kWh", "autarky rate", "spot price [€]", "fix price [€]"])

        if getattr(self, "battery_results", None) is None:
            self.battery_results = results
        else:
            self.battery_results = pd.concat([self.battery_results, results], ignore_index=True)

        return {
            "autarky_rate": autarky_rate,
            "spot_total_eur": spot_total_eur,
            "fix_total_eur": fix_total_eur
        }

    # Zusätzliche Hilfsfunktionen für Validierung und Analyse

    def validate_battery_parameters(self,capacity, power):
        """Validiert Batterie-Parameter"""
        if capacity <= 0:
            raise ValueError(f"Batteriekapazität muss positiv sein: {capacity}")
        if power <= 0:
            raise ValueError(f"Batterieleistung muss positiv sein: {power}")
        if power > capacity:
            print(f"⚠️  Warnung: Batterieleistung ({power} kW) > Kapazität ({capacity} kWh)")
            print(f"   Das bedeutet C-Rate > 1 (sehr schnelle Batterie)")

    def analyze_battery_efficiency(self, storage_levels, inflows, outflows):
        """Analysiert Batterieeffizienz"""
        total_inflow = sum(inflows)
        total_outflow = sum(outflows)
        
        if total_inflow > 0:
            efficiency = total_outflow / total_inflow
            print(f"   Batterieeffizienz: {efficiency*100:.1f}% (idealisiert)")
        
        cycles = sum(inflows) / (max(storage_levels) - min(storage_levels)) if max(storage_levels) > min(storage_levels) else 0
        print(f"   Äquivalente Vollzyklen: {cycles:.1f}")

    # Beispiel für erweiterte Simulation mit verschiedenen Batterien
    def run_battery_comparison(self, capacities=[10000, 20000, 50000], power_factor=0.5):
        """Vergleicht verschiedene Batteriekapazitäten"""
        
        print("🔋 Batterie-Vergleichsanalyse")
        print("="*50)
        
        # Lösche vorherige Ergebnisse
        self.battery_results = pd.DataFrame()
        
        for capacity in capacities:
            power = capacity * power_factor  # Power als Anteil der Kapazität
            print(f"\n--- Simulation: {capacity/1000:.1f} MWh / {power/1000:.1f} MW ---")
            
            self.validate_battery_parameters(capacity, power)
            result = self.simulate_battery(capacity, power)
            
            # Effizienz-Analyse
            if 'battery_inflow' in self.data and 'battery_outflow' in self.data:
                self.analyze_battery_efficiency(
                    self.data['battery_storage'], 
                    self.data['battery_inflow'], 
                    self.data['battery_outflow']
                )
        
        print(f"\n📋 Vergleichstabelle:")
        print(self.battery_results.round(2))
        
        return self.battery_results

# Einzelne Simulation

# result = simulate_battery(self, capacity=20000, power=10000)

# # Batterie-Vergleich
# comparison = run_battery_comparison(self, 
#     capacities=[10000, 20000, 50000], 
#     power_factor=0.5)