# -*- coding: utf-8 -*-
"""
Created on Mon Jan  8 07:18:07 2024

@author: soler
"""

import numpy as np
import pandas as pd
import os

#-----------------------1--------------------------------------------------------


def loadData(file_paths):
    dfs = []
    column_names = ['Curso académico', 'Convocatoria', 'Estudiante', 'Calificación obtenida']

    for path in file_paths:
        file_name = os.path.basename(path)
        if file_name.startswith('Asignatura') and file_name.endswith('.csv'):
            df = pd.read_csv(path, names=column_names, skiprows=1, dtype={'Calificación obtenida': 'float32'})
            df['Asignatura'] = file_name[:-4]
            
            # Convertir la columna 'Convocatoria' a categórica
            df['Convocatoria'] = df['Convocatoria'].astype('category')

            dfs.append(df)

    combined_df = pd.concat(dfs, ignore_index=True)
    return combined_df

# Directorio donde se encuentran los archivos
directory = 'Data'
file_paths = [os.path.join(directory, file) for file in os.listdir(directory)]

df = loadData(file_paths)




#---------------------2----------------------------------------------------------

def calculate_counts_score(df):
    # Inicializar conteos
    suspensos = df[df['Calificación obtenida'] < 5.0].values.shape[0]
    aprobados = df[(df['Calificación obtenida'] >= 5.0) & (df['Calificación obtenida'] < 7.0)].values.shape[0]
    notables = df[(df['Calificación obtenida'] >= 7.0) & (df['Calificación obtenida'] < 9.0)].values.shape[0]
    sobresalientes = df[df['Calificación obtenida'] >= 9.0].values.shape[0]
    
    return suspensos, aprobados, notables, sobresalientes


def tableAll(df, a):
    df_asignatura = df[df['Asignatura'] == a]
    return calculate_counts_score(df_asignatura)

def tableYear(df, a, y):
    df_year = df[(df['Asignatura'] == a) & (df['Curso académico'] == y)]
    return calculate_counts_score(df_year)

def tableYearConv(df, a, y, c):
    df_year_conv = df[(df['Asignatura'] == a) & (df['Curso académico'] == y) & (df['Convocatoria'] == c)]
    return calculate_counts_score(df_year_conv)

def tableConv(df, a, c):
    df_conv = df[(df['Asignatura'] == a) & (df['Convocatoria'] == c)]
    return calculate_counts_score(df_conv)


tableAll(df, a = 'Asignatura01')
tableYear(df, a='Asignatura01', y='2010/2011')
tableYearConv(df, a='Asignatura01', y='2010/2011', c ='Febrero' )
tableConv(df, a='Asignatura01', c ='Febrero')


#------------------3------------------------------------------------------------

def meansExams(df,a):
    mean_exams = df[df['Asignatura']== a].groupby(['Estudiante']).size().mean()
    return np.round(mean_exams, decimals=2)

meansExams(df, a='Asignatura01')


#--------------4---------------------------------------------------------------
def allSubjects(df):
    df_aprobados = df[df['Calificación obtenida'] >= 5]
    aprobados_bool = df_aprobados.groupby(['Estudiante']).transform('size') >= 30
    return len(df_aprobados[aprobados_bool]['Estudiante'].drop_duplicates().tolist())

allSubjects(df)

def allSubjects(df):
    # Filtrar por aprobados
    df_aprobados= df[df['Calificación obtenida'] >= 5]
    
    # Agrupar por Estudiantes y Asignaturas (se cuenta el número de veces que se presenta a la asignatura aprobada)
    aprobados_grouped = df_aprobados.groupby(['Estudiante', 'Asignatura']).size().reset_index(name = 'Numero de veces peresentado')
    
    # Número de asignaturas total que hay en el departamento
    total_subjects = df['Asignatura'].nunique()
    
    # Reagrupar el DataFrame aprobados_grouped y contar el número de veces que aparece
    aprobados_grouped_subjects = aprobados_grouped.groupby('Estudiante').size().reset_index(name = 'Asignaturas aprobadas')
    
    # Filtrar por los alumnos que aparezcan tantas veces como asignaturas hay en el departamento
    students_aprobados_all = aprobados_grouped_subjects[aprobados_grouped_subjects['Asignaturas aprobadas'] == total_subjects]['Estudiante'].tolist()
    
    return students_aprobados_all

allSubjects(df)

#-----------5--------------------------------------------------------------
def allSubjectsFirstYear(df):
    # Agrupar por Estudiante y Asignatura contando el número de años académicos únicos para cada combinación de 'Estudiante' y 'Asignatura'
    years_per_subject = df.groupby(['Estudiante', 'Asignatura'])['Curso académico'].nunique()

    # Filtrar por el número de veces que se ha presentando una vez
    students_all_subjects_one_year = years_per_subject[years_per_subject == 1]

    # Crear un DataFrame de la Serie anterior y agrupor por Estudiante para contarlos 
    students_one_year_total = students_all_subjects_one_year.reset_index().groupby('Estudiante').size()
    
    # Número de asignaturas total que hay en el departamento
    total_subjects = df['Asignatura'].nunique()
    
    # Filtrar por los que coincida con el número total de asignaturas del departamento
    students_one_year_total_all = students_one_year_total[students_one_year_total == total_subjects].index.tolist()
    
    # Asegurarse de que hayan aprobado
    students_one_year_total_all_passed = allSubjects(df[df['Estudiante'].isin(students_one_year_total_all)])
    
    
    return students_one_year_total_all_passed
    
allSubjectsFirstYear(df)


#-------------6----------------------------------------------------------------
def academicRecord(df):
    # Ordenar el DataFrame por Estudiante, Asignatura y Curso académico
    df_sorted = df.sort_values(by=['Estudiante', 'Asignatura', 'Curso académico'])

    # Obtener el último examen realizado por cada estudiante en cada asignatura
    last_exam_grades = df_sorted.groupby(['Estudiante', 'Asignatura'])['Calificación obtenida'].last().reset_index()

    # Crear un nuevo DataFrame con los expedientes académicos
    academic_record = last_exam_grades.pivot(index='Estudiante', columns='Asignatura', values='Calificación obtenida')

    return academic_record

academicRecord(df)



