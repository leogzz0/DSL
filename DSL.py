#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  30 13:30:56 2022

DSL que modela una onda sonora

@author: leogzz0
"""

import re
import numpy as np
#import matplotlib.pyplot as plt
import sounddevice as sd

time = 1000 # milisegundos
note_arr = [] # arreglo de notas
octave_arr = [] # arrelgo de octavas
duration_arr = [] # arreglo de duracion
token_arr = [] # arreglo de tokens
token = 0 
user_input_a = 0
flag = 0
line_error = 0
lex = True
sintaxis = False
conc = ""

# regex
comment = re.compile('#[\w\W]*') 
BAR_r = re.compile('#BAR') 
name = re.compile('[a-z][\w|\d]*\ *') 
particion = re.compile('\|') 
note_m = re.compile('[A|B|C|D|E|F|G](b*?|#*?)(-[1,2]|[0|1|2|3|4|5|6|7|8])[w|h|q|e|s|t|f]([\.]+|[t|3|5|7|9|33|tt]|\ )?')
note2_m = re.compile('[A|B|C|D|E|F|G](b*?|#*?)(-[1,2]|[0|1|2|3|4|5|6|7|8])[w|h|q|e|s|t|f]([\.]+|[5|7|9]|t{1,2}|3{1,2})?')
pause = ('R[w|h|q|e|s|t|f]([\.]+|[t|3|5|7|9])?')
pause2 = ('R[w|h|q|e|s|t|f]([\.]+|[t|3|5|7|9]|)?')
txt_file = re.compile('[\w\W]+\.(txt)')

# funcion con la formula de frecuencia implementada para obtener la frecuencia de una nota
def get_freq(note: int, octave: int) -> int:
    expo = (octave - 3) * 12 + (note - 10)
    return int(440 * ((2 ** (1/12)) ** expo))

# funcion con la formula de una onda acustica para obtener la onda de una nota
def get_wave(note: int, octave: int, duration: int):
    framerate = 44100
    freq = get_freq(note, octave)
    t = np.linspace(0, duration/time, int(framerate * duration/time))
    wave = np.sin(2 * np.pi * freq * t)
    sd.play(wave, framerate)
    sd.wait()
    
    #plt.plot(wave(:1000))
    #plt.show()

# funcion que identificara la nota y regresara un valor numerico
def get_letter(note):
    if note == "A":
        return 10 
    elif note == "B": 
        return 12 
    elif note == "C":
        return 1 
    elif note == "D":
        return 3 
    elif note == "E":
        return 5 
    elif note == "F":
        return 6 
    elif note == "G":
        return 8 
    return 0

# funcion que identificara una octava y regresara un valor numerico
def get_octave(octave):
    if octave == "0":
        return 0
    elif octave == "1":
        return 1
    elif octave == "2":
        return 2
    elif octave == "3":
        return 3
    elif octave == "4":
        return 4
    elif octave == "5":
        return 5
    elif octave == "6":
        return 6
    elif octave == "7":
        return 7
    elif octave == "8":
        return 8
    return 0

# funcion para identificar un sostenido o bemol y regresara un 1 o -1
def get_accidental(accidental):
    if accidental == "#":
        return 1
    elif accidental == "b":
        return -1
    return 0

# funcion que identificara lo que en MUTRAN es el tiempo de una nota 
def get_temp(value):
    if value == "w":
        return 1000
    elif value == "h":
        return 500
    elif value == "q":
        return 250 
    elif value == "e":
        return 125 
    elif value == "s":
        return 62.5 
    elif value == "t":
        return 33.3
    elif value == "f":
        return 16.6
    return 0

# funcion que identificara el modificador de tiempo y regresara un decimal
def get_modtemp(value_temp):
    if value_temp == "t":
        return 2/3
    elif value_temp == "3":
        return 2/3
    elif value_temp == "5":
        return 0.8
    elif value_temp == "7":
        return 6/7 
    elif value_temp == "9":
        return 8/9 
    elif value_temp == ".":
        return .25
    elif value_temp == "tt" or value_temp == "33":
        return 4/9
    return 1

"""
funcion que crea la nota tomando en cuenta la nota, la octava y la duracion
despues de obtener los valores los almacena en su respectivo arreglo
"""
def create_note(conc):
    get_note = 0
    octave_result = 0
    get_duration = 0
    dot = 1.25
    dot_mod = False
    
    # concatenacion de notas, octavas y duracion
    for i in range (0, len(conc)):
        get_note += get_letter(conc[i])
        get_note += get_accidental(conc[i])
        if conc[i] == "-":
            octave_result += get_octave(conc[i+1]) * -1
            i += 1
        else:
            if octave_result == 0:
                octave_result += get_octave(conc[i])
        
        get_duration += get_temp(conc[i])
        
        if conc[i] == ".":
            dot_mod = True
            dot += get_modtemp(conc[i])
        
        if dot_mod == True and len(conc) == i+1:
            get_duration *= dot
        else:
            if (conc[i] == '3' or conc[i] == 't') and len(conc) != i+1:
                get_duration *= get_modtemp(conc[i] + conc[i+1])
                i+1
            else:
                get_duration *= get_modtemp(conc[i])
                
    # concatenacion (note|octave|duration)
    note_arr.append(get_note)
    octave_arr.append(octave_result)
    duration_arr.append(get_duration)

# funcion para analisis de lexico y muestreo de error
def input_error(conc):
    print('\nError en la linea ' + line_error) 
    print('\nNo se reconoce ' + conc)
    return ''

def aceptor(case):
    return ""

# funcion que creara la nota
def ciclo(iteration, user_input):
    input_c = ""
    iteration += 1
    for i in range(iteration, len(user_input)):
        user_input_a = ord(user_input[i])
        if user_input_a != 13 and user_input[i] != " ":
            input_c += user_input[i]
        else:
            return input_c

# funcion para comentarios
def comments(iteration, user_input):
    input_c = ""
    iteration += 1
    for i in range(iteration, len(user_input)):
        user_input_a = ord(user_input[i])
        if user_input_a != 13:
            input_c += user_input[i]
        else: 
            return i, input_c
        
#funcion para la lectura del archivo txt
def read_txt(file):
    if not txt_file.fullmatch(file):
        # para que el usuario no tenga que escribir .txt
        file += '.txt'
        
    # extractor de informacion del archivo
    with open(file, 'r') as file_input:
        # variable para guardar la info
        file_info = file_input.readline()
        info = True
        list = []
        for line in file_input:
            if info == True:
                list.append(file_info)
                info =False
            list.append(line)
            
        list_data = ""
            
            # convertidor de info a string
        for element in list:
            new_element = element.strip().split(",")
            list_data += new_element[0] + chr(13)
            
        return list_data


# con la infromacion ya extraida empezamos con el analisis de sintaxis
# funcion que nos permitira avanzar en el arreglo de tokens
def move():
    global token
    global sintaxis
    global line_error
    if(len(token) > 0):
        token = token_arr.pop()
        if token == 5:
            line_error += 1
        else: 
            sintaxis = True
# comment
def music_sheet():
    if not sintaxis:
        if token == 0:
            move()
            first_note()
        elif token == 5:
            move()
            music_sheet()
        elif token == 4:
            move()
            comentario()
        else:
            print('Error en la linea ' + line_error + '. Se esperaba un nombre o comentario')
            exit()
            
# funcion que obtendra la primera nota
def first_note():
    if token == 1 and token == 1:
        move()
        nota()
    else:
        print('Error en la linea ' + line_error + '. Se esperaba una nota o descanso.')
        exit()
        
def nota():
    if token == 1 or token == 2:
        move()
        nota()
    elif token == 3 :
        move()
        limit()
    elif not token == 5:
        print('Error en la linea ' + line_error + '. Se esperaba una nota o descanso.')
        exit()

def limit():
    if token == 1 or token == 2:
        move()
        nota()
    elif not token == 5:
        print('Error en la linea ' + line_error + '. Se esperaba una nota o descanso.')
        exit()
        
def comentario():
    if not token == 5:
        print('Error en la linea ' + line_error + '. Se esperaba un enter para terminar un comentario.')
        exit()

def analisis():
    move()
    music_sheet()
    
    if sintaxis != True:
        analisis()
        
    
# Ejecucion 
file = input('\nEscribe el nombre del archivo para compilarlo: ')
print('\nCompilando archivo...')
user_input = read_txt(file)
print('\nIniciando el analisis de lexico...')

# detector de informacion
for i in range(0, len(user_input)):
    if i <= flag and i != 0:
        continue
    
    user_input_a = ord(user_input[i])
    
    if user_input_a != 13:
        conc += user_input[i]
    else: 
        token_arr.append(5)
        line_error += 1
        
        # detector de comentarios y palabras reservadas
    if conc == '#':
        comment_a = comments(i, user_input)
        flag = comment_a[0]
        conc += comment_a[1]
        
        if BAR_r.fullmatch(conc):
            token_arr.append(4)
            conc = aceptor('\nSe detecto palabra reservada #BAR')
            token_arr.append(5)
    
        if comment.fullmatch(conc):
            accepted_message = 'Se identifico comentario: ' + conc
            conc = aceptor(accepted_message)
            line_error += 1
            token_arr.append(4)
            token_arr.append(5)
            continue

        line_error += 1
        
        # detector de nota
        if note_m.fullmatch(conc):
            if user_input[i] == 's':
                time = 250
                
            conc += ciclo(i, user_input)
            
            if note2_m.fullmatch(conc):
                create_note(conc)
                accepted_message = 'Se detecto una nota musical: ' + conc
                conc = aceptor(accepted_message)
                token_arr.append(1)
                continue
            else:
                line_error += 1
                conc = input_error(conc)
                lex = False
                break
            
        if pause.fullmatch(conc):
            conc += ciclo(i, user_input)
            
            if pause2.fullmatch(conc):
                create_note(conc)
                accepted_message = 'Se detecto un descanso: ' + conc
                conc = aceptor(accepted_message)
                token.append(2)
                continue
            else: 
                line_error += 1
                conc = input_error(conc)
                lex = False
                break
            
        if particion.fullmatch(conc):
            conc = aceptor('\nlimitador de medida')
            token.append(3)
            continue
        
        if user_input_a == 13 or user_input[i] == '':
            if name.fullmatch(conc):
                accepted_message = 'Se detecto nombre: ' + conc
                conc = aceptor(accepted_message)
                token.append(0)
                continue
            
            if conc == " " or conc == "":
                conc = ""
            else:
                if user_input_a != 13:
                    line_error += 1
                conc = input_error(conc)
                lex = False
                break

if lex == True:
    print('\nAnalizando sintaxis...')
    
if sintaxis == True:
    print('\nReproduciendo cancion...')
    for i in range(0, len(note_arr)):
        get_wave(note_arr[i], octave_arr[i], duration_arr[i])
        
print('\nFin de analisis.')
    
    