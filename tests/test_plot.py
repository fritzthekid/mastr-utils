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
    outfile = f"{testdir}/tmp/x.svg"
    os.remove(outfile) if os.path.exists(outfile) else None
    teststr = f"{testdir}/data/stromerzeuger_pv_brd.csv,-q, BruttoleistungDerEinheit > 10000,-o,{outfile}x,-s"
    args = teststr.split(',')
    doplot(args)
    file = open(f"{outfile}").read()
    assert len(re.findall("\n", file)) == 441


def test_plot_stacked_rng_bawue_bay():
    analyse = Analyse(file_path=f"{testdir}/data/rng_bawue_bay.csv",timeout = DEBUGTIMEOUT)
    query = 'Energieträger == "Biomasse"#'
    query += 'Energieträger == "Geothermie"#'
    query += 'Energieträger == "Solare Strahlungsenergie"#'
    query += 'Energieträger == "Wind"'
    analyse.plot_stacked(query, 'Bundesland', 
                         artefact="Speicher (in Betrieb)",output_filename=f"{testdir}/tmp/x.svg")

def test_plot_stacked_speicher():
    analyse = Analyse(file_path=f"{testdir}/data/pv_speicher_ge_1mw.csv",timeout = DEBUGTIMEOUT)
    analyse.plot_stacked('is_battery & ge_1mw & lt_10mw#is_battery & ge_10mw & lt_100mw#is_battery & ge_100mw', 
                         'Bundesland', artefact="Speicher (Betrieb + Planung)",
                         output_filename=f"{testdir}/tmp/x.svg")
    pass

def test_plot_stacked_pv():
    # analyse.plot('is_active & is_pv & ge_10mw & lt_100mw', 'bundesland', artefact="PV 10-100 MW")
    teststr = f"{testdir}/data/stromerzeuger_pv_brd.csv;-q;is_pv & ge_1mw & lt_10mw#is_pv & ge_10mw & lt_100mw#is_pv & ge_100mw;"
    teststr += f"-d;Bundesland;-o;{testdir}/tmp/x.svg;-s;-l;[10000,5e6,1e4]"
    args = teststr.split(';')
    doplot(args)
    pass

def test_a_s():
    teststr = f"{testdir}/data/stromerzeuger_ludwigsburg.csv,-s"
    args = teststr.split(',')
    doplot(args)
    teststr = f"{testdir}/data/stromerzeuger_ludwigsburg.csv,-a"
    args = teststr.split(',')
    doplot(args)
    # teststr = f"-h"
    # args = teststr.split(',')
    # doplot(args)
    assert True

# def xx():
#     teststr = f'/home/eduard/work/mastr-utils/mastr_utils/../tmp/anamastr/landkreis-ludwigsburg.csv;-q;is_pv#Energieträger="Biomasse"&HauptbrennstoffDerEinheit!="Biogas"#HauptbrennstoffDerEinheit=="Biogas";-d;Ort;-o;/home/eduard/work/mastr-utils/mastr_utils/../tmp/anamastr/landkreis-ludwigsburg.svg;-m;0;-r;2000;-s;-l;[10000,5e7,3e5]'
#     args = teststr.split(';')
#     doplot(args)
#     pass

def test_before_after():
    teststr = f'{testdir}/data/landkreis-ludwigsburg.csv;-q;is_pv & after_01.01.2021#is_pv & before_31.12.2024;-d;Ort;-o;{testdir}/tmp/landkreis-ludwigsburg.svg;-m;0;-r;2000;-s;-l;[10000,5e7,3e5]'
    args = teststr.split(';')
    doplot(args)
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

# xx()
# test_plot_stacked_pv()
# test_plot_stacked_rng_bawue_bay()
# test_pv_brd_simple()
# test_plot_stacked_rng_bawue_bay()
# test_plot_stacked_speicher()
