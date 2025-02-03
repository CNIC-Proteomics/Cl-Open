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

def readfile_comet (file):

    """
    Read input file to dataframe.

    ### No readable function ###

    """

    '### No readable function ###'

    try:
    	df = pd.read_csv(file,sep='\t', skiprows=1, float_precision='high', low_memory=False, index_col=False)
    	return df

    except FileNotFoundError:
    	print('\n###		FILE NOT FOUND 		###\n\nOpen File ruth not found (comand -op). Please check the path:\n'+ str(file) + '\n')

    	sys.exit(1)

    

def readfile_txt (file):

	"""
	### No readable function ###

    """

	try:

		df=pd.read_csv(file, sep='\t')

		return df

	except FileNotFoundError:
		print('\n###		FILE NOT FOUND 		###\n\nClose File ruth not found (comand -cl). Please check the path:\n'+ str(file) + '\n')
		sys.exit(1)


def readfile (file):

	"""
	### No readable function ###

	"""

	try:

		extension=str(file).split('.')[-1].lower()

		if extension in ['txt','csv']:

			# Abre el archivo y lee la primera línea
			with open(file, 'r') as f:
				primera_linea = f.readline()

			if 'CometVersion' in primera_linea:
				# Lee el resto del archivo, comenzando desde la segunda línea
				df = pd.read_csv(file, delimiter='\t', skiprows=1)

			else:
				print(file)

				df=pd.read_csv(file, sep='\t')


		elif extension == 'feather':

			df=pd.read_feather(file)

		elif extension == 'xml':

			df=pd.read_xml(file)

		else:

			print('\n###		TIPE FILE ERROR 		###\n\nFile extension not suported: '+ str(extension) + '\n')

		return df


	except FileNotFoundError:
		print('\n###		FILE NOT FOUND 		###\n\nClose File ruth not found (comand -cl). Please check the path:\n'+ str(file) + '\n')
		sys.exit(1)


def readfile_xml (file):

	"""
	### No readable function ###

    """

	try:

		df=pd.read_xml(file)

		return df

	except FileNotFoundError:
		print('\n###		FILE NOT FOUND 		###\n\nProteome Discovere modification list File ruth not found (comand -mdl). Please check the path:\n'+ str(file) + '\n')
		sys.exit(1)

def num_function (df, column, num_value):

	try:

		df[column]=num_value

	except:
		logging.info('\n\n###		FUNCTION ERROR 		###\n\nSomething went wrong with the function "num_function", please check the selection of required columns in the configuration file to execute this function correct.\n'+
			'If you have doubts about how the function works, please review the instructions or contact support.')
		sys.exit(1)

	return df

def xcorr_corr (df, column, xcorr, sequence, charge):
    
    ### Calculate cXCorr ###

    try:

    	rc=np.where(df[charge]>=3, '1.22', '1').astype(float)
    	cXCorr1= np.log(df[xcorr]/rc)/np.log(2*df[sequence].str.len())

    	df[column]=cXCorr1

    except:
    	logging.info('\n\n###		FUNCTION ERROR 		###\n\nSomething went wrong with the function "xcorr_corr", please check the selection of required columns in the configuration file to execute this function correct.\n'+
    		'Remember that this function requieres the xcorr values, charge values and plain sequence to get the peptide legth.\n' + 'If you have doubts about how the function works, please review the instructions or contact support.')
    	sys.exit(1)
    
    return df

def change_modifiedpeptide (df,column, annotated_close):

	### Change Annotated sequence from PD as Comet format ###

	try:

		df[column]=df[annotated_close].str.replace('[','').str.replace(']', '').str.upper()

	except:
		logging.info('\n\n###		FUNCTION ERROR 		###\n\nSomething went wrong with the function "change_modifiedpeptide", please check the selection of required columns in the configuration file to execute this function correct.\n'+
			'If you have doubts about how the function works, please review the instructions or contact support.')
		sys.exit(1)

	return df

def prev_aa (df,column, annotated_close):

	### Get previous aa ###

	try:

		df[column]=df[annotated_close].str.extract(r'\[(\w)\]')

	except:
		logging.info('\n\n###		FUNCTION ERROR 		###\n\nSomething went wrong with the function "prev_aa", please check the selection of required columns in the configuration file to execute this function correct.\n'+
			'Remember that this function requieres the last aminoacid indicate with this structurte [R].\n' + 'If you have doubts about how the function works, please review the instructions or contact support.')
		sys.exit(1)

	return df


def next_aa (df,column, annotated_close):

	### Get next aa ###

	try:

		df[column]=df[annotated_close].str.extract(r'\[([^\]]+)\]$')

	except:
		logging.info('\n\n###		FUNCTION ERROR 		###\n\nSomething went wrong with the function "next_aa", please check the selection of required columns in the configuration file to execute this function correct.\n'+
			'Remember that this function requieres the first aminoacid indicate with this structurte [R].\n' + 'If you have doubts about how the function works, please review the instructions or contact support.')
		sys.exit(1)

	return df

