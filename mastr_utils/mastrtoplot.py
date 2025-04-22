#!/usr/bin/env /home/eduard/.venv/waerme/bin/python
# -*- coding: utf-8 -*-

"""
Script to convert the mastr file to a gpx file
with the help of the analyse_mastr.py script
calling convention:
    python mastrtogpx.py <path to mastr file> -q '<query>' -o <path to output gpx file>
"""

import sys
import argparse
import logging
import signal
from .analyse_mastr import Analyse, tmpdir   # Import the Analyse class from analyse_mastr.py

# Configure logging
log_file = f"{tmpdir}/mastrtogpx.log"
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def main(testargs=None):
    logging.info("Starting mastrtogpx conversion")
    try:
        parser = argparse.ArgumentParser(description="Convert MaStR file to GPX file")
        parser.add_argument("mastr_file", help="Path to the MaStR CSV file")
        parser.add_argument("-q", "--query", help="Query to filter the data [default=None]", default=None)
        parser.add_argument("-d", "--depends", help="Histogram depends on argument [default=Bundesland]", default="Bundesland")
        parser.add_argument("-o", "--output", help="Path to the output GPX file [default=None]", default=None)
        parser.add_argument("-m", "--min_weight", help="Minimum weight of the cluster [default=0]", default=0)
        parser.add_argument("-r", "--radius", help="Radius [default=2000]", default=2000)
        parser.add_argument("-a", "--analyse_datastruct", help="Value Ranges in Bundesland, Bruttoleistung", action="store_true")
        parser.add_argument("-c", "--show-columns", help="Show the columns of the MaStR file [default=False]", action="store_true")
        parser.add_argument("-s", "--sort", help="Sort depends according to total power [default=False]", action="store_true")
        parser.add_argument("-l", "--limits", help="limits", default='[5,10e6,2e4]')
        parser.add_argument("-h_query", "--help_query", help="Show Examples for Query [default=False]", action="store_true")

        # args = parser.parse_args([f"{tmpdir}/../tests/data/stromerzeuger_ludwigsburg.csv", "-o", "/tmp/x.gpx", "-s", "-e"])
        # pass
        if testargs is None:
            args = parser.parse_args()
        else:
            args = parser.parse_args(testargs)
        # Show the query examples
        if args.help_query:
            print("Query to filter the data")
            print("Example: -q 'is_active & is_pv'")
            print("Example: -q 'BetriebsStatus != \"In Betrieb\" & is_pv & is_10mw'")
            print("Example: -q 'is_pv & Ort == \"Berlin\"'")
            print("Example: -q 'EnergieTräger == \"Erdgas\"'")
            return

        timeout, filesize, datasize = eval(args.limits)
        signal.alarm (timeout)
        analyse = Analyse(file_path=args.mastr_file,
                          timeout = timeout, filesize = filesize, datasize = datasize)
        # if option -s Show the columns of the MaStR file
        if args.show_columns:
            print("Columns in the MaStR file:")
            print(analyse.show_columns("    "))
            return
        
        # if option -a analyse the data structure
        if args.analyse_datastruct:
            print(analyse.analyse_datastruct())
            return

        # Generate the GPX file
        if args.output is None:
            print("Please provide an output file (-o option)")
            parser.print_help()
            return

        analyse.plot_stacked(filter_exprs=args.query, depends=args.depends, output_filename=args.output, 
                             sort=args.sort, min_weight = args.min_weight, radius=args.radius)
        logging.info("Conversion completed successfully")
    except Exception as e:
        logging.error(f"Error during mastrtogpx conversion: {e}")
        raise

if __name__ == "__main__":
    main()