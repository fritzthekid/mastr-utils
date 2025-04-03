# tests

import subprocess
import os
from flask import jsonify
import sys
import re

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/..")

from mastr_utils.analyse_mastr import Analyse
from mastr_utils.mastrtogpx import main as dogpx

testdir = os.path.dirname(os.path.abspath(__file__))


# import mastr_utils
# from mastr_utils.analyse_mastr import rootdir

# testdir = os.path.dirname(os.path.abspath(__file__))

teststr_1 = f"mastrtogpx {testdir}/data/stromerzeuger_ludwigsburg.csv -q ge_1mw -o {testdir}/tmp/x.gpx"
teststr_2 = "mastrtogpx ~/Downloads/Stromerzeuger(18).csv -q is_speicher&ge_10kw -o tmp/x.gpx -c Blue"

teststr_3 = None
teststr_4 = None # "mastrtogpx ~/Downloads/Stromerzeuger(20).csv -q 'BruttoleistungDerEinheit > 1000000000000' -o tmp/x.gpx -e".split()

def print_properties_testfile(file):
    print(f"len: {len(re.findall("\n", file))}")
    print(f"<wpt: {len(re.findall("<wpt", file))}")
    print(f"</wpt {len(re.findall("</wpt>", file))}")
    symbols = []
    for symbol in re.findall("<sym>(.*?)</sym>", file):
        symbols.append(symbol)
    print(f"symobls {len(symbols)}")
    print(f"set(symbols): {set(symbols)}")
          
def do_test0():
    command = teststr_1.split()
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print('Conversion completed successfully.')

        return jsonify({
            'status': 'success',
            'message': 'Conversion completed successfully.',
            'download_url': f"{command[6]}"
        })
    except subprocess.CalledProcessError as e:
        print('Error during conversion:', e.stderr)
        return jsonify({'status': 'error', 'message': e.stderr})
    except Exception as e:
        print('Unexpected error:', e)
        return jsonify({'status': 'error', 'message': 'An unexpected error occurred.'})
    
def do_gen_gpx(**argv):
    pass

def test_stromerzeuger_ludwigsburg():
    analyse = Analyse(file_path=f"{testdir}/data/stromerzeuger_ludwigsburg.csv")
    analyse.gen_gpx(
        conditions="ge_1mw",
        output_file=f"{testdir}/tmp/x.gpx",
        min_weight=0,
        symbol_part=[True, None]
    )
    file = open(f"{testdir}/tmp/x.gpx", "r").read()
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
    teststr_5 = f"{testdir}/data/stromerzeuger_pv_brd.csv,-q,BruttoleistungDerEinheit > 10000,-o,{testdir}/tmp/x.gpx,-c,x,-m,90000,-r,2000,-e"

    args = teststr_5.split(',')
    # args = [f"{testdir}/tests/data/stromerzeuger_ludwigsburg.csv", "-o", "{}/x.gpx", "-s", "-e"]
    dogpx(args)
    file = open(f"{testdir}/tmp/x.gpx").read()
    assert len(re.findall("\n", file)) == 212
    assert len(re.findall("<wpt", file)) == 21
    assert len(re.findall("</wpt>", file)) == 21
    symbols = []
    for symbol in re.findall("<sym>(.*?)</sym>", file):
        symbols.append(symbol)
    assert len(symbols) == 21
    assert set(symbols) == {'Solare Strahlungsenergie'}
    
def test_wind_bawue_area_search():
    teststr = f"{testdir}/data/stromerzeuger_wind_bawue.csv,-q,BruttoleistungDerEinheit > 6000,-o,{testdir}/tmp/x20.gpx,-c,x,-m,20000,-r,20000,-e"

    args = teststr.split(',')
    # args = [f"{testdir}/tests/data/stromerzeuger_ludwigsburg.csv", "-o", "{}/x.gpx", "-s", "-e"]
    dogpx(args)
    file = open(f"{testdir}/tmp/x20.gpx").read()
    print_properties_testfile(file)
    assert len(re.findall("\n", file)) == 82
    assert len(re.findall("<wpt", file)) == 8
    assert len(re.findall("</wpt>", file)) == 8
    symbols = []
    for symbol in re.findall("<sym>(.*?)</sym>", file):
        symbols.append(symbol)
    assert len(symbols) == 8
    pass
    assert set(symbols) == {'Wind'}

def test_file_size():
    try:
        teststr = f"{testdir}/data/stromerzeuger_ludwigsburg.csv;-o;{testdir}/tmp/x20.gpx;-l;[5, 1e5, 1e2]"
        args = teststr.split(';')
        dogpx(args)
    except AssertionError:
        assert True
    
def test_data_size():
    try:
        teststr = f"{testdir}/data/stromerzeuger_ludwigsburg.csv;-o;{testdir}/tmp/x20.gpx;-l;[5, 2e6, 1e3]"
        args = teststr.split(';')
        dogpx(args)
        assert False, "test data size limit not detected" 
    except AssertionError:
        assert True

def test_time_limit():
    try:
        teststr = f"{testdir}/data/stromerzeuger_ludwigsburg.csv;-o;{testdir}/tmp/x20.gpx;-l;[-1, 2e6, 1e4]"
        args = teststr.split(';')
        dogpx(args)
        assert False, "time limit test failed"
    except TimeoutError: 
        assert True

def test_nan_float():
    teststr = f"{testdir}/data/stromerzeuger_1_4MB_2T.csv;-o;{testdir}/tmp/x.gpx;-c;x;-m;2000;-r;900000;-e;-l;[1000000,5e6,1e4]"
    args = teststr.split(';')
    dogpx(args)
    assert True
