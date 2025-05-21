import pandas as pd
import numpy as np
import math
import datetime
import os
import re
import math
import shutil
import time
import subprocess
import platform
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import seaborn as sns
# import plotly.express as px

from .cluster import filter_large_weights
import logging
import signal
from .symbols import energie_symbols

from gpxpy.gpx import GPX, GPXWaypoint
# from xml.etree import ElementTree
from xml.sax.saxutils import escape

plt.rcParams['svg.fonttype'] = 'none'

# Get the root path of the current directory
rootpath = os.path.dirname(os.path.abspath(__file__))
# shutil.rmtree('/tmp/anamastr-*', ignore_errors=True)
# tmpdir = f"/tmp/anamastr-{os.getpid()}"
tmpdir = f"{rootpath}/../tmp/anamastr"
os.makedirs(tmpdir, exist_ok=True)

# Configure logging
log_file = f"{tmpdir}/mastr_analyse.log"
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

global timeout_value
timeout_value = 6

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    print(f"Execption exception timeout ({timeout_value} sec)")
    logging.info(f"Execption exception timeout ({timeout_value} sec)")
    raise TimeoutError("time limit exceeded")

signal.signal(signal.SIGALRM, timeout_handler)

# List of all the Bundesland in Germany
bundeslaender = [
    'Baden-Württemberg', 
    'Bayern', 
    'Berlin', 
    'Brandenburg', 
    'Bremen', 
    'Hamburg', 
    'Hessen',
    'Mecklenburg-Vorpommern', 
    'Niedersachsen',
    'Nordrhein-Westfalen',
    'Rheinland-Pfalz',
    'Saarland',
    'Sachsen', 
    'Sachsen-Anhalt',
    'Schleswig-Holstein',
    'Thüringen'
]

# Function to convert string to datetime
def str_to_datetime(date):
    try:
        return datetime.datetime.strptime(date, "%d.%m.%Y").date()
    except:
        return datetime.datetime.strptime("01.01.2099", "%d.%m.%Y").date()   

#def c_h(s):
#    return re.sub('[^0-9A-Za-z]','_', str(s))

# Function to convert string to camel case
def to_camel_case(text):
    s = re.sub("[-.:]", " ",text)
    s = re.sub("[()]", "_", s)
    s = s.split()
    if len(text) == 0:
        return text
    return s[0] + ''.join(i.capitalize() for i in s[1:])

def isnum(s):
    try:
        r = isinstance(float(s),float)
    except:
        r = False
    return r

# Haversine-Formel
# def haversine(lon1, lat1, lon2, lat2):
#     # Radius der Erde in Metern
#     R = 6371000

#     # Umrechnung in Bogenmaß
#     phi1 = math.radians(lat1)
#     phi2 = math.radians(lat2)
#     delta_phi = math.radians(lat2 - lat1)
#     delta_lambda = math.radians(lon2 - lon1)

#     # Haversine-Formel
#     a = math.sin(delta_phi / 2)**2 + \
#         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
#     c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

#     distance = R * c
#     return distance  # in Metern

def clean_bruttoleistung(data):
    for i,val in enumerate(data["BruttoleistungDerEinheit"]):
        if type(val) == str:
            val = round(float(re.sub(',','.',val))) 
        data.at[data.iloc[i].name,"BruttoleistungDerEinheit"] = np.float64(val)

def get_creation_date(file_path):
    stat = os.stat(file_path)
    
    # Versuch 1: Direkt über st_birthtime (nur macOS)
    if hasattr(stat, 'st_birthtime'):
        try:
            ftime = datetime.datetime.fromtimestamp(stat.st_birthtime)
            return ftime.strftime("%d.%m.%Y")
        except Exception:
            pass

    # Versuch 2: Über "stat" Kommando auswerten
    if platform.system() == "Linux" or platform.system() == "Darwin":
        try:
            res = subprocess.run(["stat", file_path], capture_output=True, text=True)
            for line in res.stdout.splitlines():
                if re.search(r'(?i)birth|geburt', line):
                    date_match = re.search(r'\d{4}-\d{2}-\d{2}', line)
                    if date_match:
                        y, m, d = date_match.group(0).split('-')
                        return f"{d}.{m}.{y}"
        except Exception:
            pass

    # Versuch 3: Fallback auf Änderungszeit
    ftime = datetime.datetime.fromtimestamp(stat.st_mtime)
    return ftime.strftime("%d.%m.%Y")

