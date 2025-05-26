# tests

import subprocess
import os
from flask import jsonify
import sys
import re
import pytest
import pandas
print(pandas.__version__)
import matplotlib
print(matplotlib.__version__)
import seaborn
print(seaborn.__version__)
import sklearn
print(sklearn.__version__)

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/..")

from mastr_utils.analyse_mastr import Analyse, get_creation_date
from mastr_utils.mastrtoplot import main as doplot
from mastr_utils.mastrtogpx import main as dogpx

testdir = os.path.dirname(os.path.abspath(__file__))

DEBUGTIMEOUT = 1000

def print_properties_testfile(file):
    file_len = len(re.findall('\n', file))
    print(f"len: {file_len}")
    print(f"<wpt: {len(re.findall('<wpt', file))}")
    print(f"</wpt {len(re.findall('</wpt>', file))}")
    symbols = []
    for symbol in re.findall("<sym>(.*?)</sym>", file):
        symbols.append(symbol)
    print(f"symobls {len(symbols)}")
    print(f"set(symbols): {set(symbols)}")

def profiling_simple():
    # analyse.plot('is_active & is_pv & ge_10mw & lt_100mw', 'bundesland', artefact="PV 10-100 MW")
    outfile = f"{testdir}/tmp/x.svg"
    os.remove(outfile) if os.path.exists(outfile) else None
    teststr = f"{testdir}/data/stromerzeuger_pv_brd.csv;-q;is_pv & ge_1mw & lt_10mw#is_pv & ge_10mw & lt_100mw#is_pv & ge_100mw;"
    teststr += f"-d;Bundesland;-o;{outfile};-s;-l;[10000,5e6,1e4]"
    args = teststr.split(';')
    doplot(args)
    file = open(f"{outfile}").read()
    assert len(re.findall("\n", file)) > 100

def profiling_plot():
    # analyse.plot('is_active & is_pv & ge_10mw & lt_100mw', 'bundesland', artefact="PV 10-100 MW")
    outfile = f"{testdir}/tmp/x.svg"
    os.remove(outfile) if os.path.exists(outfile) else None
    teststr =  f"{testdir}/data/anlagen_brd_wind_ge2mw.csv;"
    teststr += f"-q;BruttoleistungDerEinheit < 5000#BruttoleistungDerEinheit >= 5000;"
    teststr += f"-d;Bundesland;-o;{outfile};-s;-l;[10000,5e7,3e5]"
    # mastrtoplot /home/eduard/work/mastr-utils/tmp/anamastr/12/anlagen_brd_wind_ge2mw.csv -q 'BruttoleistungDerEinheit < 5000#BruttoleistungDerEinheit >= 5000' -d Bundesland -o /home/eduard/work/mastr-utils/tmp/anamastr/12/anlagen_brd_wind_ge2mw.svg -m 0 -r 2000 -s -l [10000,5e7,3e5]
    args = teststr.split(';')
    doplot(args)
    file = open(f"{outfile}").read()
    assert len(re.findall("\n", file)) > 100

def profiling_gpx():
    analyse = Analyse(file_path=f"{testdir}/data/anlagen_brd_pv_ge_500kw.csv", figname="fig", fig_num=0, 
                 timeout = 50000, filesize = 20e7, datasize=4e4)
    outfile = f"{testdir}/tmp/x.gpx"
    os.remove(outfile) if os.path.exists(outfile) else None
    analyse.gen_gpx(conditions='is_active & is_pv & ge_10mw & lt_100mw', output_file=f"{outfile}", symbol_part=[False, "Amber"], min_weight=100000, radius=2000)
    # teststr =  f"{testdir}/data/anlagen_brd_pv_ge_500kw.csv;-q;BruttoleistungDerEinheit > 1000;"
    # teststr += f"-o; {outfile};-m;100000;-r;2000;-l;[10000,5e7,3e5]"
    # args = teststr.split(';')
    # doplot(args)
    result = open(f"{outfile}").read()
    assert len(result) > 1000 

# profiling_simple()
profiling_plot()
profiling_gpx()
