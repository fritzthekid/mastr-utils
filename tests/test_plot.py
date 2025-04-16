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


def test_plot():
    analyse = Analyse(file_path=f"{testdir}/data/stromerzeuger_ludwigsburg.csv",timeout = DEBUGTIMEOUT)
    analyse.plot("is_pv","Postleitzahl",output_filename=f"{testdir}/tmp/x.svg")
    assert True

def test_pv_brd_simple():
    teststr = f"{testdir}/data/stromerzeuger_pv_brd.csv,-q,[BruttoleistungDerEinheit > 10000],-o,{testdir}/tmp/x.csf"
    args = teststr.split(',')
    doplot(args)
    pass

def test_plot_stacked_rng_bawue_bay():
    analyse = Analyse(file_path=f"{testdir}/data/rng_bawue_bay.csv",timeout = DEBUGTIMEOUT)
    analyse.plot_stacked(['Energieträger == "Biomasse"', 
                          'Energieträger == "Geothermie"',
                          'Energieträger == "Solare Strahlungsenergie"',
                          'Energieträger == "Solarthermie"',
                          'Energieträger == "Wind"'], 'Bundesland', 
                         artefact="Speicher (in Betrieb)",output_filename=f"{testdir}/tmp/x.svg")

def test_plot_stacked_speicher():
    analyse = Analyse(file_path=f"{testdir}/data/pv_speicher_ge_1mw.csv",timeout = DEBUGTIMEOUT)
    analyse.plot_stacked(['is_speicher & ge_1mw & lt_10mw','is_speicher & ge_10mw & lt_100mw', 'is_speicher & ge_100mw'], 
                         'Bundesland', artefact="Speicher (Betrieb + Planung)",
                         output_filename=f"{testdir}/tmp/speicher.svg")
    pass

def x():
    analyse = Analyse(file_path=f"{testdir}/data/rng_bawue_bay.csv",timeout = DEBUGTIMEOUT)
    # analyse.plot_stacked(['is_pv & ge_1mw & lt_10mw & is_active','is_pv & ge_10mw & lt_100mw & is_active', 'is_pv & ge_100mw & is_active'], 'bundesland', artefact="PV (in Betrieb)")
    # analyse.plot_stacked(['is_pv & ge_1mw & lt_10mw','is_pv & ge_10mw & lt_100mw', 'is_pv & ge_100mw'], 'bundesland', artefact="PV (Betrieb + Planung)")
    # analyse.plot('is_active & is_pv & ge_10mw & lt_100mw', 'bundesland', artefact="PV 10-100 MW")
    # analyse.plot('is_active & is_pv & ge_100mw', 'bundesland', artefact="PV >100 MW")
    # analyse.plot_stacked(['is_pv & ge_100mw','is_pv & ge_10mw & lt_100mw', 'is_pv & ge_1mw & lt_10mw'], 'bundesland', artefact="PV (Betrieb + Planung)", has_legend=True)

    # analyse = Analyse(file_path=f"{rootpath}/../db/MarktStammregister/pvgt1mw.ods", figname="fig2", fig_num=10)
    # analyse.plot_stacked(['is_pv & ge_1mw & lt_10mw & is_active','is_pv & ge_10mw & lt_100mw & is_active', 'is_pv & ge_100mw & is_active'], 'bundesland', artefact="PV (in Betrieb)")
    # analyse.plot_stacked(['is_pv & ge_1mw & lt_10mw','is_pv & ge_10mw & lt_100mw', 'is_pv & ge_100mw'], 'bundesland', artefact="PV (Betrieb + Planung)")


# test_plot_stacked_rng_bawue_bay()
test_pv_brd_simple()
test_plot_stacked_speicher()
