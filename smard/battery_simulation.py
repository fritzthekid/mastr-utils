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

    def load_strategie(self, energy_balance, current_storage, capacity, price_below_average):
        if energy_balance <= 0:
            return False
        return True

    def unload_strategie(self, energy_balance, current_storage, capacity, price_below_average):
        return energy_balance < 0

    def simulate_battery(self, capacity=20000, power=10000):
        """
        Simuliert das Verhalten einer Batterie über einen Zeitraum
        
        Parameter:
        - capacity [kWh]: Batteriekapazität
        - power [kW]: Maximum Lade-/Entladeleistung pro Stunde
        - verwendet self.data["my_renew"] und self.data["my_demand"]
        
        Berechnet:
        - storage_level (Füllstand) [kWh]
        - residual (ungedeckter Bedarf) [kWh] 
        - exflow (überschüssige Energie) [kWh]
        - battery flows (Ein-/Ausfluss) [kWh]
        
        Logik:
        1. Energiebalance = erneuerbare - Nachfrage
        2. Bei Überschuss: Batterie laden (falls möglich)
        3. Bei Defizit: Batterie entladen (falls möglich)
        4. Residual = ungedeckter Bedarf nach Batterieentladung
        5. Exflow = nicht speicherbare überschüssige Energie
        """
        
        # Listen für Ergebnisse initialisieren
        storage_levels = []          # Füllstand der Batterie
        residuals = []              # Ungedeckter Bedarf
        exflows = []               # Nicht speicherbare Überschüsse
        battery_inflows = []       # Energie in Batterie (positiv)
        battery_outflows = []      # Energie aus Batterie (positiv)
        
        # Startfüllstand: 50% der Kapazität
        current_storage = capacity / 2
        
        # Validierung der Eingabedaten
        if not hasattr(self, 'data'):
            raise ValueError("self.data existiert nicht")
        if 'my_renew' not in self.data or 'my_demand' not in self.data:
            raise ValueError("my_renew oder my_demand fehlen in self.data")
        if len(self.data['my_renew']) != len(self.data['my_demand']):
            raise ValueError("my_renew und my_demand haben unterschiedliche Längen")
        
        print(f"Simulation: {capacity/1000:.1f} MWh Kapazität, {power/1000:.1f} MW Leistung")
        print(f"Datenpunkte: {len(self.data['my_renew'])}")
        
        # Hauptschleife: Iteriere über alle Zeitpunkte
        for i, (renewable, demand, load) in enumerate(zip(self.data["my_renew"], self.data["my_demand"], self.data["loadstrategy"])):
            
            # Energiebalance berechnen (kWh)
            energy_balance = renewable - demand
            
            # Initialisierung für diesen Zeitschritt
            battery_inflow = 0
            battery_outflow = 0
            residual = 0
            exflow = 0
            
            if energy_balance > 0 and (True or current_storage < 0.3*capacity or load):
                # ÜBERSCHUSS: Versuche Batterie zu laden and price < average)
                
                # Maximale Ladeleistung berechnen
                max_charge_power = min(power, capacity - current_storage)  # Begrenzung durch Kapazität
                actual_charge = min(energy_balance, max_charge_power)      # Begrenzung durch verfügbare Energie
                
                if actual_charge > 0:
                    battery_inflow = actual_charge
                    current_storage += actual_charge
                    
                    # Überschüssige Energie, die nicht gespeichert werden kann
                    exflow = energy_balance - actual_charge
                else:
                    # Batterie voll, alle überschüssige Energie geht verloren
                    exflow = energy_balance
            
            elif energy_balance < 0 and (True or current_storage > 0.3*capacity or not load):
                # DEFIZIT: Versuche Batterie zu entladen and price high
                
                needed_energy = abs(energy_balance)
                
                # Maximale Entladeleistung berechnen
                max_discharge_power = min(power, current_storage)         # Begrenzung durch Speicherinhalt
                actual_discharge = min(needed_energy, max_discharge_power) # Begrenzung durch benötigte Energie
                
                if actual_discharge > 0:
                    battery_outflow = actual_discharge
                    current_storage -= actual_discharge
                    
                    # Restlicher ungedeckter Bedarf
                    residual = needed_energy - actual_discharge
                else:
                    # Batterie leer, kompletter Bedarf ist ungedeckt
                    residual = needed_energy
            
            # Ergebnisse speichern
            storage_levels.append(current_storage)
            residuals.append(residual)
            exflows.append(exflow)
            battery_inflows.append(battery_inflow)
            battery_outflows.append(battery_outflow)
            
            # Debug-Output für erste paar Iterationen
            # if i < 5:
            #     print(f"  Stunde {i:2d}: Renewable={renewable:6.0f}, Demand={demand:6.0f}, "
            #         f"Balance={energy_balance:6.0f}, Storage={current_storage:6.0f}, "
            #         f"In={battery_inflow:4.0f}, Out={battery_outflow:4.0f}, "
            #         f"Residual={residual:4.0f}, Exflow={exflow:4.0f}")
        
        # Ergebnisse in self.data speichern
        self.data["battery_storage"] = storage_levels
        self.data["residual"] = residuals
        self.data["exflow"] = exflows
        self.data["battery_inflow"] = battery_inflows
        self.data["battery_outflow"] = battery_outflows  # Konsistente Benennung

        # Berechnung der Ergebnisse (from orginal)
        autarky_rate = 1 - (sum(residuals) / sum(self.data["my_demand"])) if sum(self.data["my_demand"]) > 0 else 1
        # share = (sum(self.data["my_demand"]) + sum(residuals))/sum(self.data["my_demand"])
        # share = (sum(residuals))/sum(self.data["my_demand"])
        spot_price = sum(residuals*self.data["price_per_kwh"])/100
        fix_price = sum(residuals)*self.costs_per_kwh/100
        results = pd.DataFrame([[capacity/1000,f"{(sum(residuals)/1000):.2f}",f"{(sum(exflows)/1000):.2f}", f"{autarky_rate:.2f}",f"{(spot_price/1000):.2f}",f"{(fix_price/1000):.2f}"]], 
                               columns=["capacity MWh","residual MWh","exflow MWh", "autarky rate", "spot price [T€]", "fix price [T€]"])
        self.battery_results = pd.concat([self.battery_results, results], ignore_index=True)
        pass
        # # Gesamtstatistiken berechnen
        # total_demand = sum(self.data["my_demand"])
        # total_residual = sum(residuals)
        # total_exflow = sum(exflows)
        # total_renewable = sum(self.data["my_renew"])
        
        # # Selbstversorgungsgrad
        # self_sufficiency_share = (total_demand - total_residual) / total_demand if total_demand > 0 else 0
        
        # # Autarkiegrad (umgekehrt zum residual share)
        # autarky_rate = 1 - (total_residual / total_demand) if total_demand > 0 else 1
        
        # # Eigenverbrauchsanteil
        # self_consumption_rate = (total_renewable - total_exflow) / total_renewable if total_renewable > 0 else 0
        
        # # Kosten berechnen (falls price_per_kwh vorhanden)
        # spot_price_cost = 0
        # fix_price_cost = 0
        
        # if hasattr(self.data, 'price_per_kwh') and 'price_per_kwh' in self.data:
        #     # Spotpreis-Kosten für Residualstrom
        #     if len(self.data['price_per_kwh']) == len(residuals):
        #         spot_price_cost = sum(r * p for r, p in zip(residuals, self.data['price_per_kwh'])) / 100
        
        # if hasattr(self, 'costs_per_kwh'):
        #     # Fixpreis-Kosten für Residualstrom  
        #     fix_price_cost = total_residual * self.costs_per_kwh / 100
        
        # # Ergebnis-DataFrame erstellen
        # result_row = {
        #     "capacity_mwh": capacity / 1000,
        #     "residual_mwh": total_residual / 1000,
        #     "exflow_mwh": total_exflow / 1000,
        #     "self_sufficiency_pct": self_sufficiency_share * 100,
        #     "autarky_rate_pct": autarky_rate * 100,
        #     "self_consumption_pct": self_consumption_rate * 100,
        #     "spot_price_k_euro": spot_price_cost / 1000,
        #     "fix_price_k_euro": fix_price_cost / 1000,
        #     "avg_storage_pct": np.mean(storage_levels) / capacity * 100,
        #     "min_storage_mwh": min(storage_levels) / 1000,
        #     "max_storage_mwh": max(storage_levels) / 1000
        # }
        
        # results_df = pd.DataFrame([result_row])
        
        # # An bestehende Ergebnisse anhängen
        # if hasattr(self, 'battery_results') and self.battery_results is not None:
        #     self.battery_results = pd.concat([self.battery_results, results_df], ignore_index=True)
        # else:
        #     self.battery_results = results_df
        
        # # Zusammenfassung ausgeben
        # print(f"\n📊 Simulationsergebnisse:")
        # print(f"   Batteriekapazität: {capacity/1000:.1f} MWh")
        # print(f"   Selbstversorgung: {autarky_rate*100:.1f}%")
        # print(f"   Eigenverbrauch: {self_consumption_rate*100:.1f}%")
        # print(f"   Residualstrom: {total_residual/1000:.1f} MWh")
        # print(f"   Überschuss: {total_exflow/1000:.1f} MWh")
        # print(f"   Mittlerer Füllstand: {np.mean(storage_levels)/capacity*100:.1f}%")
        
        # return {
        #     'total_residual_mwh': total_residual / 1000,
        #     'total_exflow_mwh': total_exflow / 1000,
        #     'autarky_rate': autarky_rate,
        #     'self_consumption_rate': self_consumption_rate
        # }


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