def change_sep(df, column, protein_close):

	### Change sep ; for , ###

	try:

		df[column]=df[protein_close].str.replace(';',',')

	except:
		logging.info('\n\n###		FUNCTION ERROR 		###\n\nSomething went wrong with the function "change_sep", please check the selection of required columns in the configuration file to execute this function correct.\n'+
			'Remember that this function requieres strings separated with ; to change to ,.\n' + 'If you have doubts about how the function works, please review the instructions or contact support.')
		sys.exit(1)

	return df

def count_acc (df, column, protein_close):

	### Count ###

	try:

		df[column]=df[protein_close].str.split(',').apply(len)

	except:
		logging.info('\n\n###		FUNCTION ERROR 		###\n\nSomething went wrong with the function "count_acc", please check the selection of required columns in the configuration file to execute this function correct.\n'+
			'Remember that this function requieres strings separated with ,.\n' + 'If you have doubts about how the function works, please review the instructions or contact support.')
		sys.exit(1)

	return df

def exp_mz_from_MH(df, column, MH, charge):

	try:
		df[column]=(df[MH] + (df[charge]-1) * 1.007276)/df[charge]

	except:
		logging.info('\n\n###		FUNCTION ERROR 		###\n\nSomething went wrong with the function "exp_mz", please check the selection of required columns in the configuration file to execute this function correct.\n'+
			'Remember that this function requieres numbers in the columns: MH and chanrge.\n' + 'If you have doubts about how the function works, please review the instructions or contact support.')
		sys.exit(1)

	return df

def exp_mz_from_neutral(df, column, MH, charge):

	try:
		df[MH]=(df[MH]+1.007276)
		df[column]=(df[MH] + (df[charge]-1) * 1.007276)/df[charge]

	except:
		logging.info('\n\n###		FUNCTION ERROR 		###\n\nSomething went wrong with the function "exp_mz", please check the selection of required columns in the configuration file to execute this function correct.\n'+
			'Remember that this function requieres numbers in the columns: MH and chanrge.\n' + 'If you have doubts about how the function works, please review the instructions or contact support.')
		sys.exit(1)

	return df

def exp_neutral_mass (df, column, MH, charge):

	try:

		MassMod_path= os.path.join(os.getcwd(), "config/MassMod.ini")

		MassMod = configparser.ConfigParser(inline_comment_prefixes='#')
		MassMod.read(MassMod_path)

	except:
		logging.info('\n\n###		CONFIGURATION ERROR 		###\n\nMassMod.ini file has not been found in the config folder. Please check if exists that file.\n'+
			'If you have doubts about how the function works, please review the instructions or contact support.')
		sys.exit(1)


	try:

	    m_proton = MassMod.getfloat('Masses', 'm_proton')
	    m_hydrogen = MassMod.getfloat('Masses', 'm_hydrogen')
	    m_oxygen = MassMod.getfloat('Masses', 'm_oxygen')

	except:

		logging.info('\n\n###		CONFIGURATION ERROR 		###\n\nIt not find "Fixed Modifications" configuration in MassMod.ini of config folder. Please check if exists that configuration.\n'+
			'If you have doubts about how the function works, please review the instructions or contact support.')
		sys.exit(1)


	try:
    
		#df[column] = df[MH] + (df[charge]-1)*m_proton
		df[column]=df[MH] - 1.007276


	except:

		logging.info('\n\n###		FUNCTION ERROR 		###\n\nSomething went wrong with the function "exp_neutral_mass", please check the selection of required columns in the configuration file to execute this function correct.\n'+
			'If you have doubts about how the function works, please review the instructions or contact support.')
		sys.exit(1)

	return df



