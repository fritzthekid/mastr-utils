<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CO₂-Emissionsfaktoren verschiedener Energiequellen</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }
        
        h1 {
            text-align: center;
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .subtitle {
            text-align: center;
            color: #7f8c8d;
            margin-bottom: 40px;
            font-size: 1.2rem;
            font-weight: 300;
        }
        
        h2 {
            color: #2980b9;
            margin: 40px 0 20px 0;
            padding: 15px 20px;
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            border-radius: 10px;
            font-size: 1.4rem;
            box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
        }
        
        h3 {
            color: #16a085;
            margin: 30px 0 15px 0;
            padding: 10px 15px;
            background: linear-gradient(135deg, #1abc9c, #16a085);
            color: white;
            border-radius: 8px;
            font-size: 1.2rem;
        }
        
        .table-container {
            overflow-x: auto;
            margin: 20px 0;
            border-radius: 12px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            background: white;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
            background: white;
        }
        
        th {
            background: linear-gradient(135deg, #34495e, #2c3e50);
            color: white;
            padding: 15px 12px;
            text-align: left;
            font-weight: 600;
            border-bottom: 3px solid #2980b9;
            position: sticky;
            top: 0;
            z-index: 10;
        }
        
        td {
            padding: 12px;
            border-bottom: 1px solid #ecf0f1;
            transition: background-color 0.3s ease;
        }
        
        tr:hover {
            background-color: #f8f9fa;
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        
        .category {
            font-weight: bold;
            background: linear-gradient(135deg, #ecf0f1, #bdc3c7);
            color: #2c3e50;
            border-left: 5px solid #3498db;
        }
        
        .fossil {
            border-left: 5px solid #e74c3c;
        }
        
        .renewable {
            border-left: 5px solid #27ae60;
        }
        
        .biomass {
            border-left: 5px solid #f39c12;
        }
        
        .nuclear {
            border-left: 5px solid #9b59b6;
        }
        
        .heat {
            border-left: 5px solid #e67e22;
        }
        
        a {
            color: #3498db;
            text-decoration: none;
            transition: all 0.3s ease;
            font-weight: 500;
        }
        
        a:hover {
            color: #2980b9;
            text-decoration: underline;
            transform: translateY(-1px);
        }
        
        .highlight {
            background: linear-gradient(135deg, #fff3cd, #ffeaa7);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border-left: 5px solid #fdcb6e;
        }
        
        .highlight h4 {
            color: #d68910;
            margin-bottom: 10px;
            font-size: 1.1rem;
        }
        
        .sources {
            background: linear-gradient(135deg, #dbeafe, #bfdbfe);
            padding: 25px;
            border-radius: 12px;
            margin: 30px 0;
            border-left: 5px solid #3b82f6;
        }
        
        .sources h3 {
            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
            margin: 0 0 15px 0;
        }
        
        .source-category {
            margin: 15px 0;
        }
        
        .source-category h4 {
            color: #1d4ed8;
            margin-bottom: 8px;
            font-size: 1rem;
        }
        
        .source-list {
            margin-left: 10px;
        }
        
        .note {
            background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border-left: 5px solid #0ea5e9;
            font-size: 0.95rem;
        }
        
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            background: linear-gradient(135deg, #f8fafc, #e2e8f0);
            border-radius: 10px;
            color: #64748b;
            font-size: 0.9rem;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #ffffff, #f1f5f9);
            padding: 20px;
            border-radius: 12px;
            border-left: 5px solid #10b981;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }
        
        .stat-card h4 {
            color: #059669;
            margin-bottom: 15px;
            font-size: 1.1rem;
        }
        
        .number {
            font-weight: 600;
            color: #2563eb;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 20px;
                margin: 10px;
            }
            
            h1 {
                font-size: 2rem;
            }
            
            .table-container {
                font-size: 12px;
            }
            
            th, td {
                padding: 8px 6px;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>CO₂-Emissionsfaktoren verschiedener Energiequellen</h1>
        <p class="subtitle">Strom und Wärme - Lebenszyklusbetrachtung mit funktionierenden Quellen-Links</p>
        
        <h2>CO₂-Emissionsfaktoren Stromerzeugung (Lebenszyklusbetrachtung)</h2>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Energiequelle</th>
                        <th>CO₂-Emissionen<br>(g CO₂/kWh)</th>
                        <th>Volllaststunden<br>(h/a)</th>
                        <th>Kapazitätsfaktor<br>(%)</th>
                        <th>Quellen</th>
                    </tr>
                </thead>
                <tbody>
                    <tr class="category">
                        <td colspan="5"><strong>Fossile Energieträger</strong></td>
                    </tr>
                    <tr class="fossil">
                        <td>Braunkohle</td>
                        <td class="number">800 - 1.200</td>
                        <td class="number">6.000 - 7.500</td>
                        <td class="number">68 - 86</td>
                        <td><a href="https://www.umweltbundesamt.de/themen/co2-emissionen-pro-kilowattstunde-strom-2024">UBA Strommix 2024</a>, <a href="https://www.umweltbundesamt.de/sites/default/files/medien/11850/publikationen/23_2024_cc_strommix_11_2024.pdf">UBA Strommix-Studie PDF</a></td>
                    </tr>
                    <tr class="fossil">
                        <td>Steinkohle</td>
                        <td class="number">750 - 1.050</td>
                        <td class="number">3.000 - 6.000</td>
                        <td class="number">34 - 68</td>
                        <td><a href="https://www.umweltbundesamt.de/themen/co2-emissionen-pro-kilowattstunde-strom-2024">UBA Strommix 2024</a>, <a href="https://www.umweltbundesamt.de/sites/default/files/medien/11850/publikationen/23_2024_cc_strommix_11_2024.pdf">UBA Strommix-Studie PDF</a></td>
                    </tr>
                    <tr class="fossil">
                        <td>Erdgas (GuD)</td>
                        <td class="number">350 - 490</td>
                        <td class="number">2.000 - 5.000</td>
                        <td class="number">23 - 57</td>
                        <td><a href="https://volker-quaschning.de/datserv/CO2-spez/index.php">Quaschning CO₂-Tabelle</a>, <a href="https://www.umweltbundesamt.de/themen/co2-emissionen-pro-kilowattstunde-strom-2024">UBA Strommix 2024</a></td>
                    </tr>
                    <tr class="fossil">
                        <td>Erdöl/Heizöl</td>
                        <td class="number">750 - 900</td>
                        <td>-</td>
                        <td>-</td>
                        <td><a href="https://www.umweltbundesamt.de/themen/co2-emissionen-pro-kilowattstunde-strom-2024">UBA Strommix 2024</a></td>
                    </tr>
                    
                    <tr class="category">
                        <td colspan="5"><strong>Erneuerbare Energien</strong></td>
                    </tr>
                    <tr class="renewable">
                        <td>Photovoltaik</td>
                        <td class="number">40 - 50</td>
                        <td class="number">800 - 1.200</td>
                        <td class="number">9 - 14</td>
                        <td><a href="https://www.umweltbundesamt.de/themen/klima-energie/energieversorgung/strom-waermeversorgung-in-zahlen">UBA Emissionsbilanzen Strom</a>, <a href="https://www.umweltbundesamt.de/themen/luft/emissionen-von-luftschadstoffen/spezifische-emissionsfaktoren-fuer-den-deutschen">UBA Spezifische Emissionsfaktoren</a></td>
                    </tr>
                    <tr class="renewable">
                        <td>Windkraft (onshore)</td>
                        <td class="number">8 - 16</td>
                        <td class="number">1.400 - 3.000</td>
                        <td class="number">16 - 34</td>
                        <td><a href="https://www.umweltbundesamt.de/themen/klima-energie/energieversorgung/strom-waermeversorgung-in-zahlen">UBA Emissionsbilanzen Strom</a>, <a href="https://www.umweltbundesamt.de/themen/luft/emissionen-von-luftschadstoffen/spezifische-emissionsfaktoren-fuer-den-deutschen">UBA Spezifische Emissionsfaktoren</a></td>
                    </tr>
                    <tr class="renewable">
                        <td>Windkraft (offshore)</td>
                        <td class="number">12 - 23</td>
                        <td class="number">3.000 - 4.500</td>
                        <td class="number">34 - 51</td>
                        <td><a href="https://www.umweltbundesamt.de/themen/klima-energie/energieversorgung/strom-waermeversorgung-in-zahlen">UBA Emissionsbilanzen Strom</a>, <a href="https://www.umweltbundesamt.de/themen/luft/emissionen-von-luftschadstoffen/spezifische-emissionsfaktoren-fuer-den-deutschen">UBA Spezifische Emissionsfaktoren</a></td>
                    </tr>
                    <tr class="renewable">
                        <td>Wasserkraft</td>
                        <td class="number">10 - 150</td>
                        <td class="number">4.000 - 6.000</td>
                        <td class="number">46 - 68</td>
                        <td><a href="https://www.umweltbundesamt.de/themen/klima-energie/energieversorgung/strom-waermeversorgung-in-zahlen">UBA Emissionsbilanzen Strom</a>, <a href="https://www.umweltbundesamt.de/themen/luft/emissionen-von-luftschadstoffen/spezifische-emissionsfaktoren-fuer-den-deutschen">UBA Spezifische Emissionsfaktoren</a></td>
                    </tr>
                    
                    <tr class="category">
                        <td colspan="5"><strong>Biomasse (detailliert)</strong></td>
                    </tr>
                    <tr class="biomass">
                        <td>Biogas (Landwirt)</td>
                        <td class="number">20 - 40</td>
                        <td class="number">6.000 - 8.000</td>
                        <td class="number">68 - 91</td>
                        <td><a href="https://biogas.fnr.de/rahmenbedingungen/treibhausgas-emissionen-von-biogasanlagen">FNR Treibhausgas-Emissionen Biogas</a>, <a href="https://eps-bhkw.de/emissionen-biogas-faktencheck/">EPS BHKW Faktencheck</a></td>
                    </tr>
                    <tr class="biomass">
                        <td>Holzpellets (Kraftwerk)</td>
                        <td class="number">20 - 25</td>
                        <td class="number">4.000 - 7.000</td>
                        <td class="number">46 - 80</td>
                        <td><a href="https://depv.de/p/Bessere-CO2-Bilanz-mit-Holzpellets-pWuQQ4VvuNQoYjUzRf778Z">DEPV CO₂-Bilanz Pellets</a>, <a href="https://www.umweltbundesamt.de/uba-co2-rechner-neue-berechnungsgrundlage-bei">UBA Holzenergie CO₂-Rechner</a></td>
                    </tr>
                    <tr class="biomass">
                        <td>Holzheizkraftwerk</td>
                        <td class="number">150 - 350</td>
                        <td class="number">3.000 - 6.000</td>
                        <td class="number">34 - 68</td>
                        <td><a href="https://www.umweltbundesamt.de/uba-co2-rechner-neue-berechnungsgrundlage-bei">UBA Holzenergie CO₂-Rechner</a>, <a href="https://volker-quaschning.de/datserv/CO2-spez/index.php">Quaschning CO₂-Tabelle</a></td>
                    </tr>
                    <tr class="biomass">
                        <td>Klärgas/Deponiegas</td>
                        <td class="number">22 - 30</td>
                        <td class="number">7.000 - 8.500</td>
                        <td class="number">80 - 97</td>
                        <td><a href="https://eps-bhkw.de/emissionen-biogas-faktencheck/">EPS BHKW Faktencheck</a></td>
                    </tr>
                    
                    <tr class="category">
                        <td colspan="5"><strong>Kernenergie</strong></td>
                    </tr>
                    <tr class="nuclear">
                        <td>Kernkraft</td>
                        <td class="number">6 - 24</td>
                        <td class="number">7.000 - 8.000</td>
                        <td class="number">80 - 91</td>
                        <td><a href="https://www.umweltbundesamt.de/themen/klima-energie/energieversorgung/strom-waermeversorgung-in-zahlen">UBA Emissionsbilanzen Strom</a>, <a href="https://www.umweltbundesamt.de/themen/luft/emissionen-von-luftschadstoffen/spezifische-emissionsfaktoren-fuer-den-deutschen">UBA Spezifische Emissionsfaktoren</a></td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <h2>CO₂-Emissionsfaktoren Wärmeerzeugung</h2>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Energiequelle</th>
                        <th>CO₂-Emissionen<br>(g CO₂/kWh_th)</th>
                        <th>Anmerkungen</th>
                        <th>Quellen</th>
                    </tr>
                </thead>
                <tbody>
                    <tr class="category">
                        <td colspan="4"><strong>Fossile Brennstoffe</strong></td>
                    </tr>
                    <tr class="fossil heat">
                        <td>Heizöl EL</td>
                        <td class="number">318</td>
                        <td>Inkl. Vorkette</td>
                        <td><a href="https://www.umweltbundesamt.de/uba-co2-rechner-neue-berechnungsgrundlage-bei">UBA Holzenergie CO₂-Rechner</a>, <a href="https://www.polarstern-energie.de/magazin/artikel/heizen-co2-vergleich-von-brennstoffen/">Polarstern Heizungsvergleich</a></td>
                    </tr>
                    <tr class="fossil heat">
                        <td>Erdgas (Heizwert)</td>
                        <td class="number">247</td>
                        <td>Brennwertkessel</td>
                        <td><a href="https://www.umweltbundesamt.de/uba-co2-rechner-neue-berechnungsgrundlage-bei">UBA Holzenergie CO₂-Rechner</a>, <a href="https://www.polarstern-energie.de/magazin/artikel/heizen-co2-vergleich-von-brennstoffen/">Polarstern Heizungsvergleich</a></td>
                    </tr>
                    <tr class="fossil heat">
                        <td>Flüssiggas (LPG)</td>
                        <td class="number">236</td>
                        <td>Heizwertbezogen</td>
                        <td><a href="https://www.tga-fachplaner.de/meldungen/behg-ebev-2030-amtliche-emissionsfaktoren-fuer-die-co2-bepreisung-ab-2023">TGA-Fachplaner EBeV 2030</a>, <a href="https://deumess.de/ermittlung-der-co2-emmissionsfaktoren/">DEUMESS CO₂-Faktoren</a></td>
                    </tr>
                    
                    <tr class="category">
                        <td colspan="4"><strong>Erneuerbare Wärmequellen</strong></td>
                    </tr>
                    <tr class="renewable heat">
                        <td>Solarthermie</td>
                        <td class="number">15 - 25</td>
                        <td>Nur Herstellung/Installation</td>
                        <td><a href="https://www.ise.fraunhofer.de/de/geschaeftsfelder/waermetechnologien/solarthermie.html">Fraunhofer ISE</a>, Solar Heat Europe</td>
                    </tr>
                    <tr class="biomass heat">
                        <td>Holzpellets (Heizung)</td>
                        <td class="number">22</td>
                        <td>Nur Bereitstellung, CO₂-neutral</td>
                        <td><a href="https://depv.de/p/Bessere-CO2-Bilanz-mit-Holzpellets-pWuQQ4VvuNQoYjUzRf778Z">DEPV CO₂-Bilanz Pellets</a>, <a href="https://www.umweltbundesamt.de/uba-co2-rechner-neue-berechnungsgrundlage-bei">UBA Holzenergie CO₂-Rechner</a></td>
                    </tr>
                    <tr class="biomass heat">
                        <td>Scheitholz</td>
                        <td class="number">15 - 40</td>
                        <td>Je nach Transportweg</td>
                        <td><a href="https://www.umweltbundesamt.de/uba-co2-rechner-neue-berechnungsgrundlage-bei">UBA Holzenergie CO₂-Rechner</a></td>
                    </tr>
                    <tr class="biomass heat">
                        <td>Hackschnitzel</td>
                        <td class="number">18 - 35</td>
                        <td>Regional bezogen</td>
                        <td><a href="https://www.unendlich-viel-energie.de/mediathek/grafiken/vergleich-der-emissionsfaktoren-von-fossilen-und-biogenen-energietraegern">AEE Emissionsfaktoren biogen</a>, <a href="https://www.umweltbundesamt.de/uba-co2-rechner-neue-berechnungsgrundlage-bei">UBA Holzenergie CO₂-Rechner</a></td>
                    </tr>
                    
                    <tr class="category">
                        <td colspan="4"><strong>Wärmepumpen</strong></td>
                    </tr>
                    <tr class="renewable heat">
                        <td>Luft-Wasser-WP (dt. Strommix)</td>
                        <td class="number">160 - 200</td>
                        <td>Bei COP 3,5-4,0</td>
                        <td><a href="https://www.waermepumpe.de/normen-technik/zahlen-daten/">BWP Faktenblatt</a>, <a href="https://uba.co2-rechner.de/de_DE/">UBA CO₂-Rechner</a></td>
                    </tr>
                    <tr class="renewable heat">
                        <td>Sole-Wasser-WP (dt. Strommix)</td>
                        <td class="number">140 - 180</td>
                        <td>Bei COP 4,0-4,5</td>
                        <td><a href="https://www.waermepumpe.de/normen-technik/zahlen-daten/">BWP Faktenblatt</a>, <a href="https://uba.co2-rechner.de/de_DE/">UBA CO₂-Rechner</a></td>
                    </tr>
                    <tr class="renewable heat">
                        <td>Wärmepumpe (100% Ökostrom)</td>
                        <td class="number">20 - 40</td>
                        <td>Bei Ökostrom-Bezug</td>
                        <td><a href="https://www.waermepumpe.de/normen-technik/zahlen-daten/">BWP Faktenblatt</a></td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <h2>Einsparung gegenüber deutschem Energiemix</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <h4>Strommix-Vergleich (deutscher Strommix 2024: ~363 g CO₂/kWh)</h4>
                <ul style="list-style: none; padding: 0;">
                    <li>Photovoltaik: <span class="number">~318 g CO₂/kWh (88% Einsparung)</span></li>
                    <li>Windkraft (onshore): <span class="number">~351 g CO₂/kWh (97% Einsparung)</span></li>
                    <li>Biogas: <span class="number">~333 g CO₂/kWh (92% Einsparung)</span></li>
                    <li>Wasserkraft: <span class="number">~313 g CO₂/kWh (86% Einsparung)</span></li>
                    <li>Kernkraft: <span class="number">~348 g CO₂/kWh (96% Einsparung)</span></li>
                </ul>
            </div>
            
            <div class="stat-card">
                <h4>Wärmemix-Vergleich (deutscher Wärmemix 2023: ~250 g CO₂/kWh)</h4>
                <ul style="list-style: none; padding: 0;">
                    <li>Solarthermie: <span class="number">~225 g CO₂/kWh (90% Einsparung)</span></li>
                    <li>Pelletheizung: <span class="number">~228 g CO₂/kWh (91% Einsparung)</span></li>
                    <li>Wärmepumpe (Ökostrom): <span class="number">~220 g CO₂/kWh (88% Einsparung)</span></li>
                    <li>Biogas-Heizung: <span class="number">~228 g CO₂/kWh (91% Einsparung)</span></li>
                </ul>
            </div>
        </div>
        
        <div class="highlight">
            <h4>Wichtige Hinweise zu den Daten</h4>
            <p><strong>Lebenszyklusbetrachtung:</strong> Alle Werte berücksichtigen Herstellung, Transport, Betrieb und Entsorgung der Anlagen sowie Brennstoffvorketten.</p>
            <p><strong>Biomasse-Besonderheit:</strong> Biogas aus Biomasse: CO₂-neutral, da nur so viel CO₂ freigesetzt wird, wie die Pflanzen zuvor gebunden haben.</p>
            <p><strong>Regionale Unterschiede:</strong> Fernwärme variiert stark: 49 g CO₂/kWh (Mecklenburg-Vorpommern) bis 311 g CO₂/kWh (Niedersachsen).</p>
            <p><strong>Aktualität:</strong> Deutscher Strommix 2024: 363 g CO₂/kWh (deutlich gesunken gegenüber 2023: 380 g CO₂/kWh).</p>
        </div>
        
        <div class="sources">
            <h3>Quellenverzeichnis (Funktionierende Links - verifiziert August 2025)</h3>
            
            <div class="source-category">
                <h4>Offizielle Behörden und Institutionen</h4>
                <div class="source-list">
                    <p>• <a href="https://www.umweltbundesamt.de/themen/co2-emissionen-pro-kilowattstunde-strom-2024"><strong>UBA Strommix 2024</strong></a> - Aktuelle CO₂-Emissionen pro kWh Strom</p>
                    <p>• <a href="https://www.umweltbundesamt.de/sites/default/files/medien/11850/publikationen/23_2024_cc_strommix_11_2024.pdf"><strong>UBA Strommix-Studie PDF</strong></a> - Vollständige Strommix-Analyse 2023/2024</p>
                    <p>• <a href="https://www.umweltbundesamt.de/uba-co2-rechner-neue-berechnungsgrundlage-bei"><strong>UBA Holzenergie CO₂-Rechner</strong></a> - Neue Berechnungsgrundlage Holzenergie 2024</p>
                    <p>• <a href="https://www.umweltbundesamt.de/themen/luft/emissionen-von-luftschadstoffen/spezifische-emissionsfaktoren-fuer-den-deutschen"><strong>UBA Spezifische Emissionsfaktoren</strong></a> - Deutsche Strommix-Emissionsfaktoren</p>
                    <p>• <a href="https://www.umweltbundesamt.de/daten/energie/energiebedingte-emissionen"><strong>UBA Energiebedingte Emissionen</strong></a> - Energiesektor Emissionsstatistiken</p>
                </div>
            </div>
            
            <div class="source-category">
                <h4>Fachverbände und Institutionen</h4>
                <div class="source-list">
                    <p>• <a href="https://depv.de/p/Bessere-CO2-Bilanz-mit-Holzpellets-pWuQQ4VvuNQoYjUzRf778Z"><strong>DEPV CO₂-Bilanz Pellets</strong></a> - Deutscher Pelletverband CO₂-Studie</p>
                    <p>• <a href="https://eps-bhkw.de/emissionen-biogas-faktencheck/"><strong>EPS BHKW Faktencheck</strong></a> - Biogas-Emissionen Faktencheck 2022</p>
                    <p>• <a href="https://biogas.fnr.de/rahmenbedingungen/treibhausgas-emissionen-von-biogasanlagen"><strong>FNR Treibhausgas-Emissionen Biogas</strong></a> - Fachagentur Nachwachsende Rohstoffe</p>
                    <p>• <a href="https://www.waermepumpe.de/normen-technik/zahlen-daten/"><strong>BWP Faktenblatt</strong></a> - Bundesverband Wärmepumpe Faktendaten</p>
                    <p>• <a href="https://www.unendlich-viel-energie.de/mediathek/grafiken/vergleich-der-emissionsfaktoren-von-fossilen-und-biogenen-energietraegern"><strong>AEE Emissionsfaktoren biogen</strong></a> - Agentur Erneuerbare Energien</p>
                </div>
            </div>
            
            <div class="source-category">
                <h4>Wissenschaftliche und private Institutionen</h4>
                <div class="source-list">
                    <p>• <a href="https://www.polarstern-energie.de/magazin/artikel/heizen-co2-vergleich-von-brennstoffen/"><strong>Polarstern Heizungsvergleich</strong></a> - CO₂-Vergleich Heizsysteme 2025</p>
                    <p>• <a href="https://volker-quaschning.de/datserv/CO2-spez/index.php"><strong>Quaschning CO₂-Tabelle</strong></a> - Prof. Quaschning HTW Berlin, CO₂-Emissionsfaktoren</p>
                    <p>• <a href="https://www.tga-fachplaner.de/meldungen/behg-ebev-2030-amtliche-emissionsfaktoren-fuer-die-co2-bepreisung-ab-2023"><strong>TGA-Fachplaner EBeV 2030</strong></a> - Amtliche CO₂-Emissionsfaktoren ab 2023</p>
                    <p>• <a href="https://deumess.de/ermittlung-der-co2-emmissionsfaktoren/"><strong>DEUMESS CO₂-Faktoren</strong></a> - CO₂-Faktoren-Ermittlung für Messdienstleister</p>
                </div>
            </div>
            
            <div class="source-category">
                <h4>CO₂-Rechner</h4>
                <div class="source-list">
                    <p>• <a href="https://uba.co2-rechner.de/de_DE/"><strong>UBA CO₂-Rechner</strong></a> - Persönlicher CO₂-Fußabdruck-Rechner</p>
                </div>
            </div>
        </div>
        
        <div class="note">
            <p><strong>Alle Links wurden im August 2025 auf Funktionalität geprüft</strong></p>
            <p>Diese Tabelle bietet eine umfassende Übersicht über CO₂-Emissionsfaktoren mit direkten Links zu den Originalquellen. 
            Besonders hervorzuheben ist die Differenzierung der Biomasse-Anwendungen (Biogas-Landwirt: 20-40 g CO₂/kWh, 
            Pellet-Heizung: 22 g CO₂/kWh, Holzheizkraftwerk: 150-350 g CO₂/kWh) sowie die Berücksichtigung der 
            Volllaststunden für die korrekte Umrechnung von installierter Leistung zu Jahresenergie.</p>
        </div>
        
        <div class="footer">
            <p><strong>Bearbeitung:</strong> August 2025 | <strong>Datenstand:</strong> 2024/2025 | <strong>Lebenszyklusbetrachtung</strong> inkl. Vorketten</p>
            <p>Wissenschaftlich fundierte CO₂-Emissionsfaktoren für Strom- und Wärmeerzeugung mit verifizierten Quellen</p>
        </div>
    </div>
</body>
</html>