def get_date_last_modified(data,col):
    alldates = []
    for date in data[col]:
        alldates.append(datetime.datetime.strptime(date,"%d.%m.%Y"))
    return sorted(alldates)[-1].strftime("%d.%m.%Y")

# Beispiel:
# lon1, lat1 = 13.4050, 52.5200  # Berlin
# lon2, lat2 = 11.5810, 48.1351  # München

# print(f"Entfernung: {haversine(lon1, lat1, lon2, lat2):.2f} Meter")


# Define the Analyse class
class Analyse:
    # Dictionary to map column names to their descriptions
    depends_dict = {
        'betreiber': 'NameDesAnlagenbetreibers_nurOrg_',
        'bundesland': 'Bundesland',
        'lage': 'Lage der Einheit',
        'ort': 'Ort'
    }

    # Initialize the class with data from an Excel file
    def __init__(self, file_path=f"{rootpath}/../db/MarktStammregister/MaStR-Raw.ods", figname="fig", fig_num=0, 
                 timeout = 5, filesize = 10e6, datasize=2e4):
        logging.info(f"Initializing Analyse with file_path={file_path}")
        self.file_path = file_path
        self.timeout, self.filesize, self.datasize = timeout, filesize, datasize
        global timeout_value
        timeout_value = timeout
        if timeout<0:
            self.test_timeout = True
            self.timeout = 1
        else:
            self.test_timeout = False
        
        signal.alarm(self.timeout)

        try:
            self.fig_num = fig_num
            self.figname = figname
            assert os.path.getsize(file_path) <= self.filesize, f"File size exceeds limits {self.filesize}"
            if file_path.endswith('.csv'):
                self.data = pd.read_csv(file_path, sep=';', encoding='utf-8', decimal=',')
            elif file_path.endswith('.xls') or file_path.endswith('.xlsx'):
                self.data = pd.read_excel(file_path)
            elif file_path.endswith('.ods'):
                self.data = pd.read_excel(file_path, engine='odf')
            else:
                raise ValueError("Invalid file format. Please provide a CSV, XLS, or ODS file.")
            assert len(self.data) < self.datasize, f"Number of recordnummers exceeds {self.datasize}"  
            logging.info(f"Data loaded successfully from {file_path}")
        except Exception as e:
            logging.error(f"Error initializing Analyse: {e}")
            signal.alarm(0)
            raise
        for i in self.data.index:
            self.data['Inbetriebnahmedatum der Einheit'].at[i] = str_to_datetime(self.data['Inbetriebnahmedatum der Einheit'][i])
        
        columns_rename_dict = {c:to_camel_case(c) for c in self.data.columns}
        self.data.rename(columns=columns_rename_dict, inplace=True)
        self.creation_date = get_creation_date(file_path)
        self.last_modified = get_date_last_modified(self.data,"LetzteAktualisierung")
        # Add new columns based on conditions
        try:
            self.data['is_new'] = self.data['InbetriebnahmedatumDerEinheit'] > str_to_datetime('01.01.2021')
            self.data['is_active'] = self.data['BetriebsStatus'] == 'In Betrieb'