def theorical_mass(df, column, sequence, charge):

	try:

		MassMod_path= os.path.join(os.getcwd(), "config/MassMod.ini")

		MassMod = configparser.ConfigParser(inline_comment_prefixes='#')
		MassMod.read(MassMod_path)

	except:
		logging.info('\n\n###		CONFIGURATION ERROR 		###\n\nMassMod.ini file has not been found in the config folder. Please check if exists that file.\n'+
			'If you have doubts about how the function works, please review the instructions or contact support.')
		sys.exit(1)


	try:

		AAs = dict(MassMod._sections['Aminoacids'])

	except:
		logging.info('\n\n###		CONFIGURATION ERROR 		###\n\nIt not find "Aminoacids" configuration in MassMod.ini of config folder. Please check if exists that configuration.\n'+
			'If you have doubts about how the function works, please review the instructions or contact support.')
		sys.exit(1)


	try:
	    MODs = dict(MassMod._sections['Fixed Modifications'])

	except:
		logging.info('\n\n###		CONFIGURATION ERROR 		###\n\nIt not find "Fixed Modifications" configuration in MassMod.ini of config folder. Please check if exists that configuration.\n'+
			'If you have doubts about how the function works, please review the instructions or contact support.')
		sys.exit(1)

	try:

	    m_proton = MassMod.getfloat('Masses', 'm_proton')
	    m_hydrogen = MassMod.getfloat('Masses', 'm_hydrogen')
	    m_oxygen = MassMod.getfloat('Masses', 'm_oxygen')

	except:

		logging.info('\n\n###		CONFIGURATION ERROR 		###\n\nIt not find "Fixed Modifications" configuration in MassMod.ini of config folder. Please check if exists that configuration.\n'+
			'If you have doubts about how the function works, please review the instructions or contact support.')
		sys.exit(1)

	def _PSMtoMZ(sequence, charge):

		total_aas = 2*m_hydrogen + m_oxygen
		total_aas += charge*m_proton
		total_aas += float(MODs['nt']) + float(MODs['ct'])

		for aa in sequence:
		    if aa.lower() in AAs:
		        total_aas += float(AAs[aa.lower()])
		    #else: # aminoacid not in list (ask for user input?)
		        # TODO
		    if aa.lower() in MODs:
		        total_aas += float(MODs[aa.lower()])

		#MH = total_aas - (charge-1)*m_proton
		theorical = total_aas
		#MZ = (total_aas + int(charge)*m_proton) / int(charge)
		MZ = total_aas / int(charge)

		return MZ, theorical

	try:
    
		df[column] = df.apply(lambda x: _PSMtoMZ(x[sequence], x[charge])[0], axis = 1)
		df[column] = df.apply(lambda x: _PSMtoMZ(x[sequence], x[charge])[1], axis = 1)


	except:

		logging.info('\n\n###		FUNCTION ERROR 		###\n\nSomething went wrong with the function "theorical_mass", please check the selection of required columns in the configuration file to execute this function correct.\n'+
			'If you have doubts about how the function works, please review the instructions or contact support.')
		sys.exit(1)


	return df




def NA_def (df, column):

	try:

		df[column]=''

	except:
		logging.info('\n\n###		FUNCTION ERROR 		###\n\nSomething went wrong with the function "NA_def", please check the selection of required columns in the configuration file to execute this function correct.\n'+
			'If you have doubts about how the function works, please review the instructions or contact support.')
		sys.exit(1)

	return df


def set_fix_mod (df, column, modifications_close, nterm_name_modifications_close, NameDM_close_list, NameMod_close_list, 
	DM_close_list, dm_error, dm_fix_list, sequence, delta_mods, delta_peptide):

	### Extract fix modifications and change format to Comet-PTM ####

	def get_structure (modifications):

		new_fix_mod=[]
		var_mod_close=[]
		var_mod_close_position=[]
		mod_close_to_open=None
		mod_close_to_open_position=None

		for i in modifications.split('; '):

			match=re.match(r"(N-Term|\D+(\d+))\(([^)]+)\)", i)

			#position, mod_name=i.split('(')[0], i.split('(')[1].split(')')[0]
			full_position=match.group(1)
			position=match.group(2) if match.group(2) else full_position
			mod_name=match.group(3)
			dm_row =DM_close_list[DM_close_list[NameMod_close_list] == mod_name]

			### Identicar Modificaciones Fijas y buscar la dm y poner en formato COMET ###

			if not dm_row.empty:
				dm=dm_row[NameDM_close_list].iloc[0]

				if nterm_name_modifications_close in position:
					position=1

				else:
					position=position

				if any(abs(dm - float(fix)) < dm_error for fix in dm_fix_list):
					structure=f"{position}_S_{dm}"

					if position == 1:
						structure += '_n'

					new_fix_mod.append(structure)

				else:

					### Optener las modificaciones que no han sido localizadas como fijas y ponerlas en una columna como variables ###

					var_mod_close.append(str(dm))
					var_mod_close_position.append(str(position))

		### Optener la suma de las deltamasas y un promedio de la posicion para adaptar el formato al open ###

		if var_mod_close:

			mod_close_to_open=sum(list(map(float, var_mod_close)))

			positions_to_av=list(map(int,var_mod_close_position))
			mod_close_to_open_position= str(int(round(sum(positions_to_av)/len(positions_to_av))))


		return '; '.join(new_fix_mod), ';'.join(var_mod_close), ';'.join(var_mod_close_position), mod_close_to_open, mod_close_to_open_position

	def get_deltapeptide (peptide):

		### Coge las modificaciones clasificadsa como variables y la posicion y la inserta dentro de la secuencia plana para generar una secuencia con las dm ###

		seq=peptide[sequence]
		mods_close=peptide['delta_mods_cl'].split(';') if peptide['delta_mods_cl'] else ['0.00']
		positions_close=list(map(int, peptide['delta_mods_cl_position'].split(';'))) if peptide['delta_mods_cl_position'] else [1]

		mods= [str(peptide[delta_mods])] if not pd.isna(peptide[delta_mods]) else ['0.00']
		positions=int(peptide[delta_mods+'_position']) if peptide[delta_mods+'_position'] else 1

		seq_list=list(seq)
		seq_list_close=list(seq)

		for mod, pos in zip(mods_close, positions_close):
			index= pos -1
			seq_list_close[index] = f"{seq_list_close[index]}[{mod}]"

		seq_list[positions-1] = f"{seq_list[positions-1]}[{mods[0]}]"

		return ''.join(seq_list), ''.join(seq_list_close)


	try:
		df[[column, 'delta_mods_cl','delta_mods_cl_position', delta_mods, delta_mods + '_position']]=df[modifications_close].apply(lambda x: pd.Series(get_structure(x)))
	
	except:
		logging.info('\n\n###		FUNCTION ERROR 		###\n\nSomething went wrong with "get_structure" of the function "set_fix_mod", please check the selection of required columns in the configuration file to execute this function correct.\n'+
			'If you have doubts about how the function works, please review the instructions or contact support.')
		sys.exit(1)

	try:

		df[[delta_peptide, 'delta_peptide_cl']]=df.apply(lambda x: pd.Series(get_deltapeptide(x)), axis=1)
		df[delta_mods]=df[delta_mods].fillna(0.00)


	except:
		logging.info('\n\n###		FUNCTION ERROR 		###\n\nSomething went wrong with "get_deltapeptide" of the function "set_fix_mod", please check the selection of required columns in the configuration file to execute this function correct.\n'+
			'If you have doubts about how the function works, please review the instructions or contact support.')
		sys.exit(1)


	return df

