#!/usr/bin/python

# -*- coding: utf-8 -*-

# Module metadata variables
__author__ = "David del Rio Aledo"
__credits__ = ["David del Rio Aledo", "Jesus Vazquez"]
__license__ = "Creative Commons Attribution-NonCommercial-NoDerivs 4.0 Unported License https://creativecommons.org/licenses/by-nc-nd/4.0/"
__version__ = "0.1.0"
__maintainer__ = "David del Rio Aledo"
__email__ = "ddelrioa@cnic.es"
__status__ = "Development"

# import modules
import argparse
import configparser
import logging
import numpy as np
import os
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import scipy.optimize
import sys
import pandas as pd
import re
import inspect

def readfile_txt (file, message):

	"""
	### No readable function ###

    """

	try:

		df=pd.read_csv(file, sep='\t')

		return df

	except FileNotFoundError:
		print(message+ str(file) + '\n')
		sys.exit(1)


def main(args):


	#df_mods=readfile_txt(Path(r'S:\U_Proteomica\UNIDAD\Softwares\ClOpen_IDq\temp_table_clopen.txt'))
	#params_close=r'C:\Users\ddelrioa\Downloads\ClOpen_KK\config\Closed-MSFragger-4.1\config_params_Closed_MSFragger-4.1.new'

	df_mods=readfile_txt(Path(args.headers), '\n###		FILE NOT FOUND 		###\n\nTable of Close Search File not found (comand -l). Please check the path:\n')
	params_close=args.closeconfig
	program_basename=os.path.splitext(os.path.basename(params_close))[0]
	directory=args.output

	print(df_mods)

	max_var_mods=args.variablemods
	search_engine=args.searchengine

	search_numbers = df_mods['Search Number'].unique()

	# Comprobar que los valores están bien introducidos
	try:
		int_value=int(max_var_mods)

	except ValueError:
		print('\n###		MAX VARIABLE MODIFITICATION ERROR 		###\n\nValue introduced in variablemods (comand -var) is not valid. Please check the value\n')
		sys.exit(1)
	
	if "comet" in search_engine.lower() or "fragger" in search_engine.lower():
		pass

	else:
		print('\n###		SEARCH ENGINE NAME ERROR 		###\n\nThe name introduced as the search engine does not correspond to any search engine included in the program. Please check the name\n')
		sys.exit(1)

	if os.path.exists(params_close):
		pass

	else:
		print('\n###		FILE NOT FOUND 		###\n\nConfiguration Params File not found (comand -cl). Please check the path:\n')
		sys.exit(1)


	if os.path.exists(directory):

		if os.path.isdir(directory):
			pass

		else:
			print('\n###		OUTPUT DIRECTORY NOT FOUND 		###\n\nOutput directory inserted is not a directory (comand -o). Please check the path:\n')
			sys.exit(1)

	else:
		print('\n###		OUTPUT DIRECTORY NOT FOUND 		###\n\nOutput directory not found (comand -o). Please check the path:\n')
		sys.exit(1)




	if params_close:

		for search_number in search_numbers:

			print('Creating Configuration File of Search number '+ str(search_number))

			df_filtered_mods = df_mods[df_mods['Search Number'] == search_number]
			mod_id = 1

			with open(params_close,'r') as file:
				lines=file.readlines()

			updated_lines = []
			added_var_mods=set()
			mods_lines=[]
			mod_start_index = None


			for line in lines:
			    modified = False
			    updated_line=line.strip()

			    for index, row in df_filtered_mods.iterrows():

			        modification_name = row['Modification']
			        amino_acids = row['Position']
			        var_mod=row['Variable Modification']
			        mod_key = f"variable_mod_{mod_id:02d}"

			        mass_match = re.search(r'\(([\d.]+)\)', modification_name)

			        if mass_match:
			        	mass = float(mass_match.group(1))


			        found=False

		        	if var_mod == "No":

		        		for aa in amino_acids.split(','):

		        			if line.strip().startswith(f'add_{aa}_'):
			        			updated_line = re.sub(r'=(\s*)(\d+\.\d+|\d+\.|\.\d+|\d+)(\s*#.*)?$', f'= {mass}', updated_line)
			        			updated_lines.append(updated_line)
			        			modified = True
			        			break

			        # No juntar las variable mods que hay por defecto y obtener la posicion donde empiezan para que en el output
			        #aparezcan en la misma posicion

			        if var_mod=="Yes":
			        	match = re.match(f'(#\s*)?variable_mod_\\d{{2}}\\s*=', line.strip())
			        	match_comet=re.match(f'(#\s*)?variable_mod\\d{{2}}\\s*=', line.strip())

			        	if  match:
			        		modified = True

			        		if not mods_lines:
			        			mod_start_index = len(updated_lines)

			        	if match_comet:
			        		modified = True

			        		if not mods_lines:
			        			mod_start_index = len(updated_lines)


			        if modified:
			            break

			    if not modified:
			        updated_lines.append(updated_line)

	        # Añadir modificaciones variables si hay espacio
			for index, row in df_filtered_mods.iterrows():

			    if mod_id > 16:
			        break

			    if f"variable_mod_{mod_id:02d}" not in added_var_mods:
			        modification_name = row['Modification']
			        amino_acids = row['Position']
			        var_mod = row['Variable Modification']

			        if var_mod == "Yes":

			            if search_engine == "Fragger":

			                mass_match = re.search(r'\(([\d.]+)\)', modification_name)

			                if mass_match:
			                    mass = float(mass_match.group(1))
			                    aa = ''.join(amino_acids.split(','))
			                    new_mod_line = f"variable_mod_{mod_id:02d} = {mass} {aa} {max_var_mods}"
			                    mods_lines.append(new_mod_line)
			                    added_var_mods.add(f"variable_mod_{mod_id:02d}")
			                    mod_id += 1

			            elif search_engine == "Comet":
			                mass_match = re.search(r'\(([\d.]+)\)', modification_name)

			                if mass_match:
			                    mass = float(mass_match.group(1))
			                    aa = ''.join(amino_acids.split(','))
			                    new_mod_line = f"variable_mod{mod_id:02d} = {mass} {aa} {max_var_mods} -1 0 0 0.0"
			                    mods_lines.append(new_mod_line)
			                    added_var_mods.add(f"variable_mod{mod_id:02d}")
			                    mod_id += 1



			if mod_start_index is not None:
				updated_lines[mod_start_index:mod_start_index] = mods_lines

			with open(rf'{directory}/{program_basename}_Search_{search_number}.new', 'w') as file:
				updated_lines='\n'.join(updated_lines)
				file.write(updated_lines)


if __name__ == '__main__':

    # parse arguments
    parser = argparse.ArgumentParser(
        description='ClOpen Config Creator',
        epilog='''
        Create diferent config params from a table of modifications

        ''')
        
    
    parser.add_argument('-cl',  '--closeconfig', required=False, help='Configurations params file of Closed Search')
    parser.add_argument('-l', '--headers', required=False, help='Table of Close Search in Cl-Open Search function')
    parser.add_argument('-var', '--variablemods', required=False, help='Maximun of variable modifications for peptide')
    parser.add_argument('-o',  '--output', required=False, help='Output directory')
    parser.add_argument('-e',  '--searchengine', required=False, help='Search engine selected: Comet or MSFragger')
    args = parser.parse_args()
    

    # logging debug level. By default, info level
    log_file = outfile = os.path.join(os.getcwd(), 'ConfigCreator_log.txt')
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        handlers=[logging.FileHandler(log_file),
                                    logging.StreamHandler()])

    # start main function
    logging.info('start script: '+"{0}".format(" ".join([x for x in sys.argv])))
    main(args)
    logging.info('end script')

