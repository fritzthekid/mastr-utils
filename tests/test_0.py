# tests

import subprocess
import os
from flask import jsonify
import sys
import re
sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/..")
from mastr_utils.analyse_mastr import Analyse

# import mastr_utils
# from mastr_utils.analyse_mastr import rootdir

testdir = os.path.dirname(os.path.abspath(__file__))

teststr_1 = f"mastrtogpx {testdir}/data/stromerzeuger_ludwigsburg.csv -q ge_1mw -o {testdir}/tmp/x.gpx"
teststr_2 = "mastrtogpx ~/Downloads/Stromerzeuger(18).csv -q is_speicher&ge_10kw -o tmp/x.gpx -c Blue"

teststr_3 = None
teststr_4 = None # "mastrtogpx ~/Downloads/Stromerzeuger(20).csv -q 'BruttoleistungDerEinheit > 1000000000000' -o tmp/x.gpx -e".split()
teststr_5 = "/tmp/Stromerzeuger(20).csv -q BruttoleistungDerEinheit > 6000 -o /tmp/x.gpx -c x -m 10000 -r 20000 -e"


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
    
def test_0():
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

    #test_0()