def fusion_files (df_open, df_close, scan):

	### Une los dataframes del close y del open en base al scan ###

	try:
		#merged_df=pd.merge(df_open,df_close, how='outer', on=scan, suffixes=('', '_close'))

		merged_df = pd.concat([df_open, df_close], ignore_index=True)

		try:
			merged_df = merged_df.drop_duplicates()
		except:
			pass

		df_close.columns = [col + '_close' for col in df_close.columns]


	except:
		logging.info('\n\n###		FUNCTION ERROR 		###\n\nSomething went wrong with the function "fusion_files". The close and open files could not be merged.\n Please check the configuration file. \n'+
			'If you have doubts, please review the instructions or contact support.')
		sys.exit(1)

	for col in df_open.columns:

		if col in df_close.columns and col != scan:
			merged_df[col] = merged_df[col].combine_first(merged_df[col+'_close'])
			merged_df.drop(col +'_close', axis=1, inplace=True)

	#merged_df.drop([col for col in df_close.columns if col != 'scan'], axis=1, inplace=True)


	return merged_df

def filter_scans(df, filter_mod, AnalysisMethod, xcorr_column, scan, num, spscore):

	### Filtra y remueve duplicados en el dataframe clopen, se puede hacer a nivel de xcorr o priorizar uno frente otro ###

	if filter_mod !='xcorr' and filter_mod!='close' and filter_mod != 'open':

		logging.info('\n\n###		FUNCTION ERROR 		###\n\nFilter_mod can only take the values "xcorr", "close", or "open", and you have entered this in the configuration file: ' + str(filter_mod) + ' .Please select one of the three options.')
		sys.exit(1)


	if filter_mod=='xcorr':

		try:
			df.sort_values([scan, num, xcorr_column, spscore], ascending=[True, True, False, False], inplace=True)
			df.drop_duplicates(subset=[scan], keep='first', inplace=True)
			df.reset_index(drop=True, inplace=True)

		except:
			logging.info('\n\n###		FUNCTION ERROR 		###\n\nSomething went wrong with the function "filter_scans". The "xcorr" filter could not be applied correctly.\n Please check the configuration file and that there are numerical values in columns: \n'+
				str(scan) +', ' + str(num) + ', ' + str(xcorr_column) + ', ' + str(spscore) + '.'+ '\nIf you have doubts, please review the instructions or contact support.')
			sys.exit(1)

	if filter_mod=='close':

		try:
			df.sort_values([scan, AnalysisMethod], ascending=[True, True], inplace=True)
			df.drop_duplicates(subset=[scan], keep='first', inplace=True)
			df.reset_index(drop=True, inplace=True)

		except:
			logging.info('\n\n###		FUNCTION ERROR 		###\n\nSomething went wrong with the function "filter_scans". The "close" filter could not be applied correctly.\n Please check the configuration file and that there are numerical values in columns: \n'+
				str(scan) + '\nIf you have doubts, please review the instructions or contact support.')
			sys.exit(1)

	if filter_mod=='open':

		try:
			df.sort_values([scan, AnalysisMethod], ascending=[True, False], inplace=True)
			df.drop_duplicates(subset=[scan], keep='first', inplace=True)
			df.reset_index(drop=True, inplace=True)

		except:
			logging.info('\n\n###		FUNCTION ERROR 		###\n\nSomething went wrong with the function "filter_scans". The "open" filter could not be applied correctly.\n Please check the configuration file and that there are numerical values in columns: \n'+
				str(scan) + '\nIf you have doubts, please review the instructions or contact support.')
			sys.exit(1)

	return df

