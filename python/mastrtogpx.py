#!/usr/bin/env /home/eduard/.venv/waerme/bin/python
# -*- coding: utf-8 -*-

"""
Script to convert the mastr file to a gpx file
with the help of the analyse_mastr.py script
calling convention:
    python mastrtogpx.py <path to mastr file> -q '<query>' -o <path to output gpx file>
"""

import argparse
from analyse_mastr import Analyse   # Import the Analyse class from analyse_mastr.py

def main():
    parser = argparse.ArgumentParser(description="Convert MaStR file to GPX file")
    parser.add_argument("mastr_file", help="Path to the MaStR CSV file")
    parser.add_argument("-q", "--query", help="Query to filter the data", default=None)
    parser.add_argument("-o", "--output", help="Path to the output GPX file", default=None)
    parser.add_argument("-c", "--color", help="Color of Waypoints", default="Amber")
    parser.add_argument("-s", "--show-columns", help="Show the columns of the MaStR file", action="store_true")
    parser.add_argument("-h_query", "--help_query", help="Show Examples for Query", action="store_true")
    args = parser.parse_args()

    # Create an instance of the Analyse class
    if args.help_query:
        print("Query to filter the data")
        print("Example: -q 'is_active & is_pv'")
        print("Example: -q 'BetriebsStatus != \"In Betrieb\" & is_pv & is_10mw'")
        print("Example: -q 'is_pv & Ort == \"Berlin\"'")
        print("Example: -q 'EnergieTräger == \"Erdgas\"'")
        return

    analyse = Analyse(file_path=args.mastr_file)
    if args.show_columns:
        print("Columns in the MaStR file:")
        print(analyse.show_columns("    "))
        return
    
    # Generate the GPX file
    if args.output is None:
        print("Please provide an output file (-o option)")
        parser.print_help()
        return
    analyse.gen_gpx(conditions=args.query, output_file=args.output, color = args.color)

if __name__ == "__main__":
    main()