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
from .analyse_mastr import Analyse   # Import the Analyse class from analyse_mastr.py

def main():
    parser = argparse.ArgumentParser(description="Convert MaStR file to GPX file")
    parser.add_argument("mastr_file", help="Path to the MaStR CSV file")
    parser.add_argument("-q", "--query", help="Query to filter the data [default=None]", default=None)
    parser.add_argument("-o", "--output", help="Path to the output GPX file [default=None]", default=None)
    parser.add_argument("-c", "--color", help="Color of Waypoints [default='Amber']", default="Amber")
    parser.add_argument("-m", "--min_weight", help="Minimum weight of the cluster [default=0]", default=0)
    parser.add_argument("-r", "--radius", help="Radius [default=2000]", default=2000)
    parser.add_argument("-a", "--analyse_datastruct", help="Value Ranges in Bundesland, Bruttoleistung", action="store_true")
    parser.add_argument("-s", "--show-columns", help="Show the columns of the MaStR file [default=False]", action="store_true")
    parser.add_argument("-h_query", "--help_query", help="Show Examples for Query [default=False]", action="store_true")
    args = parser.parse_args()

    # Show the query examples
    if args.help_query:
        print("Query to filter the data")
        print("Example: -q 'is_active & is_pv'")
        print("Example: -q 'BetriebsStatus != \"In Betrieb\" & is_pv & is_10mw'")
        print("Example: -q 'is_pv & Ort == \"Berlin\"'")
        print("Example: -q 'EnergieTräger == \"Erdgas\"'")
        return

    analyse = Analyse(file_path=args.mastr_file)
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
    analyse.gen_gpx(conditions=args.query, output_file=args.output, color = args.color, 
                    min_weight = int(args.min_weight), radius = int(args.radius))

if __name__ == "__main__":
    main()