def filter_pep_ptm (df, file, sequence_close):

	with open(file, 'r') as fil:
		values=[line.strip() for line in fil]

	filters=df[sequence_close].isin(values)

	return filters

def check_function_existence(row, function_column):

    function_name = row[function_column]

    return function_name if globals().get(function_name) is None else None

def z_sum_dm (df, column, delta_mods):

	df[column] = df[column].astype(float)+ df[delta_mods].astype(float)

	return df


def modvar_comet (df, column,delta_mods,delta_peptide, sequence):

	def extract_s (value):

		return ','.join([item for item in value.split(',') if '_S_' in item])

	def extract_v (value):

		variable_mods=[item for item in value.split(',') if '_V_' in item]

		positions=None
		mods=None
		total=None
		positions_to_av=None
		total_position=None

		if variable_mods:

			positions=[int(item.split('_')[0]) for item in variable_mods]
			mods=[float(item.split('_')[2]) for item in variable_mods]

			total=str(sum(mods))

			total_position=str(int(round(sum(positions)/len(positions))))

			variable_mods=';'.join(variable_mods)
			positions=';'.join(map(str,positions))
			mods=';'.join(map(str,mods))

		else:
			variable_mods=""


		return variable_mods, total, positions, mods, total_position

	def get_deltapeptide (peptide):

		### Coge las modificaciones clasificadsa como variables y la posicion y la inserta dentro de la secuencia plana para generar una secuencia con las dm ###

		seq=peptide[sequence]
		mods_close=peptide['delta_mods_cl'].split(';') if peptide['delta_mods_cl'] else ['0.00']
		positions_close=list(map(int, peptide['delta_mods_cl_position'].split(';'))) if peptide['delta_mods_cl_position'] else [1]

		mods= [str(peptide[delta_mods])] if not pd.isna(peptide[delta_mods]) else ['0.00']
		positions=int(peptide[delta_mods+'_position']) if peptide[delta_mods+'_position'] else 1

		seq_list=list(seq)
		seq_list_close=list(seq)

		for mod, pos in zip(mods_close, positions_close):
			index= pos -1
			seq_list_close[index] = f"{seq_list_close[index]}[{mod}]"

		seq_list[positions-1] = f"{seq_list[positions-1]}[{mods[0]}]"

		return ''.join(seq_list), ''.join(seq_list_close)

	def dm_peptide (seq, dm, pos):

		seq_list=list(seq)

		for m, p in zip(dm, pos):
			index=p-1
			seq_list[index]=f"{seq_list[index]}[{m}]"

		return ''.join(seq_list)


	try:


		extr_v=df[column].apply(extract_v)

		df['Variable_Mods']=extr_v.apply(lambda x:x[0])
		df[delta_mods]=extr_v.apply(lambda x:x[1])
		df['delta_mods_cl_position']=extr_v.apply(lambda x:x[2])
		df['delta_mods_cl']=extr_v.apply(lambda x:x[3])
		df[delta_mods + '_position']=extr_v.apply(lambda x:x[4])
		df[[delta_peptide, 'delta_peptide_cl']]=df.apply(lambda x: pd.Series(get_deltapeptide(x)), axis=1)
		df[delta_mods]=df[delta_mods].fillna(0.00)
		df[column]=df[column].apply(extract_s)
	
	except:

		logging.info('\n\n###		FUNCTION ERROR 		###\n\nSomething went wrong with "modvar_comet" function, please check the selection of required columns in the configuration file to execute this function correct.\n'+
			'If you have doubts about how the function works, please review the instructions or contact support.')
		sys.exit(1)

	return df


### Custom Functions ###




########################



