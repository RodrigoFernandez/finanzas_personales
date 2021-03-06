#!/usr/bin/python

# -*- coding: utf-8 -*-

import sys
import csv
import argparse
import time
import json


def getHoja(ruta):
	archivo = open(ruta)
	lector = csv.reader(archivo, delimiter='\t')
	return lector

def corregir_formato_monto(monto):
	return monto.replace('.', '').replace(',', '.')

def get_fondos(lector):
	rta = {}
	
	for fila in lector:
		if len(fila) > 0:
			if '/' in fila[0] and len(fila) == 6:
				indice = 5 if len(fila[4]) == 0 else 4
				rta[fila[1]] = ('u$s' if len(fila[4]) == 0 else '$',
								float(corregir_formato_monto(fila[3])),
								float(corregir_formato_monto(fila[indice])),
								float(corregir_formato_monto(fila[2])))
	return rta

def procesar(cvs_actual, cvs_anterior):
	actual = getHoja(cvs_actual)
	fondo_actual = get_fondos(actual)
	
	anterior = getHoja(cvs_anterior)
	fondo_previo = get_fondos(anterior)
	
	claves = sorted(fondo_actual.keys())
	
	rta = []
	for clave in claves:
		valor_previo = 0
		cuotapartes_anteriores = 0
		precio_previo = 0
		
		if clave in fondo_previo.keys():
			valor_previo = fondo_previo[clave][2]
			cuotapartes_anteriores = fondo_previo[clave][3]
			precio_previo = fondo_previo[clave][1]
		
		rta.append((clave,
					fondo_actual[clave][0],
					fondo_actual[clave][1],
					fondo_actual[clave][0],
					fondo_actual[clave][2],
					fondo_actual[clave][0],
					valor_previo,
					fondo_actual[clave][0],
					fondo_actual[clave][2]-valor_previo,
					fondo_actual[clave][3],
					cuotapartes_anteriores,
					precio_previo))
	
	en_pesos = []
	en_dolares = []
	for una_rta in rta:
		if una_rta[1] == '$':
			en_pesos.append(una_rta)
		else:
			en_dolares.append(una_rta)
	
	return en_pesos + en_dolares

def get_output_string(unProcesado):
	cuota_partes_previas = float(unProcesado[10])
	cuota_partes_actuales = float(unProcesado[9])
	
	separador_cuota_partes = '=='
	if cuota_partes_previas > cuota_partes_actuales:
		separador_cuota_partes = '--'
	elif cuota_partes_previas < cuota_partes_actuales:
		separador_cuota_partes = '++'
	
	return "{} ({} {} {}):\n {} {:f} [{:f}] => {} {:f} - {} {:f} = {} {:f}\n".format(unProcesado[0],
																		unProcesado[9],
																		separador_cuota_partes,
																		unProcesado[10],
																		unProcesado[1],
																		unProcesado[2],
																		unProcesado[11],
																		unProcesado[3],
																		unProcesado[4],
																		unProcesado[5],
																		unProcesado[6],
																		unProcesado[7],
																		unProcesado[8])

def fonto_a_dic(unProcesado):
	rta = {}
	rta['nombre'] = unProcesado[0]
	rta['moneda'] = unProcesado[1]
	rta['precio'] = unProcesado[2]
	rta['cuotapartes'] = unProcesado[9]
	rta['monto'] = unProcesado[4]
	rta['precio_previo'] = unProcesado[11]
	rta['cuotapartes_previas'] = unProcesado[10]
	rta['monto_previo'] = unProcesado[6]
	rta['diferencia'] = unProcesado[8]
	return rta

def get_fecha_generacion():
	return time.strftime('%Y_%m_%d')

def get_archivo_salida_con_formato(archivo_salida):
	partes = archivo_salida.split('.')
	rta = []
	
	if len(partes) > 1:
		partes.insert(1, get_fecha_generacion())
		return ".".join(partes)
	elif len(partes) == 1:
		return partes[0] + get_fecha_generacion()
	
	return archivo_salida

def get_parser():
	parser = argparse.ArgumentParser(description="Procesador de cvs de FCI de Santander Rio")
	parser.add_argument('actual', help='CVS de la ultima ronda')
	parser.add_argument('anterior', help='CVS de la anteultima ronda')
	parser.add_argument('--exportar', help='Vuelca el procesamiento en un archivo plano')
	parser.add_argument('--json', help='Vuelca el procesamiento en un archivo json')
	return parser

if __name__ == '__main__':
	args = get_parser().parse_args()
	
	procesados = procesar(args.actual, args.anterior)
	
	if args.exportar is not None:
		nombre_archivo_salida = get_archivo_salida_con_formato(args.exportar)
		
		archivo_salida = open(nombre_archivo_salida, 'w')
		
		for procesado in procesados:
			archivo_salida.write(get_output_string(procesado) + "\n")
		archivo_salida.close()
		
	elif args.json is not None:
		nombre_archivo_salida = get_archivo_salida_con_formato(args.json)
		archivo_salida = open(nombre_archivo_salida, 'w')
		aux = {}
		aux['fondos'] = []
		
		for procesado in procesados:
			aux['fondos'].append(fonto_a_dic(procesado))
		
		archivo_salida.write(json.dumps(aux, indent=4))
		archivo_salida.close()
		
	else:
		for procesado in procesados:
			print(get_output_string(procesado))
