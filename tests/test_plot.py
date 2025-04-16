# tests

import subprocess
import os
from flask import jsonify
import sys
import re
import pytest

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/..")

from mastr_utils.analyse_mastr import Analyse
from mastr_utils.mastrtoplot import main as doplot

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

def test_stromerzeuger_ludwigsburg():
    analyse = Analyse(file_path=f"{testdir}/data/stromerzeuger_ludwigsburg.csv",timeout = DEBUGTIMEOUT)
    analyse.gen_gpx(
        conditions="ge_1mw",
        output_file=f"{testdir}/tmp/x.svg",
        min_weight=0,
        symbol_part=[True, None],    
    )
    file = open(f"{testdir}/tmp/x.svg", "r").read()
    assert len(re.findall("\n", file)) == 582
    assert len(re.findall("<wpt", file)) == 58
    assert len(re.findall("</wpt>", file)) == 58
    symbols = []
    for symbol in re.findall("<sym>(.*?)</sym>", file):
        symbols.append(symbol)
    assert len(symbols) == 58
    assert len(set(symbols)) == 8
    assert sorted(set(symbols)) == ['Biomasse', 'Erdgas', 'Mineralölprodukte', 
                                    'Solare Strahlungsenergie', 'Speicher', 
                                    'Steinkohle', 'Wasser', 'Wind'
                                    ]

def test_pv_brd_area_search():
    teststr = f"{testdir}/data/stromerzeuger_pv_brd.csv,-q,BruttoleistungDerEinheit > 10000,-o,{testdir}/tmp/x.svg,-c,x,-m,90000,-r,2000,-e"

    args = teststr.split(',')
    # args = [f"{testdir}/tests/data/stromerzeuger_ludwigsburg.csv", "-o", "{}/x.svg", "-s", "-e"]
    doplot(args)
    file = open(f"{testdir}/tmp/x.svg").read()
    assert len(re.findall("\n", file)) == 212
    assert len(re.findall("<wpt", file)) == 21
    assert len(re.findall("</wpt>", file)) == 21
    symbols = []
    for symbol in re.findall("<sym>(.*?)</sym>", file):
        symbols.append(symbol)
    assert len(symbols) == 21
    assert set(symbols) == {'Solare Strahlungsenergie'}
    
def test_wind_bawue_area_search():
    teststr = f"{testdir}/data/stromerzeuger_wind_bawue.csv,-q,BruttoleistungDerEinheit > 6000,-o,{testdir}/tmp/x20.svg,-c,x,-m,20000,-r,20000,-e"

    args = teststr.split(',')
    # args = [f"{testdir}/tests/data/stromerzeuger_ludwigsburg.csv", "-o", "{}/x.svg", "-s", "-e"]
    doplot(args)
    file = open(f"{testdir}/tmp/x20.svg").read()
    print_properties_testfile(file)
    assert len(re.findall("\n", file)) == 82
    assert len(re.findall("<wpt", file)) == 8
    assert len(re.findall("</wpt>", file)) == 8
    symbols = []
    for symbol in re.findall("<sym>(.*?)</sym>", file):
        symbols.append(symbol)
    assert len(symbols) == 8
    assert set(symbols) == {'Wind'}

@pytest.mark.xfail(raises=AssertionError)
def test_file_size():
    teststr = f"{testdir}/data/stromerzeuger_ludwigsburg.csv;-o;{testdir}/tmp/x20.svg;-l;[5, 1e5, 1e2]"
    args = teststr.split(';')
    doplot(args)
    assert True    

@pytest.mark.xfail(raises=AssertionError)
def test_data_size():
    teststr = f"{testdir}/data/stromerzeuger_ludwigsburg.csv;-o;{testdir}/tmp/x20.svg;-l;[5, 2e6, 1e3]"
    args = teststr.split(';')
    doplot(args)
    assert True

@pytest.mark.xfail(raises=TimeoutError)
def test_time_limit():
    teststr = f"{testdir}/data/stromerzeuger_ludwigsburg.csv;-o;{testdir}/tmp/x20.svg;-l;[-1, 2e6, 1e4]"
    args = teststr.split(';')
    doplot(args)
    assert True

def test_nan_float():
    teststr = f"{testdir}/data/stromerzeuger_1_4MB_2T.csv;-o;{testdir}/tmp/x.svg;-c;x;-m;2000;-r;900000;-e;-l;[1000000,5e6,1e4]"
    args = teststr.split(';')
    doplot(args)
    assert True

def test_large_file():
    teststr = f"{testdir}/data//stromerzeuger_8MB_13T.csv;-o;{testdir}/tmp/x.svg"
    args = teststr.split(';')
    doplot(args)

def test_cleebronn():
    import pandas as pd
    teststr = f"{testdir}/data/stromerzeuger_cleebronn.csv;-o;{testdir}/tmp/x.svg;-e;-l;[1000000,5e6,1e4]"
    args = teststr.split(';')
    doplot(args)
    file = open(f"{testdir}/tmp/x.svg").read()
    print_properties_testfile(file)
    assert len(re.findall("\n", file)) == 212
    assert len(re.findall("<wpt", file)) == 21
    symbols = []
    for symbol in re.findall("<sym>(.*?)</sym>", file):
        symbols.append(symbol)
    data = pd.read_csv(f"{testdir}/data/stromerzeuger_cleebronn.csv", sep=';', encoding='utf-8', decimal=',')
    assert len(data) == 394
    streets = list(str(val) for val in data["Straße"])
    astreets = {val:len([v for v in streets if v == val]) for val in set(streets)}
    assert astreets["Daimlerstraße"] == 6
    assert sum([astreets[val] for val in set(streets)]) == 394
    assert astreets['nan'] == 373
    assert set(symbols) == set([data['Energieträger'][i] for i in data.index if str(data["Straße"][i]) != "nan"])

def test_muell_klaerschlamm():
    teststr = f"{testdir}/data/muell-klaerschlamm.csv;-o;{testdir}/tmp/x.svg;-s"
    args = teststr.split(';')
    doplot(args)
    teststr = f"{testdir}/data/muell-klaerschlamm.csv;-o;{testdir}/tmp/x.svg;-a"
    args = teststr.split(';')
    doplot(args)
    assert True

def test_plot():
    analyse = Analyse(file_path=f"{testdir}/data/stromerzeuger_ludwigsburg.csv",timeout = DEBUGTIMEOUT)
    analyse.plot("is_pv","Postleitzahl")
    assert True

def test_pv_brd_simple():
    teststr = f"{testdir}/data/stromerzeuger_pv_brd.csv,-q,BruttoleistungDerEinheit > 10000,-o,{testdir}/tmp/x.csf"
    args = teststr.split(',')
    doplot(args)
    pass

test_pv_brd_simple()