def main(args):

	"""
	### No readable function ###

    """



	###  Leer config File ###

	if os.path.exists(args.config):
		pass

	else:
		logging.info('\n\n###		FILE NOT FOUND 		###\n\nConfiguration File ruth not found (comand -c). Please check the path:\n'+ str(args.config) + '\n')
		sys.exit(1)

	config = configparser.ConfigParser(inline_comment_prefixes='#')
	config.read(args.config)


	### Open File arguments ###

		### Generar una clase vacia para almacenar la configuracion

	class ConfigObject:

		pass

	def load_config_to_object(config_path, section):

	    # Crear una instancia de ConfigObject
	    config_obj = ConfigObject()
	    
	    if section in config:

	        for key, value in config[section].items():

	            # Convertir a los tipos adecuados según sea necesario
	            if value.isdigit():
	                value = int(value)

	            else:

	                try:
	                    value = float(value)
	                except ValueError:
	                    pass

	            # Asignar el valor al objeto
	            setattr(config_obj, key, value)

	    return config_obj

	try:

		config_obj=load_config_to_object(config, "ClOpen")
		config_dict=vars(config_obj)


		sequence=config["ClOpen"].get("sequence")
		charge=config["ClOpen"].get('charge')
		exp_neutral_mass=config["ClOpen"].get('exp_neutral_mass')
		delta_mods=config["ClOpen"].get('delta_mods')
		delta_peptide=config["ClOpen"].get('delta_peptide')
		scan=config["ClOpen"].get('scan')
		num=config["ClOpen"].get('num')
		score=config["ClOpen"].get('score')
		spscore=config["ClOpen"].get('spscore')

		### Close File arguments ###

		sequence_close = config["ClOpen"].get("sequence_close")
		xcorr=config["ClOpen"].get('xcorr')
		num_value=config["ClOpen"].getint('num_value')
		annotated_close=config["ClOpen"].get('annotated_close')
		protein_close=config["ClOpen"].get('protein_close')
		modifications_close=config["ClOpen"].get('modifications_close')
		nterm_name_modifications_close=config["ClOpen"].get('nterm_name_modifications_close')
		MH=config["ClOpen"].get('MH')

		### Proteome Discoverer arguments ###
		

		NameDM_close_list=config["ClOpen"].get('NameDM_close_list')
		NameMod_close_list=config["ClOpen"].get('NameMod_close_list')
		dm_error=config["ClOpen"].getfloat('dm_error')

		### Scan Filter arguments ###

		filter_mod=config["ClOpen"].get('filter_mod')

		### Headers List Columns names ###

		open_header = config["ClOpen"].get('open_header')
		close_header = config["ClOpen"].get('close_header')
		function_header = config["ClOpen"].get('function_header')


	except KeyError:
		logging.info('\n###		INCORRECT CONFIGURATION FILE 		###\n\nThe [ClOpen] configuration was not found in the configuration file.\nPlease check if the file includes this configuration or if you have accidentally edited the name of the configuration:\n'+ str(args.config) + '\n')
		sys.exit(1)

	### ClOpen Fix Modification List ###

	dm_fix_list=[]

	try:

		for key, value in config['ClOpen Fix Close Modifications'].items():

			dm_fix_list.append(float(value.strip()))

	except KeyError:
		logging.info('\n###		INCORRECT CONFIGURATION FILE 		###\n\nThe [ClOpen Fix Close Modifications] configuration was not found in the configuration file.\nPlease check if the file includes this configuration or if you have accidentally edited the name of the configuration:\n'+ str(args.config) + '\n')
		sys.exit(1)

	logging.info('Configuration File read successfully!')


	### Folder processing ###

	path_eq=readfile(Path(args.patheq))

	for index, row in path_eq.iterrows():

		open_ruth=row[0]
		close_ruth=row[1]

		logging.info('Processing this files:\n' + 'Open path: ' + open_ruth +'\nClose path: ' + close_ruth +'\n')

		### Read Close and Open Files ###

		
		df_open = readfile(Path(open_ruth))
		df_open['AnalysisMethod']='OpenSearch'
		df_open["Raw"] = os.path.basename(Path(open_ruth))

		logging.info('Open File read successfully!')


		df_close= readfile(Path(close_ruth))
		df_close['AnalysisMethod']='ClosedSearch'
		df_close["Raw"] = os.path.basename(Path(close_ruth))

		logging.info('Close File read successfully!')


		### Read Peptides and PTMs files and filter Close file ###


		if args.peptides and args.ptm:

			if os.path.exists(args.peptides):
				logging.info('Peptides List File read successfully!')

			else:
				logging.info('\n\n###		FILE NOT FOUND 		###\n\nPeptides File ruth not found (comand -pep). Please check the path:\n'+ str(args.peptides) + '\n')
				sys.exit(1)

			if os.path.exists(args.ptm):
				logging.info('Modifications List File read successfully!')

			else:
				logging.info('\n\n###		FILE NOT FOUND 		###\n\nModifications File ruth not found (comand -mod). Please check the path:\n'+ str(args.ptm) + '\n')
				sys.exit(1)

			fil_pep=filter_pep_ptm(df_close, args.peptides, sequence_close)
			fil_ptm=filter_pep_ptm(df_close, args.ptm, sequence_close)

			df_close=df_close[fil_pep | fil_ptm]

			logging.info('Close File data filtered by peptides and PTMs successfully!')
			logging.info('Close File has retrieved ' + str(df_close.shape[0]) + ' scans to include in Open File.\n')

		if args.ptm and not args.peptides:

			if os.path.exists(args.ptm):
				logging.info('Modifications List File read successfully!')

			else:
				logging.info('\n\n###		FILE NOT FOUND 		###\n\nModifications File ruth not found (comand -mod). Please check the path:\n'+ str(args.ptm) + '\n')
				sys.exit(1)

			df_close=filter_pep_ptm(df_close, args.ptm, sequence_close)

			logging.info('Close File data filtered by PTMs successfully!')
			logging.info('Close File has retrieved ' + str(df_close.shape[0]) + ' scans to include in Open File.\n')

		if args.peptides and not args.ptm:

			if os.path.exists(args.peptides):
				logging.info('Peptides List File read successfully!')

			else:
				logging.info('\n\n###		FILE NOT FOUND 		###\n\nPeptides File ruth not found (comand -pep). Please check the path:\n'+ str(args.peptides) + '\n')
				sys.exit(1)

			df_close=filter_pep_ptm(df_close, args.peptides, sequence_close)

			logging.info('Close File data filtered by peptides successfully!')
			logging.info('Close File has retrieved ' + str(df_close.shape[0]) + ' scans to include in Open File.\n')


		###  Read Headers table configuration  ###


		df_headers=readfile(Path(args.headers))
		df_headers=df_headers.sort_values(by=function_header, key=pd.isna, ascending=False)
		df_headers=df_headers.reset_index(drop=True)

			# Comprobar que los headers de la configuracíon se encuentran en el archivo headers #

		try:
			open_values=set(df_headers[open_header])

		except KeyError:
			logging.info('\n\n###		INCORRECT HEADER 		###\n\nThe header: ' + str(open_header) + ' does not match any of the headers in Header List File (command -l). Please check the configuration file or Header list file:\n'+
				'\tHeader List File: ' + str(args.headers) + '\n' + '\tConfig File: ' + str(args.config) + '\n')
			sys.exit(1)

		try:
			close_values=set(df_headers[close_header])

		except KeyError:
			logging.info('\n\n###		INCORRECT HEADER 		###\n\nThe header: ' + str(close_header) + ' does not match any of the headers in Header List File (command -l). Please check the configuration file or Header list file:\n'+
				'\tHeader List File: ' + str(args.headers) + '\n' + '\tConfig File: ' + str(args.config) + '\n')
			sys.exit(1)

		try:
			function_values=set(df_headers[function_header])

		except KeyError:
			logging.info('\n\n###		INCORRECT HEADER 		###\n\nThe header: ' + str(function_header) + ' does not match any of the headers in Header List File (command -l). Please check the configuration file or Header list file:\n'+
				'\tHeader List File: ' + str(args.headers) + '\n' + '\tConfig File: ' + str(args.config) + '\n')
			sys.exit(1)


			# Comprobar que los headers del archivo headers se encuentran en los archivos de open y close #


		missing_open_values = [value for value in open_values if value not in df_open.columns]
		missing_open_values = pd.Series(missing_open_values).dropna().tolist()

		missing_close_values = [value for value in close_values if value not in df_close.columns]
		missing_close_values = pd.Series(missing_close_values).dropna().tolist()

		if not missing_open_values:
			logging.info('All headers from Headers List are in Open File!')

		else:
			logging.info("\n\n###		INCORRECT HEADER 		###\n\nThe following 'Open' values are not headers of the Open File: " + str(", ".join(missing_open_values))+'\nPlease check the names.')
			sys.exit(1)


		if not missing_close_values:
			logging.info('All headers from Headers List are in Close File!')

		else:
			logging.info("\n\n###		INCORRECT HEADER 		###\n\nThe following 'Close' values are not headers of the Close File: " + str(", ".join(missing_close_values))+'\nPlease check the names.')
			sys.exit(1)


			# Comprobar que las funciones llamadas en el archivo headers son funciones del codigo #

		missing_functions= set(df_headers.apply(check_function_existence, axis=1, function_column=function_header))
		missing_functions= [func for func in missing_functions if not pd.isna(func)]

		if missing_functions is not None and len(missing_functions)>0:
			logging.info(f"\n\n###		INCORRECT FUNCTION NAME 		###\n\nThe following functions are not exist in the code: " + ", ".join(map(str,[func for func in missing_functions if not pd.isna(func)]))+'\nPlease check the names.')
			sys.exit(1)

		else:
			logging.info('All functions from Headers List are functions in the code!')


		###  Read PD Mod List  ###


		if args.modlist:

			DM_close_list=readfile(Path(args.modlist))

			try:
				DM_close_list[NameDM_close_list]

			except KeyError:
				logging.info('\n\n###		INCORRECT HEADER 		###\n\nThe header: ' + str(NameDM_close_list) + ' does not match any of the headers in Proteome Discover File (command -mdl). Please check the configuration file or Proteome Discover File:\n'+
				'\tProteome Discoverer File: ' + str(args.modlist) + '\n' + '\tConfig File: ' + str(args.config) + '\n')
				sys.exit(1)


			try:
				DM_close_list[NameMod_close_list]

			except KeyError:
				logging.info('\n\n###		INCORRECT HEADER 		###\n\nThe header: ' + str(NameMod_close_list) + ' does not match any of the headers in Proteome Discover File (command -mdl). Please check the configuration file or Proteome Discover File:\n'+
				'\tProteome Discoverer File: ' + str(args.modlist) + '\n' + '\tConfig File: ' + str(args.config) + '\n')
				sys.exit(1)

			logging.info('Proteome List File read successfully!')


		### Change columns names and apply functions ###

		logging.info("Renaming the columns...")


		for i in range(len(df_headers)):

			if pd.isna(df_headers[function_header][i]) and  (df_headers[open_header][i] != df_headers[close_header][i]):

				if pd.notna(df_headers[close_header][i]):

					df_close=df_close.rename(columns={str(df_headers[close_header][i]) : str(df_headers[open_header][i])})
					logging.info('Rename column: "' + str(df_headers[close_header][i]) + '" from Close File as: "' + str(df_headers[open_header][i]) + '" of Open File.')

			else:

				function_name=df_headers[function_header][i]
				function=globals().get(function_name)

				signature=inspect.signature(function)
				funct_requiere_args=signature.parameters.keys()

				df=df_close
				column=df_headers[open_header][i]

				args_functions={
					'df':df,
					'column':column,
					'num_value': num_value,
					'xcorr': xcorr,
					'sequence': sequence,
					'charge' : charge,
					'annotated_close': annotated_close,
					'protein_close' : protein_close,
					'modifications_close' : modifications_close,
					'nterm_name_modifications_close' : nterm_name_modifications_close,
					'DM_close_list' : DM_close_list,
					'NameDM_close_list' : NameDM_close_list,
					'NameMod_close_list' : NameMod_close_list,
					'dm_error' : dm_error,
					'dm_fix_list' : dm_fix_list,
					'delta_mods' : delta_mods,
					'delta_peptide' : delta_peptide,
					'exp_neutral_mass' : exp_neutral_mass,
					'MH': MH
				}

				filtered_kwargs={key: value for key, value in args_functions.items() if key in funct_requiere_args}

				logging.info('Applying function "' + str(df_headers[function_header][i]) + ' to create ' + str(column) + ' in Close File.')
				logging.info('\tRequiere argument: ' + str(', '.join(filtered_kwargs.keys())))
				df_close=function(**filtered_kwargs)


		AnalysisMethod='AnalysisMethod'

		df_new=fusion_files(df_open, df_close, scan)

		if args.open:
			file_name=os.path.basename(Path(args.open))

		if args.patheq:
			file_name=os.path.basename(Path(open_ruth))

		file_name=os.path.splitext(file_name)[0]

		if args.output:
			df_new.to_csv(os.path.join(os.path.join(Path(args.output)), file_name + '_BeforeFilter_ClOpen.txt'), sep='\t', index=False)

		if args.open:
			df_new.to_csv(os.path.join(os.path.join(Path(args.open)), file_name + '_BeforeFilter_ClOpen.txt'), sep='\t', index=False)

		if args.patheq and not args.output:
			df_new.to_csv(os.path.join(os.path.join(Path(args.patheq)), file_name + '_BeforeFilter_ClOpen.txt'), sep='\t', index=False)

		df_new=filter_scans(df=df_new, filter_mod=filter_mod, AnalysisMethod=AnalysisMethod, xcorr_column=score, scan=scan, num=num, spscore=spscore)

		if args.output:
			df_new.to_csv(os.path.join(Path(args.output), file_name + "_ClOpen.txt"), sep='\t', index=False)

		if args.open:
			df_new.to_csv(os.path.join(os.path.join(Path(args.open)), file_name + '_ClOpen.txt'), sep='\t', index=False)

		if args.patheq and not args.output:
			df_new.to_csv(os.path.join(os.path.join(Path(args.patheq)), file_name + '_ClOpen.txt'), sep='\t', index=False)