#            self.data['is_battery'] = ( self.data['Energieträger'] == 'Speicher' and self.data['Speichertechnologie'] == 'Batterie' )
            self.data['is_battery'] = ( self.data['Speichertechnologie'] == 'Batterie' )
            self.data['is_pv'] = self.data['Energieträger'] == 'Solare Strahlungsenergie'
        except Exception as e:
            raise e
        finally:
            signal.alarm(0)
        try:
            clean_bruttoleistung(self.data)
            self.data['ge_10kw'] = self.data['BruttoleistungDerEinheit'] >= 10
            self.data['ge_100kw'] = self.data['BruttoleistungDerEinheit'] >= 100
            self.data['ge_1mw'] = self.data['BruttoleistungDerEinheit'] >= 1000
            self.data['ge_10mw'] = self.data['BruttoleistungDerEinheit'] >= 10000
            self.data['ge_100mw'] = self.data['BruttoleistungDerEinheit'] >= 100000
            self.data['lt_10mw'] = self.data['BruttoleistungDerEinheit'] < 10000
            self.data['lt_100mw'] = self.data['BruttoleistungDerEinheit'] < 100000
            self.data['is_gewaesser'] = self.data['ArtDerSolaranlage'] == 'Gewässer'
            self.data['is_freiflaeche'] = self.data['ArtDerSolaranlage'] == 'Freifläche'
        except Exception as e:
            logging.info("cleaning Bruttoleistung der Einheit failed")
        finally:
            signal.alarm(0)
        try:
            self.data['is_BaWue'] = self.data['Bundesland'] == 'Baden-Württemberg'
        except Exception as e:
            raise e
        finally:
            signal.alarm(0)
        if self.test_timeout:
            time.sleep(2)
            raise TimeoutError("Test timeout failed")
        signal.alarm(0)

    def show_columns(self, trailer=""):
        s = ""
        for c in self.data.columns:
            s += f"{trailer}{c}\n"
        return s

    def analyse_datastruct(self):
        try:
            print(f"Anzahl Einträge: {len(self.data)}")
        except:
            pass
        try:
            print(f"Bundesländer: {set(self.data['Bundesland'])}")
        except:
            pass
        try:
            print(f"Anzahl Gemeinden: {len(set(self.data['Ort']))}")
        except:
            pass
        try:
            print(f"Bruttoleistung min: {min(self.data['BruttoleistungDerEinheit'])}, max: {max(self.data['BruttoleistungDerEinheit'])}")
        except:
            pass
        try:
            print("Energieträger: ", set(self.data['Energieträger']))
        except:
            pass
        try:
            print("Betriebsstatus: ", set(self.data['BetriebsStatus']))
        except:
            pass

    # Method to query the data based on a condition and dependency
    def query(self, condition, depends=None):
        depends_column = self.depends_dict.get(depends, depends)
        
        # Extract date filters from the condition
        after = None
        before = None
        if 'after_' in condition:
            after_index = condition.index('after_') + len('after_')
            after = condition[after_index:after_index + 10]
            afterdate = str_to_datetime(after)
            self.data['after_cond'] = self.data['InbetriebnahmedatumDerEinheit'] > afterdate
            condition = condition.replace(f'after_{after}', '')
        if 'before_' in condition:
            before_index = condition.index('before_') + len('before_')
            before = condition[before_index:before_index + 10]
            beforedate = str_to_datetime(before)
            self.data['before_cond'] = self.data['InbetriebnahmedatumDerEinheit'] < beforedate
            condition = condition.replace(f'before_{before}', '')
        
        # Apply date filters if provided
        if after:
            condition += f" & after_cond"
        if before:
            condition += f" & before_cond"
        condition = re.sub('&[ \t]*&', '&', condition)
        condition = re.sub('&[ \t]*&', '&', condition)
        condition = re.sub("^ *& *","", condition)
        # print(f"amastr condition: {condition}")
        # print(f"amastr depends: {depends}")

        try:
            filtered_data = self.data.query(condition)
        except ValueError as e:
            raise ValueError(f"{e}: {condition}")
        # print(filtered_data)
        return filtered_data.groupby(depends_column)['BruttoleistungDerEinheit'].sum().reset_index()

    # Method to plot the data based on a condition and dependency
    def plot(self, condition, depends, artefact="X", output_filename="x"):
        grouped_data = self.query(condition, depends)
        depends_column = self.depends_dict.get(depends, depends)
        plt.figure(figsize=(10, 6))  # Adjust the figure size as needed
        sns.barplot(x=depends_column, y='BruttoleistungDerEinheit', data=grouped_data)
        plt.title(f"Bruttoleistung der Einheit nach {depends_column} für Bedingung: {condition}")
        plt.xlabel(depends_column.capitalize())
        plt.ylabel('Bruttoleistung der Einheit (kW)')
        plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels by 45 degrees
        plt.tight_layout()  # Adjust layout to make room for labels
        plt.figtext(0.95, 0.01, 'MaStR Stand t.b.d', ha='right', va='center')
        splitfile = os.path.splitext(os.path.abspath(output_filename))
        if splitfile[1] not in ["svg", "png"]:
            output_filename = f"{splitfile[0]}.svg"
        plt.savefig(f'{output_filename}')
        plt.close()

    def plot_stacked(self, filter_exprs, depends, artefact=None, output_filename="x", sort=False, min_weight=0, radius=2000):
        import matplotlib.pyplot as plt
        import pandas as pd

        # Daten vorbereiten
        # data = self.data  # Angenommen, self.data ist ein DataFrame
        min_weight = float(min_weight)
        radius = float(radius)
        if min_weight > 0:
            self.data = filter_large_weights(self.data, cluster_radius_m=radius, min_weight=min_weight).query(f'BruttoleistungDerEinheit > {min_weight}')

        grouped_data = pd.DataFrame()

        for expr in filter_exprs.split("#"):
            valc = self.validate(expr)
            if len(valc) > 0:
                error_message = f"Invalid condition, with unknown arguments: {valc}"
                logging.error(error_message)
                raise ValueError(error_message)
            filtered = self.query(expr, depends)
            grouped = filtered.groupby(depends)['BruttoleistungDerEinheit'].sum()
            grouped_data[expr] = grouped

        assert ( len(grouped_data.values.shape) == 2 and 
                grouped_data.values.shape[0]>0 and grouped_data.values.shape[1]>0), f"No data found for condition: {filter_exprs}"

        if sort:
            gdv = grouped_data.values
            gdd = {grouped_data.index[i]:sum([v for v in gdv[i] if str(v) != "nan"]) for i in range(gdv.shape[0])}
            res = {key: val for key, val in sorted(gdd.items(), key = lambda ele: ele[1])[::-1]}
            grouped_data = grouped_data.reindex(index=[n for n in res])
        grouped_data.fillna(0, inplace=True)

        # Gestapeltes Balkendiagramm erstellen
        sns.set_theme(style="whitegrid")
        grouped_data.plot(kind="bar", stacked=True, figsize=(14, 9))
        if artefact:
            title = artefact
        else:
            title = os.path.splitext(os.path.basename(self.file_path))[0]
            if min_weight > 0:
                title += f" (min Leistung im Cluster: {int(min_weight)}kW)"
        plt.title(title)
        plt.xlabel(depends)
        plt.ylabel('Bruttoleistung')
        plt.xticks(rotation=45, ha='right', fontsize=14)
        # plt.legend(title='_')
        plt.figtext(0.95, 0.01, f'MaStR Stand {self.last_modified}', ha='right', va='center')
        plt.tight_layout()
        splitfile = os.path.splitext(os.path.abspath(output_filename))
        if splitfile[1] not in ["svg", "png"]:
            output_filename = f"{splitfile[0]}.svg"
        if not os.path.isdir(os.path.dirname(splitfile[0])):
            raise ValueError("Output filename is no valid")
        plt.savefig(f'{output_filename}')
        plt.close()

    def validate(self, condition):
        valid_columns = self.data.columns
        arguments = re.findall(r'\b\w+\b', re.sub("\".*\"","",condition))
        failed_args =  [arg for arg in [a for a in arguments if not isnum(a)] if arg not in valid_columns]
        return [arg for arg in failed_args if not arg.startswith("after_") and not arg.startswith("before_")] 

    # Method to generate GPX file
    def gen_gpx(self, conditions=None, output_file="gpx.gpx", symbol_part=[False, "Amber"], min_weight=0, radius=1000):
        logging.info(f"Generating GPX file with conditions={conditions}, output_file={output_file}, symbol_part={symbol_part}")
        signal.alarm(self.timeout)
        try:
            if conditions is None or conditions == "":
                gpx_data = self.data
            else:
                valc = self.validate(conditions)
                if len(valc) > 0:
                    error_message = f"Invalid condition, with unknown arguments: {valc}"
                    logging.error(error_message)
                    raise ValueError(error_message)
                gpx_data = self.data.query(conditions)

            if len(gpx_data) == 0:
                logging.error(f"No data found for condition: {conditions}")
                raise ValueError(f"No data found for condition: {conditions}")
                return

            if min_weight > 0:
                gpx_data = filter_large_weights(gpx_data, cluster_radius_m=radius, min_weight=min_weight).query(f'BruttoleistungDerEinheit > {min_weight}')

            gpx = GPX()
            for i in gpx_data.index:
                if (math.isnan(gpx_data['KoordinateBreitengrad_wgs84_'][i]) or
                        math.isnan(gpx_data['KoordinateLängengrad_wgs84_'][i])):
                    continue
                if symbol_part[0]:
                    if gpx_data['Energieträger'][i] in energie_symbols:
                        this_symbol = gpx_data['Energieträger'][i]
                    else:
                        this_symbol = "Navaid, Amber"
                else:
                    this_symbol = f"Navaid, {symbol_part[1]}"
                point = GPXWaypoint(
                    latitude=gpx_data['KoordinateBreitengrad_wgs84_'][i],
                    longitude=gpx_data['KoordinateLängengrad_wgs84_'][i],
                    name=f"P{i}",
                    comment=f"{gpx_data['AnzeigeNameDerEinheit'][i]}",
                    symbol=this_symbol
                )
                desc = f"Name: {gpx_data['AnzeigeNameDerEinheit'][i]}"
                desc += f"<ul><li>Leistung: {gpx_data['BruttoleistungDerEinheit'][i]} kWp<br>\n"
                desc += f"<li>Betriebs-Status: {gpx_data['BetriebsStatus'][i]}</li>\n"
                desc += f"<li>Energieträger: {gpx_data['Energieträger'][i]}</li>\n"
                desc += f"<li>Inbetriebnahmedatum der Einheit: {gpx_data['InbetriebnahmedatumDerEinheit'][i]}</li>\n"
                desc += f"<li>MaStR: {gpx_data['MaStRNrDerEinheit'][i]}</li></ul>"
                point.description = desc
                gpx.waypoints.append(point)
                
            splitfile = os.path.splitext(output_file)
            output_file = splitfile[0]+".gpx"
            if not os.path.isdir(os.path.dirname(output_file)):
                raise ValueError("Output file - directory fails")
            with open(output_file, 'w') as f:
                f.write(gpx.to_xml())
            logging.info(f"GPX file generated successfully: {output_file}")
            if self.test_timeout:
                time.sleep(2)
                raise ValueError("Test timeout failed")
        except ValueError as e:
            logging.error(f"ValueError: {e}")
            signal.alarm(0)
            raise ValueError(e)
        except Exception as e:
            logging.error(f"Error generating GPX file: {e}")
            if e.args[0] == "invalid syntax":
                signal.alarm(0)
                raise ValueError("Query: invalid syntax")
            else:
                signal.alarm(0)
                raise ValueError("Error generating GPX file")                
        finally:
            signal.alarm(0)