if __name__ == '__main__':

    # parse arguments
    parser = argparse.ArgumentParser(
        description='ClOpen',
        epilog='''
        Fusion Close and Open Output

        ''')
        
    defaultconfig = os.path.join(os.getcwd(), "config/SHIFTS.ini")
    
    parser.add_argument('-op',  '--open', required=False, help='Input file from Open Search')
    parser.add_argument('-cl',  '--close', required=False, help='Input file from Close Search (Proteom Discoverer)')
    parser.add_argument('-l', '--headers', required=True, help='Header equivalation columns')
    parser.add_argument('-mdl', '--modlist', required=False, help='PD Modifications list')
    parser.add_argument('-o',  '--output', required=False, help='Output directory')
    parser.add_argument('-pep',  '--peptides', required=False, help='Peptide list to include from CloseSearch')
    parser.add_argument('-mod',  '--ptm', required=False, help='Modification list to include from CloseSearch')
    parser.add_argument('-pl',  '--patheq', required=False, help='Path to txt file with comparation ruths of Open and Close files')
    parser.add_argument('-c', '--config', default=defaultconfig, help='Path to custom config.ini file')

    args = parser.parse_args()
    
    # parse config
    config = configparser.ConfigParser(inline_comment_prefixes='#')
    config.read(args.config)

    # logging debug level. By default, info level
    log_file = outfile = os.path.join(os.getcwd(), 'ClOpen_log.txt')

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        handlers=[logging.FileHandler(log_file),
                                    logging.StreamHandler()])

    # start main function
    logging.info('start script: '+"{0}".format(" ".join([x for x in sys.argv])))
    main(args)
    logging.info('end script')