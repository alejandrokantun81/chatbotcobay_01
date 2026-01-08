import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import os

# ---------------------------------------------------------
# 1. BASE DE CONOCIMIENTO MAESTRA DE ALTIUS COBAY
# ---------------------------------------------------------
DATOS_RAG = [
    # =========================================================================
    # BLOQUE 1: REGLAMENTO INTERIOR DE TRABAJO
    # =========================================================================
    {
        "id": "rit_01",
        "metadata": { "sección": "Preámbulo y Cap I (Arts. 1-2)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Reglamento Interior de Trabajo del Colegio de Bachilleres del Estado de Yucatán (COBAY). Fundamentado en la Ley del COBAY. Cap I. Art 1: Observancia obligatoria. Art 2 (Definiciones): 'Adscripción' (lugar de servicio), 'Alumno', 'Centros EMSAD', 'Contrato Colectivo', 'Jornada de trabajo' (tiempo a disposición). Tipos de trabajador: 'Docente', 'Administrativo', 'Técnico', 'Manual'."
    },
    {
        "id": "rit_02",
        "metadata": { "sección": "Cap II: Relaciones Individuales (Arts. 3-5)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Cap II. Art 3: Contrato debe tener datos, duración, categoría, salario. Art 4: Terminación según art 53 LFT. Art 5 (Rescisión sin responsabilidad patrón): Certificados falsos, violencia, pedir dádivas, alterar documentos, embriaguez/drogas, portar armas."
    },
    {
        "id": "rit_03",
        "metadata": { "sección": "Cap II: Rescisión y Terminación (Arts. 5-8)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Continuación Art 5: Sustraer equipos, daños, acoso sexual, faltar >3 días en 30 días, negarse a evaluaciones, prisión. Art 6: Rescisión por trabajador (Art 51 LFT). Art 7: Renuncia con finiquito previo no adeudo. Pago en 30 días. Art 8: Constancias de no adeudo en 5 días."
    },
    {
        "id": "rit_04",
        "metadata": { "sección": "Cap III: Ingreso y IV: Nombramientos (Arts. 9-13)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Cap III. Art 9: Requisitos: Mexicano (o extranjero con permiso), aprobar evaluación. Docentes por Ley Servicio Profesional. Art 10: Documentos (CV, Título, Cédula, Antecedentes no penales, etc). Art 11: Prohibido 'meritorios'. Cap IV. Art 12: Nombramientos por escrito (Dir. Gral). Art 13: Servicio estricto al contrato."
    },
    {
        "id": "rit_05",
        "metadata": { "sección": "Cap V: Movimientos y VI: Jornada (Arts. 14-20)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Cap V. Altas, Movimientos, Promociones. Cap VI. Art 18-19: Jornadas: Completa (7h o 8h docentes), Tres cuartos (5-7h), Media (3.5-5h), Por horas clase. Art 20: Servicio fuera de adscripción cuenta desde el punto de concentración."
    },
    {
        "id": "rit_06",
        "metadata": { "sección": "Cap VI: Horarios y Registro (Arts. 21-26)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Art 21: Horarios según necesidades. Art 22: 30 min alimentos en continuo. Art 24-26: Registro obligatorio (lector, reloj, lista). Si falla, avisar a RH y usar libreta."
    },
    {
        "id": "rit_07",
        "metadata": { "sección": "Cap VI: Tolerancias y Retardos (Arts. 27-30)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Art 28 Tolerancias: Admin/Docente jornada: 20 min. Docente horas: 10 min (1ra hora). 2 tolerancias = 1 retardo. Art 29-30 Retardos: Admin (min 21-30), Docente horas (min 11-20). 3 retardos = 1 falta injustificada."
    },
    {
        "id": "rit_08",
        "metadata": { "sección": "Cap VI: Faltas y Descuentos (Arts. 31-33)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Art 31: Falta si llega después de tolerancia/retardo o no checa. Art 33 Faltas injustificadas (no pago): Sin permiso, 4 faltas en 30 días, salir antes, abandonar labores."
    },
    {
        "id": "rit_09",
        "metadata": { "sección": "Cap VI: Justificaciones y Estímulos (Arts. 34-36)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Art 34: Max 3 justificaciones/semestre. Art 35 Estímulo Puntualidad: Base/plaza con 90% asistencia. 7.5 días salario/semestre. Art 36 Días Económicos: 9 al año (base/plaza 1 año antigüedad). Solicitar 2 días antes. No usados se pagan en enero."
    },
    {
        "id": "rit_10",
        "metadata": { "sección": "Cap VII: Lugar y Permutas (Arts. 37-41)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Art 37: Cambio adscripción por reorganización o necesidad sin responsabilidad patrón. Art 39 Permuta: Intercambio mismo puesto/sueldo. Art 41: Esperar 2 años para nueva permuta."
    },
    {
        "id": "rit_11",
        "metadata": { "sección": "Cap VII: Mantenimiento y VIII: Pagos (Arts. 42-48)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Art 42: Limpieza y cuidado. Cap VIII. Art 45: Pago días 15 y último. Art 48: Deducciones solo por ley (Art 110 LFT)."
    },
    {
        "id": "rit_12",
        "metadata": { "sección": "Cap IX: Descansos y Vacaciones (Arts. 49-53)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Art 49: 5 días trabajo x 2 descanso. Art 51 Vacaciones: 2 periodos de 10 días hábiles (1 año antigüedad). Art 52 Prima: 12 días/semestre (Base), 6 días/semestre (Contrato)."
    },
    {
        "id": "rit_13",
        "metadata": { "sección": "Cap X: Aguinaldo y XI: Licencias (Arts. 54-55)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Art 54 Aguinaldo: 40 días (Base), 20 días (Contrato). Pago antes 20 dic. Cap XI Licencias Sin Goce: Hijos <1 año (6 m), Asuntos particulares (6 m, req 2 años ant.), Cargos elección."
    },
    {
        "id": "rit_14",
        "metadata": { "sección": "Cap XI: Licencias con Goce (Arts. 56-57)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Art 56 Con Goce (Base): Gravidez (90 días), Lactancia (2 reposos 30 min o reducción), Paternidad/Adopción (5 días). Art 57: Solicitud escrita a Dir Gral."
    },
    {
        "id": "rit_15",
        "metadata": { "sección": "Cap XII: Obligaciones (Art. 58)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Art 58: Cumplir normas, respeto alumnos/compañeros, no violencia, cuidar materiales, confidencialidad, no propaganda, actualizar datos."
    },
    {
        "id": "rit_16",
        "metadata": { "sección": "Cap XIII: Prohibiciones (Art. 59)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Art 59: Prohibido: Gratificaciones, faltar, abandonar, falsificar, uso personal bienes, embriaguez, armas, acoso sexual, alterar disciplina."
    },
    {
        "id": "rit_17",
        "metadata": { "sección": "Cap XIV: Obligaciones COBAY y XV: Seguridad (Arts. 60-64)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Art 60 COBAY: No discriminar, pagar oportuno. Cap XV: Seguridad e higiene responsabilidad COBAY. Trabajador debe avisar accidentes en 48h."
    },
    {
        "id": "rit_18",
        "metadata": { "sección": "Cap XV: Accidentes (Arts. 65-69)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Art 66: IMSS califica riesgos. Art 68: Justificación solo con incapacidad IMSS (48h). Art 69: Acta circunstanciada inmediata."
    },
    {
        "id": "rit_19",
        "metadata": { "sección": "Cap XVI: Capacitación y Ascensos (Arts. 70-77)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Art 70: Capacitación obligatoria (Comisión Mixta). Art 74: Ascensos por preparación, antigüedad y eficiencia."
    },
    {
        "id": "rit_20",
        "metadata": { "sección": "Cap XVII: Sanciones (Arts. 78-80)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Art 78: Extrañamiento, Suspensión (1-8 días), Rescisión. Art 79 Extrañamiento: Falta respeto, descuido, etc."
    },
    {
        "id": "rit_21",
        "metadata": { "sección": "Cap XVII: Suspensiones y Proceso (Arts. 81-86)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Art 81 Suspensión: Daños, reincidencia, etc. Art 82: Acta administrativa con audiencia. Prescribe en 30 días."
    },
    {
        "id": "rit_22",
        "metadata": { "sección": "Cap XVIII, XIX y Transitorios", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Art 88: Incompatibilidad de dos plazas. Vigencia desde 24 abril 2014."
    },

    # =========================================================================
    # BLOQUE 2: REGLAMENTO ACADÉMICO
    # =========================================================================
    {
        "id": "acad_01",
        "metadata": { "tipo_documento": "Reglamento Académico", "sección": "Título I: Generalidades y Objetivos (Arts. 1-3)" },
        "contenido": "REGLAMENTO ACADÉMICO COBAY. TÍTULO PRIMERO. Art 1: Cobay es organismo público descentralizado. Art 2: Imparte Bachillerato General escolarizado y EMSAD. Objetivos: Fortalecer capacidad intelectual, educación de calidad, competencias y TIC. Art 3: Facultades: Equivalencias, incorporar escuelas, promover cultura/deporte."
    },
    {
        "id": "acad_02",
        "metadata": { "tipo_documento": "Reglamento Académico", "sección": "Título I: Definiciones y Modalidades (Arts. 4-7)" },
        "contenido": "Art 4 Definiciones: Alumno (con matrícula vigente), Actividades paraescolares, Centro EMSAD, Personal Académico, Planteles. Art 6 Modalidades: I. Escolarizada. II. EMSAD. Duración máxima del bachillerato: 10 semestres. Art 7: Observancia obligatoria."
    },
    {
        "id": "acad_03",
        "metadata": { "tipo_documento": "Reglamento Académico", "sección": "Título I Cap II: Plan de Estudios (Arts. 8-12)" },
        "contenido": "Art 8 Plan de Estudios: Matemáticas, Ciencias Experimentales, Comunicación, Ciencias Sociales, Humanidades. Art 9 Componentes: Básico, Propedéutico (5to-6to sem) y Formación para Trabajo (3ro-6to sem). Art 11: Alumno elige capacitación en 1ra semana de 3er semestre."
    },
    {
        "id": "acad_04",
        "metadata": { "tipo_documento": "Reglamento Académico", "sección": "Título II Cap I-II: Categorías e Ingreso (Arts. 13-16)" },
        "contenido": "Art 13 Categorías: Regular (sin adeudos), Irregular (adeuda max 3 UAC), Repetidor (2da vez en mismo semestre, reprobó 4+). Art 14 Ingreso: Solicitud, Certificado secundaria, Acta nacimiento (max 17 años), Fotos, CURP, Examen."
    },
    {
        "id": "acad_05",
        "metadata": { "tipo_documento": "Reglamento Académico", "sección": "Título II Cap II: Inscripción (Arts. 17-25)" },
        "contenido": "Art 19 Inscripción 1er sem: Seleccionado en examen, entregar documentos y cubrir cuotas. Art 22 Extemporánea: Max 20 días hábiles. Art 24 Certificado secundaria limite 15 oct. Art 25: Prohibidos alumnos oyentes."
    },
    {
        "id": "acad_06",
        "metadata": { "tipo_documento": "Reglamento Académico", "sección": "Título II Cap II: Reinscripción y Cambios (Arts. 26-30)" },
        "contenido": "Art 26: Reinscripción semestral. Recursar mismo semestre solo una vez. Art 28 Cambio plantel: Una vez por ciclo, sujeto a cupo y autorización DCE. Art 30: Inscripción con estudios parciales requiere equivalencia."
    },
    {
        "id": "acad_07",
        "metadata": { "tipo_documento": "Reglamento Académico", "sección": "Título II Cap III: Equivalencia y Revalidación (Arts. 31-38)" },
        "contenido": "Art 32: Equivalencia por semestre completo si acredita todo (solo 2º-5º sem). Art 33: Dictamen por UAC si es incompleto. Art 36: Trámite ante DCE, validez un semestre."
    },
    {
        "id": "acad_08",
        "metadata": { "tipo_documento": "Reglamento Académico", "sección": "Título II Cap IV: Evaluación y Acreditación (Arts. 39-44)" },
        "contenido": "Art 40 Mínimo aprobatorio: 70 puntos. Art 41 Ordinaria: Dos parciales (70% formativa, 30% sumativa). Promedio parciales = 70% final. Examen ordinario = 30% final. Exenta ordinario con 100 en parciales. Art 42: Req 90% asistencia para derecho a evaluación."
    },
    {
        "id": "acad_09",
        "metadata": { "tipo_documento": "Reglamento Académico", "sección": "Título II Cap IV-V: Promoción y Recuperación (Arts. 45-51)" },
        "contenido": "Art 47 Promoción: No adeudar >3 UAC, no exceder 10 semestres. Art 49: Reprobar 4+ UAC tras recuperación = Repetidor (baja temporal). Art 51 Recuperación: al concluir ordinario (1-4 UAC reprobadas)."
    },
    {
        "id": "acad_10",
        "metadata": { "tipo_documento": "Reglamento Académico", "sección": "Título II Cap V: Evaluación Extraordinaria y Especial (Arts. 52-57)" },
        "contenido": "Art 53 Irregulares (max 3 UAC pendientes) van a Extraordinario (hasta 2 veces misma UAC). Art 54 Evaluación Especial: Última oportunidad si debe 1 sola UAC tras extra. Art 56: No repetir mismo semestre >1 vez."
    },
    {
        "id": "acad_11",
        "metadata": { "tipo_documento": "Reglamento Académico", "sección": "Título II Cap VI: Revisión Académica (Arts. 58-62)" },
        "contenido": "Art 59 Revisión calificación: Solicitud en 3 días hábiles. Art 62 Renuncia calificaciones: Para mejorar promedio (max 3 UAC). Req ser regular. Calificación de extraordinario es definitiva."
    },
    {
        "id": "acad_12",
        "metadata": { "tipo_documento": "Reglamento Académico", "sección": "Título II Cap VII: Bajas (Arts. 63-69)" },
        "contenido": "Art 63 Bajas: Temporal y Definitiva. Art 64 Temporal: Max 2 semestres. Causas: Solicitud, reprobar 4+, sanción. Art 67 Deserción: Inasistencia 15 días naturales."
    },
    {
        "id": "acad_13",
        "metadata": { "tipo_documento": "Reglamento Académico", "sección": "Título II Cap VII-VIII: Baja Definitiva y Certificación (Arts. 70-77)" },
        "contenido": "Art 71 Baja Definitiva: Solicitud, rebasar 10 semestres, documentos falsos, agotar oportunidades, faltas graves. Art 76 Certificado terminación: Acredita plan completo."
    },
    {
        "id": "acad_14",
        "metadata": { "tipo_documento": "Reglamento Académico", "sección": "Título II Cap IX: Derechos (Art. 78)" },
        "contenido": "Art 78 Derechos Alumnos: Educación calidad, trato digno, credencial, becas, seguro facultativo, ser representante, revisión calificaciones."
    },
    {
        "id": "acad_15",
        "metadata": { "tipo_documento": "Reglamento Académico", "sección": "Título II Cap IX: Obligaciones (Art. 79)" },
        "contenido": "Art 79 Obligaciones: Cumplir normas, enaltecer Cobay, uniforme, disciplina. Prohibido: Suspender labores, falsificar, violencia, drogas, armas, dañar bienes."
    },
    {
        "id": "acad_16",
        "metadata": { "tipo_documento": "Reglamento Académico", "sección": "Título II Cap IX y Transitorios: Sanciones (Arts. 80-82)" },
        "contenido": "Art 80 Sanciones: Amonestación, Suspensión (max 3 días), Baja temporal, Baja definitiva. Art 82: Baja definitiva por indisciplina grave requiere dictamen Dir. Académica. Vigencia desde 2017."
    },

    # =========================================================================
    # BLOQUE 3: CONTRATO COLECTIVO DE TRABAJO
    # =========================================================================
    {
        "id": "cct_01",
        "metadata": { "sección": "Aprobación y Votación 2024", "tipo_documento": "Contrato Colectivo de Trabajo" },
        "contenido": "CFCRL 30 abril 2024: Aprobación Convenio Revisión CCT-01/2020 entre STCBEY y COBAY. Consulta 20 marzo 2024: 1515 votos emitidos, 885 a favor (58%). Cumple Art 390 Ter LFT. Se ordena registro."
    },
    {
        "id": "cct_02",
        "metadata": { "sección": "Definiciones (I-XIII)", "tipo_documento": "Contrato Colectivo de Trabajo" },
        "contenido": "CCT-01/2020 COBAY-STCBEY. Definiciones: I. COBAY. II. STCBEY (Sindicato titular). IV. Trabajador Activo. VIII. Salario. IX. Salario Tabulado. X. Tabulador. XI. Adscripción. XIII. Representantes (Comité Ejecutivo)."
    },
    {
        "id": "cct_03",
        "metadata": { "sección": "Cap I: Disposiciones (Clausulas 1-5)", "tipo_documento": "Contrato Colectivo de Trabajo" },
        "contenido": "Cláusula 1: Regula condiciones base/plaza. Excluye confianza (salvo seg. social/aguinaldo). Cláusula 2: COBAY reconoce a STCBEY como titular del CCT. Cláusula 3: Leyes aplicables (CCT, Estatuto, LFT, Ley Trabajadores Estado Yucatán)."
    },
    {
        "id": "cct_04",
        "metadata": { "sección": "Cap II-III: Revisión (Clausulas 6-13)", "tipo_documento": "Contrato Colectivo de Trabajo" },
        "contenido": "Cláusula 6: Revisión salarial anual, integral cada 2 años. Cláusula 10: Ingreso sujeto a Ley Sistema Carrera Maestras. Cláusula 11: Preferencia mexicanos y sindicalizados. Cláusula 13: COBAY provee material de calidad."
    },
    {
        "id": "cct_05",
        "metadata": { "sección": "Cap IV-V: Derechos y Clasificación (Clausulas 14-17)", "tipo_documento": "Contrato Colectivo de Trabajo" },
        "contenido": "Cláusula 14: Derechos irrenunciables. Cláusula 16: Reubicación por reforma educativa o supresión de plaza (indemnización si no hay reubicación). Transferencias voluntarias o necesarias con 15 días aviso. Cláusula 17: Reclasificación no debe perjudicar salario."
    },
    {
        "id": "cct_06",
        "metadata": { "sección": "Cap VI-VII: Jornada y Salario (Clausulas 18-22)", "tipo_documento": "Contrato Colectivo de Trabajo" },
        "contenido": "Cláusula 18: Jornada Admin (35h/sem), Docente (40h, 30h, 20h o por hora). Vigilantes acumulada fin semana. Cláusula 19: 5 días labor x 2 descanso. Cláusula 20: Salario según tabulador autorizado presupuesto egresos."
    },
    {
        "id": "cct_07",
        "metadata": { "sección": "Cap VII: Pagos y Descuentos (Clausulas 23-25)", "tipo_documento": "Contrato Colectivo de Trabajo" },
        "contenido": "Cláusula 23: Pago días 15 y 30. Cláusula 25 Descuentos: Deudas COBAY/ISSTEY, Cuotas sindicales, Pensión alimenticia, Caja ahorro STCBEY."
    },
    {
        "id": "cct_08",
        "metadata": { "sección": "Cap VIII-IX: Vacaciones y Licencias (Clausulas 26-29)", "tipo_documento": "Contrato Colectivo de Trabajo" },
        "contenido": "Cláusula 26: 2 periodos vacacionales 10 días hábiles. Manuales antes del periodo escolar. Cláusula 28: Licencia sin goce (tras 2 años antigüedad): Hasta 6 meses renovables. Reincorporación misma condición."
    },
    {
        "id": "cct_09",
        "metadata": { "sección": "Cap IX: Gravidez y Cargos (Clausulas 30-32)", "tipo_documento": "Contrato Colectivo de Trabajo" },
        "contenido": "Cláusula 32 Gravidez: 120 días sueldo íntegro. Discapacidad hijo (+8 sem). Adopción (8 sem). Lactancia/Complicaciones (+10 días). Prórroga si coincide con vacaciones."
    },
    {
        "id": "cct_10",
        "metadata": { "sección": "Cap X: Comisiones Mixtas (Clausulas 33-39)", "tipo_documento": "Contrato Colectivo de Trabajo" },
        "contenido": "Cláusula 33 Comisiones Mixtas (STCBEY-COBAY): Seguridad e Higiene, Capacitación, Antigüedades, Reglamento Interior."
    },
    {
        "id": "cct_11",
        "metadata": { "sección": "Cap XI-XII: Servicios Médicos y Sanciones (Clausulas 40-44)", "tipo_documento": "Contrato Colectivo de Trabajo" },
        "contenido": "Cláusula 40: Servicio Médico ISSTEY/IMSS (cubre familia). Cláusula 41: Justificantes IMSS. Cláusula 44 Sanciones: Extrañamiento, Acta, Suspensión (max 8 días), Rescisión."
    },
    {
        "id": "cct_12",
        "metadata": { "sección": "Cap XIII-XIV: Obligaciones COBAY (Clausulas 45-50)", "tipo_documento": "Contrato Colectivo de Trabajo" },
        "contenido": "Cláusula 45: Preferencia propuesta STCBEY para vacantes. Cláusula 48: Entrega CCT. Cláusula 50: Trato con representantes STCBEY."
    },
    {
        "id": "cct_13",
        "metadata": { "sección": "Prestaciones Económicas I (Clausulas 51-58)", "tipo_documento": "Contrato Colectivo de Trabajo" },
        "contenido": "Cláusula 52 Despensa: Plaza $1,380.50 ($2,761 dic), Base $34.50/hr ($69 dic). Cláusula 53 Aguinaldo: 40 días tabulado. Cláusula 54 Vale Pavo 8kg. Cláusula 55-56 Apoyo convivios ($150). Cláusula 57 Prima Vacacional: 12 días/periodo. Cláusula 58 Ajuste Calendario: 5 días salario en dic."
    },
    {
        "id": "cct_14",
        "metadata": { "sección": "Prestaciones Económicas II (Clausulas 59-63)", "tipo_documento": "Contrato Colectivo de Trabajo" },
        "contenido": "Cláusula 59 Días Económicos: 9/año. No usados se pagan enero (12 días). Cláusula 60 Puntualidad: 7.5 días/semestre (90% asistencia). Cláusula 61 Prima Antigüedad: 1.5% salario/año desde 15 años. Cláusula 62 Estímulo Antigüedad: $2,000 (10, 20, 30 años). Cláusula 63 Eficiencia (Tabla)."
    },
    {
        "id": "cct_15",
        "metadata": { "sección": "Ayudas Sociales (Clausulas 64-69)", "tipo_documento": "Contrato Colectivo de Trabajo" },
        "contenido": "Cláusula 64 Titulación: $5,000. Cláusula 65 Útiles: $300-$500/hijo. Cláusula 66-67 Lentes/Ortopédicos: $2,500/$2,150 anual. Cláusula 68 Seguro Vida: 40 meses. Cláusula 69 Defunción: $17,000."
    },
    {
        "id": "cct_16",
        "metadata": { "sección": "Días y Apoyos Docentes (Clausulas 70-76)", "tipo_documento": "Contrato Colectivo de Trabajo" },
        "contenido": "Cláusula 70: Pago extra 24 abril y 15 mayo. Cláusula 72 Material Didáctico. Cláusula 73 Productividad (18.53%). Cláusula 74 Superación Académica (titulados). Cláusula 76 Libros: $600 anual."
    },
    {
        "id": "cct_17",
        "metadata": { "sección": "Apoyos Familiares (Clausulas 77-90)", "tipo_documento": "Contrato Colectivo de Trabajo" },
        "contenido": "Cláusula 77 Exención inscripción hijos. Cláusula 78 Canastilla $1,500. Cláusula 79 Guardería $588/mes. Cláusula 80 Prima dominical. Cláusula 88 Paternidad: 5 días. Cláusula 89 Enfermedad familiar: 6 días/año. Cláusula 90 Licencia cuidados <1 año (6-12 meses sin goce)."
    },
    {
        "id": "cct_18",
        "metadata": { "sección": "Días Personales y Tabulador (Clausulas 91-Final)", "tipo_documento": "Contrato Colectivo de Trabajo" },
        "contenido": "Cláusula 91 Uniformes. Cláusula 92-95 Descansos: Cumpleaños, Día Madre/Padre, Luto (3 días directo, 2 indirecto). Anexo Tabulador: Técnico ($7.5k-11k), Vigilante ($8.4k), Profesor CB I ($435/hr)."
    },

    # =========================================================================
    # BLOQUE 4: DIRECTORIO INSTITUCIONAL
    # =========================================================================
    {
        "id": "dir_01",
        "metadata": { "sección": "Dirección General y Staff", "tipo_documento": "Directorio Institucional" },
        "contenido": """
        DIRECTORIO DE AUTORIDADES DEL COBAY:
        
        1. DIRECCIÓN GENERAL
           - Titular: Mtro. Didier Manuel De Jesús Barrera Novelo (Director General).
           - Dirección: Calle 34 núm. 420-B x 35, Col. López Mateos, Mérida.
           - Teléfono: (999) 611 8690 Ext. 28051 y 28052.
        
        2. UNIDAD DE VINCULACIÓN
           - Titular: Ing. Manuel Alberto Bonilla Campo (Jefe de Unidad).
           - Teléfono: Ext. 28091.
        
        3. COMUNICACIÓN SOCIAL
           - Titular: Lic. Martín Rodrigo Kauil Conde (Jefe de Departamento).
           - Teléfono: Ext. 28007.
        
        4. RELACIONES PÚBLICAS
           - Titular: Lic. Oswaldo Cardeña Medina (Jefe de Departamento).
           - Teléfono: Ext. 28007.
        
        5. DIRECCIÓN JURÍDICA
           - Titular: Mtro. David Alejandro Patrón Bianchi (Director Jurídico).
           - Teléfono: Ext. 28044 y 28045.
           - Asuntos Contenciosos: Lic. Alfonso Arturo Orozco Araiza (Jefe Depto). Tel: Ext. 608 / Cel: 9991678554.
           - Asuntos Mixtos: Lic. Julio César Rodríguez (Jefe Depto). Tel: Ext. 605 / Cel: 9991678554.
           - Unidad de Transparencia: Lic. Gabriela Margarita Montejo Diaz. Tel: Ext. 605 / Cel: 9991678554.
        """
    },
    {
        "id": "dir_02",
        "metadata": { "sección": "Dirección Administrativa y Planeación", "tipo_documento": "Directorio Institucional" },
        "contenido": """
        6. DIRECCIÓN ADMINISTRATIVA
           - Titular: C.P. Martha Cecilia Dorantes Caballero (Directora Administrativa).
           - Teléfono: Ext. 608 / Cel: 9991678554.
           - Subdirección de Finanzas: C.P. Daniel Gallardo Colli. Tel: Ext. 606 / Cel: 9991678554.
           - Recursos Humanos: Lic. Lizbeth Beatríz García Pérez. Tel: Ext. 28015.
           - Recursos Materiales: Mtra. Maira Alejandra Alcocer Pulido. Tel: (999) 611 8690 / Cel: 9991678553.
           - Informática: Lic. Leydi Del Socorro Cobá. Tel: Ext. 28022.
           - Servicios Generales: Mtro. José Carlos Brito Díaz. Tel: (999) 611 8690 / Cel: 9999254377.
           - Unidad de Control y Evaluación (Interna): Mtro. Leobardo Medina Xix. Tel: Ext. 602 / Cel: 9991678554.
           - Supervisión Zona 01: Lic. Javier Arcangel May Meléndez (Ext. 28046).
           - Supervisión Zona (General): Lic. José Dolores Chay Cauich (Ext. 28046).
           - Supervisión Zona 03: Mtro. Luis Enrique Alamilla Herrera (Ext. 28046).

        7. DIRECCIÓN TÉCNICA Y PLANEACIÓN
           - Titular: Mtra. Mariela Elizabeth Mena Godoy.
           - Teléfono: Ext. 28040.
           - Presupuesto: C.P. Cristina Isabel Sánchez López. Tel: Ext. 606 / Cel: 9991678554.
           - Estadísticas: Ing. Beatriz De Fátima Arceo Medina. Tel: Ext. 606 / Cel: 9991678554.
           - Estudios y Proyectos: Arqto. Antonio Morales Balderas. Tel: Ext. 28091.
        """
    },
    {
        "id": "dir_03",
        "metadata": { "sección": "Dirección Académica", "tipo_documento": "Directorio Institucional" },
        "contenido": """
        8. DIRECCIÓN ACADÉMICA
           - Director: Dr. Cristian Miguel Sosa Molina.
           - Teléfono: Ext. 28025 y 28026.
           
           - Subdirector Académico: Dr. Manuel Alejandro Kantún Ramírez.
           - Teléfono: Ext. 28026.
           
           - Control Escolar: Lic. Ileana Del Carmen Rodríguez Quintal. Tel: Ext. 28036.
           - Actualización y Formación Docente: Lic. Tania Beatríz Figueroa Chan. Tel: Ext. 28028.
           - Servicios Académicos: Mtro. Marco Antonio Turriza Chan. Tel: Ext. 28027.
           - Orientación, Laboratorios y Bibliotecas: Mtro. Javier Concha Bastarrachea. Tel: Ext. 28031.
           - Actividades Cívicas, Culturales y Deportivas: Lic. Jorge Abel Jiménez Aguilar. Tel: Ext. 28034.
           - Coordinación EMSAD: Laet. Minelia Soberanis Herrera. Tel: Ext. 28039.
        """
    },

    # =========================================================================
    # BLOQUE 5: CALENDARIO ESCOLAR
    # =========================================================================
    {
        "id": "cal_01",
        "metadata": { "sección": "Febrero - Marzo 2026", "tipo_documento": "Calendario Escolar" },
        "contenido": """
        FEBRERO 2026:
        - 02/Feb: Suspensión de Labores (Inhábil).
        - 03/Feb: Inicio de semestre 2026-A (Administrativo).
        - 04/Feb: Reunión de Trabajo Colegiado (2 días).
        - 06/Feb: Inicio de clases del semestre (Académico).
        - Fines de semana: Eval. Extraordinarios 1º, 3º, 5º Sem.

        MARZO 2026:
        - 02/Mar: 1er Examen Parcial de 6º Semestre.
        - 09/Mar: 1er Examen Parcial de 2º y 4º Semestre.
        - 16/Mar: Suspensión de Labores (Inhábil).
        - 17/Mar: Eval. Especial de 1º, 3º y 5º semestre.
        - 23/Mar: Eval. Cap. Administración (4º y 6º Sem).
        - 24/Mar: Eval. Cap. Interv. Educ. Oblig (4º y 6º Sem).
        - 25/Mar: Eval Cap TIC'S (4º y 6º Sem).
        - 27/Mar: Entrega de Boletas 1er parcial.
        - 30/Mar: Inicio Período de Vacaciones.
        - Fines de semana: Eval. Extraordinarios 1º, 3º, 5º Sem.
        """
    },
    {
        "id": "cal_02",
        "metadata": { "sección": "Abril - Mayo 2026", "tipo_documento": "Calendario Escolar" },
        "contenido": """
        ABRIL 2026:
        - 01-10/Abr: Periodo de Vacaciones.
        - 13/Abr: Eval. Extraord Capacitaciones (4º y 6º Sem).
        - 20/Abr: Eval. Cap. Higiene y Salud Com. (4º y 6° sem).
        - 21/Abr: Eval Cap. Turismo (4º y 6º Sem).
        - 27/Abr: Eval. Especial de 1º, 3º y 5º semestre.
        - 28/Abr: 2do. Examen Parcial de 6º Sem.
        - 29/Abr: Eval. Extraord Capacitaciones (4º y 6º Sem).
        - 30/Abr: 2do. Examen Parcial de 2º y 4º Sem.
        - Fines de semana: Eval. Extraordinarios 1º, 3º, 5º Sem.

        MAYO 2026:
        - 01/May: Suspensión de Labores (Inhábil).
        - 04/May: Continuación 2do. Examen Parcial 6º Sem.
        - 11/May: Continuación 2do. Examen Parcial 2º y 4º Sem.
        - 18/May: Eval. Especial 1º, 3º y 5º semestre.
        - 22/May: Entrega de Boletas 2º parcial (6º sem).
        - 25/May: Fecha límite para solicitar Certificados al DCE.
        - 29/May: Entrega de Boletas 2º parcial (2º y 4º sem).
        - Fines de semana: Eval. Extraordinarios 1º, 3º, 5º Sem.
        """
    },
    {
        "id": "cal_03",
        "metadata": { "sección": "Junio - Agosto 2026", "tipo_documento": "Calendario Escolar" },
        "contenido": """
        JUNIO 2026:
        - 01/Jun: Eval todas las Capacitaciones 6º Sem.
        - 02/Jun: 3er. Examen Parcial de 6º sem.
        - 03/Jun: Eval todas las Capacitaciones 4º Sem.
        - 04/Jun: Reinscripción Repetidores 3º y 5º Sem.
        - 05/Jun: Eval. Extraord Capacitaciones 6º Sem.
        - 06/Jun: 3er. Examen Parcial 2º y 4º Sem.
        - 07/Jun: Solicitud Certificados Egresión (FC).
        - 08/Jun: Periodo Recuperación 6º semestre.
        - 09/Jun: Eval Extraord Capacitaciones 4º Sem.
        - 10/Jun: Solicitud Certificados Egresión (Ext).
        - 11/Jun: Entrega Boletas 3er parcial (2º y 4º sem).
        - 12/Jun: Reinscripciones 3º y 5º semestre.
        - 13/Jun: Período Recuperación 2º y 4º Sem.

        JULIO 2026:
        - 01/Jul: Ceremonia de Entrega de Certificados.
        - 02/Jul: Trámites de Equivalencia, Traslados.
        - 03/Jul: Inscripciones de Nuevo Ingreso.
        - 04/Jul: Entrega Boletas Recuperación.
        - 05/Jul: Fin de Semestre 2026-A.
        - 06/Jul: Inicio Receso de Clases.

        AGOSTO 2026:
        - 01/Ago: Receso Dirección General.
        - 02/Ago: Receso Planteles.
        - 03/Ago: Inicio Ciclo Escolar 2026-2027 (26-B).
        - 04/Ago: Trámites Equivalencia/Traslados.
        - 05/Ago: Reinscripciones 3º y 5º semestre.
        - 06/Ago: Reinscripción Repetidores 1º Sem.
        """
    },

    # =========================================================================
    # BLOQUE 6: PLANTELES Y MATRÍCULA 2025-B
    # =========================================================================
    {
        "id": "mat_01",
        "metadata": { "sección": "Estadísticas Generales y Planteles 1-30", "tipo_documento": "Matrícula 2025-B" },
        "contenido": """
        RESUMEN ESTADÍSTICO 2025-B:
        - Total Planteles: 72
        - Matrícula Global: 27,704 alumnos.
        - Desglose: 1º Semestre (10,575), 3º Semestre (8,743), 5º Semestre (8,386).

        DETALLE PLANTELES (ID 1-30):
        1. ABALA: 103 alumnos (1º:38, 3º:34, 5º:31).
        2. ACANCEH: 435 alumnos (1º:173, 3º:130, 5º:132).
        3. AKIL: 337 alumnos (1º:150, 3º:85, 5º:102).
        4. BACA: 365 alumnos (1º:135, 3º:111, 5º:119).
        6. BUCTZOTZ: 262 alumnos (1º:94, 3º:65, 5º:103).
        5. CACALCHEN: 270 alumnos (1º:103, 3º:86, 5º:81).
        7. CALOTMUL: 109 alumnos (1º:46, 3º:32, 5º:31).
        8. CAUCEL: 661 alumnos (1º:233, 3º:213, 5º:215).
        9. CENOTILLO: 115 alumnos (1º:43, 3º:38, 5º:34).
        10. CELESTUN: 208 alumnos (1º:74, 3º:61, 5º:73).
        11. CENOTILLO (2): 115 alumnos (1º:43, 3º:38, 5º:34).
        12. CHACSINKIN: 120 alumnos (1º:43, 3º:39, 5º:38).
        13. CHANKOM: 114 alumnos (1º:42, 3º:34, 5º:38).
        14. CHAPAB: 113 alumnos (1º:48, 3º:32, 5º:33).
        15. CHEMAX: 721 alumnos (1º:285, 3º:232, 5º:204).
        16. CHENKU: 1424 alumnos (1º:480, 3º:465, 5º:479).
        17. CHICHIMILA: 249 alumnos (1º:107, 3º:79, 5º:63).
        18. CHICXULUB PUEBLO: 161 alumnos (1º:74, 3º:46, 5º:41).
        19. CHOCHOLA: 163 alumnos (1º:63, 3º:45, 5º:55).
        20. CHUMAYEL: 144 alumnos (1º:57, 3º:38, 5º:49).
        21. DZAN: 187 alumnos (1º:73, 3º:58, 5º:56).
        22. DZEMUL: 127 alumnos (1º:46, 3º:33, 5º:48).
        23. DZIDZANTUN: 260 alumnos (1º:93, 3º:82, 5º:85).
        24. DZILAM GONZALEZ: 208 alumnos (1º:76, 3º:65, 5º:67).
        25. DZITAS: 154 alumnos (1º:65, 3º:47, 5º:42).
        26. ESPITA: 451 alumnos (1º:185, 3º:145, 5º:121).
        27. HALACHO: 477 alumnos (1º:182, 3º:156, 5º:139).
        28. HOCTUN: 248 alumnos (1º:98, 3º:77, 5º:73).
        29. HOMUN: 294 alumnos (1º:113, 3º:99, 5º:82).
        30. HUHI: 191 alumnos (1º:73, 3º:55, 5º:63).
        """
    },
    {
        "id": "mat_02",
        "metadata": { "sección": "Planteles 31-60", "tipo_documento": "Matrícula 2025-B" },
        "contenido": """
        DETALLE PLANTELES (ID 31-60):
        31. HUNUCMA: 696 alumnos (1º:293, 3º:218, 5º:185).
        32. IXIL: 129 alumnos (1º:55, 3º:40, 5º:34).
        33. KANNASIN: 1016 alumnos (1º:456, 3º:290, 5º:270).
        34. KANTUNIL: 149 alumnos (1º:52, 3º:54, 5º:43).
        35. KINCHIL: 267 alumnos (1º:110, 3º:80, 5º:77).
        36. LOBAIN: 576 alumnos (1º:186, 3º:191, 5º:199).
        37. MANI: 179 alumnos (1º:61, 3º:57, 5º:61).
        38. MAXCANU: 452 alumnos (1º:169, 3º:139, 5º:144).
        39. MAYAPAN: 126 alumnos (1º:50, 3º:39, 5º:37).
        40. MERIDA-NTE: 1120 alumnos (1º:348, 3º:366, 5º:406).
        41. MOCOCHA: 107 alumnos (1º:45, 3º:33, 5º:29).
        42. MOTUL: 519 alumnos (1º:195, 3º:178, 5º:146).
        43. MUNA: 398 alumnos (1º:146, 3º:126, 5º:126).
        44. OPICHEN: 233 alumnos (1º:91, 3º:68, 5º:74).
        45. OXKUTZCAB: 552 alumnos (1º:218, 3º:176, 5º:158).
        46. PANABA: 226 alumnos (1º:102, 3º:69, 5º:55).
        47. PETO: 569 alumnos (1º:227, 3º:173, 5º:169).
        48. PROGRESO: 769 alumnos (1º:305, 3º:240, 5º:224).
        49. SAMAHIL: 154 alumnos (1º:62, 3º:43, 5º:49).
        50. SANTA ELENA: 151 alumnos (1º:55, 3º:53, 5º:43).
        51. SEYE: 329 alumnos (1º:126, 3º:110, 5º:93).
        52. SINANCHE: 111 alumnos (1º:42, 3º:38, 5º:31).
        53. SOTUTA: 248 alumnos (1º:101, 3º:74, 5º:73).
        54. SUCILA: 157 alumnos (1º:61, 3º:51, 5º:45).
        55. TAHDZIU: 169 alumnos (1º:73, 3º:52, 5º:44).
        56. TEABO: 248 alumnos (1º:97, 3º:75, 5º:76).
        57. TECAX: 394 alumnos (1º:163, 3º:123, 5º:108).
        58. TECOH: 330 alumnos (1º:141, 3º:105, 5º:84).
        59. TEKOM: 150 alumnos (1º:58, 3º:41, 5º:51).
        60. TELCHAC PUEBLO: 127 alumnos (1º:53, 3º:33, 5º:41).
        """
    },
    {
        "id": "mat_03",
        "metadata": { "sección": "Planteles 61-78 y Segundo Grupo", "tipo_documento": "Matrícula 2025-B" },
        "contenido": """
        DETALLE PLANTELES (ID 61-78):
        61. TEMAX: 233 alumnos (1º:85, 3º:77, 5º:71).
        62. TEPAKAM: 83 alumnos (1º:31, 3º:25, 5º:27).
        63. TICOPO: 213 alumnos (1º:87, 3º:68, 5º:58).
        64. TICUL: 800 alumnos (1º:308, 3º:249, 5º:243).
        65. TIMUCUY: 157 alumnos (1º:71, 3º:42, 5º:44).
        66. TIXMEHUAC: 162 alumnos (1º:54, 3º:58, 5º:50).
        67. TIZIMIN: 681 alumnos (1º:276, 3º:223, 5º:182).
        68. TUNKAS: 120 alumnos (1º:52, 3º:33, 5º:35).
        69. TZUCACAB: 391 alumnos (1º:158, 3º:120, 5º:113).
        70. UAYMA: 158 alumnos (1º:57, 3º:50, 5º:51).
        71. UCU: 157 alumnos (1º:58, 3º:58, 5º:41).
        72. UMAN: 741 alumnos (1º:298, 3º:221, 5º:222).
        73. VALLADOLID: 851 alumnos (1º:286, 3º:287, 5º:278).
        74. XOCCHEL: 193 alumnos (1º:74, 3º:61, 5º:58).
        75. X-MATKUIL: 1702 alumnos (1º:580, 3º:535, 5º:587).
        76. YAXCABÁ: 202 alumnos (1º:82, 3º:63, 5º:57).
        77. YAXKUKUL: 168 alumnos (1º:67, 3º:52, 5º:49).
        78. YOBAIN: 93 alumnos (1º:35, 3º:29, 5º:29).

        SEGUNDO GRUPO DE PLANTELES/CENTROS:
        1. BECAL: 143 alumnos (1º:66, 3º:41, 5º:36).
        2. CELESTUN: 126 alumnos (1º:49, 3º:44, 5º:33).
        3. CHIKINDZONOT: 150 alumnos (1º:63, 3º:45, 5º:42).
        4. DZITYA: 124 alumnos (1º:48, 3º:41, 5º:35).
        5. DZONOT CARRETERO: 85 alumnos (1º:29, 3º:24, 5º:32).
        6. KAUA: 166 alumnos (1º:69, 3º:51, 5º:46).
        7. PISTE: 253 alumnos (1º:85, 3º:80, 5º:88).
        8. POPOLNAH: 93 alumnos (1º:45, 3º:32, 5º:16).
        9. TIXCACALCUPUL: 176 alumnos (1º:63, 3º:58, 5º:55).
        10. TIXCANCAL: 125 alumnos (1º:44, 3º:35, 5º:46).
        11. XCAN: 203 alumnos (1º:75, 3º:67, 5º:61).
        """
    },

    # =========================================================================
    # BLOQUE 7: INFRAESTRUCTURA (Inventario de Salones y Turnos)
    # =========================================================================
    {
        "id": "infra_01",
        "metadata": { "sección": "Inventario de Salones y Turnos", "tipo_documento": "Infraestructura Educativa" },
        "contenido": """
        INVENTARIO DE SALONES Y DISTRIBUCIÓN DE TURNOS POR PLANTEL:

        1. Abalá: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        2. Acanceh: 12 Salones. 1º(Matutino-Discontinuo), 3º(Matutino-Discontinuo/Vespertino-Discontinuo), 5º(Vespertino-Discontinuo).
        3. Akil: 9 Salones. 1º(Matutino), 3º(Matutino/Vespertino), 5º(Vespertino).
        4. Baca: 12 Salones. 1º(Matutino), 3º(Matutino/Vespertino), 5º(Vespertino).
        5. Becanchen EMSAD: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        6. Buctzotz: 8 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        7. Cacalchén: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        8. Calotmul: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        9. Caucel: 15 Salones. 1º(Matutino/Vespertino), 3º(Matutino/Vespertino), 5º(Matutino/Vespertino).
        10. Celestún EMSAD: 6 Salones. 1º(Matutino/Vespertino), 3º(Matutino/Vespertino), 5º(Matutino/Vespertino).
        11. Cenotillo: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        12. Cepeda: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        13. Chacsinkin EMSAD: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        14. Chankom EMSAD: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        15. Chemax: 16 Salones. 1º(Matutino), 3º(Vespertino), 5º(Matutino/Vespertino).
        16. Chenkú: 28 Salones. 1º(Matutino/Vespertino), 3º(Matutino/Vespertino), 5º(Matutino/Vespertino).
        17. Chichimilá: 9 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        18. Chicxulub Pueblo: 9 Salones. 1º(Matutino/Vespertino), 3º(Matutino), 5º(Vespertino).
        19. Chikindzonot: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        20. Cholul: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        21. Colonia Yucatán: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        22. Cuzamá: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        23. Dzemul: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        24. Dzidzantún: 9 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        25. Dzilam Gonzalez: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        26. Dzitás: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        27. Dzonot Carretero EMSAD: 6 Salones. 1º(Vespertino), 3º(Vespertino), 5º(Vespertino).
        28. Halachó: 12 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        29. Homún: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        30. Hunucmá: 15 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        31. Kanasín: 23 Salones. 1º(Matutino/Vespertino), 3º(Matutino/Vespertino), 5º(Matutino/Vespertino).
        32. Kantunil: 4 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        33. Kaua EMSAD: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        34. Kimbilá: 9 Salones. 1º(Matutino), 3º(Matutino/Vespertino), 5º(Vespertino).
        35. Kinchil: 9 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        36. Komchén: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        37. Muna: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        38. Opichén: 5 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        39. Peto: 18 Salones. 1º(Matutino), 3º(Matutino/Vespertino), 5º(Vespertino).
        40. Pisté EMSAD: 9 Salones. 1º(Vespertino), 3º(Matutino/Vespertino), 5º(Matutino).
        41. Popolnah EMSAD: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        42. Progreso: 30 Salones. 1º(Matutino/Vespertino), 3º(Matutino/Vespertino), 5º(Matutino/Vespertino).
        43. Rio Lagartos: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        44. Sacalum: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        45. San José Tzal: 6 Salones. 1º(Mat-Disc/Vesp-Disc), 3º(Mat-Disc/Vesp-Disc), 5º(Mat-Disc/Vesp-Disc).
        46. Santa Elena: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        47. Santa Rosa: 45 Salones. 1º(Matutino/Vespertino), 3º(Matutino/Vespertino), 5º(Matutino/Vespertino).
        48. Seyé: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        49. Sinanché: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        50. Sotuta: 9 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        51. Sucilá: 4 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        52. Tahdziu EMSAD: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        53. Teabo: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        54. Tecax: 12 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        55. Tecoh: 9 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        56. Tekit: 9 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        57. Tekom: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        58. Telchac Pueblo: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        59. Temax: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        60. Temozón: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        61. Tepakam: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        62. Teya: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        63. Ticopó: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        64. Ticul: 18 Salones. 1º(Matutino/Vespertino), 3º(Matutino/Vespertino), 5º(Matutino/Vespertino).
        65. Timucuy: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        66. Tinum: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        67. Tixcacalcupul EMSAD: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        68. Tixcancal EMSAD: 6 Salones. 1º(Vespertino), 3º(Matutino/Vespertino), 5º(Matutino).
        69. Tixkokob: 15 Salones. 1º(Matutino/Vespertino), 3º(Matutino/Vespertino), 5º(Matutino/Vespertino).
        70. Tixméhuac: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        71. Tixpéual: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        72. Tizimín: 18 Salones. 1º(Matutino/Vespertino), 3º(Matutino/Vespertino), 5º(Matutino/Vespertino).
        73. Tunkás: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        74. Tzucacab: 9 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        75. Uayma: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        76. Ucú: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        77. Umán: 18 Salones. 1º(Matutino/Vespertino), 3º(Matutino/Vespertino), 5º(Matutino/Vespertino).
        78. Valladolid: 18 Salones. 1º(Matutino/Vespertino), 3º(Matutino/Vespertino), 5º(Matutino/Vespertino).
        79. Xcan EMSAD: 6 Salones. 1º(Vespertino), 3º(Vespertino), 5º(Vespertino).
        80. X-Matkuil: 30 Salones. 1º(Matutino/Vespertino), 3º(Matutino/Vespertino), 5º(Matutino/Vespertino).
        81. Xocchel: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        82. Xoclán: 30 Salones. 1º(Matutino/Vespertino), 3º(Matutino/Vespertino), 5º(Matutino/Vespertino).
        83. Yaxcabá: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        84. Yaxkukul: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        85. Yobain: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        """
    }
]

# ---------------------------------------------------------
# 2. CONFIGURACIÓN DEL SISTEMA
# ---------------------------------------------------------
def generar_contexto_sistema(datos):
    contexto = "ERES ALTIUS COBAY, UN SISTEMA DE CONSULTORÍA INTELIGENTE PARA EL COLEGIO DE BACHILLERES DEL ESTADO DE YUCATÁN.\n"
    contexto += "Tu misión es fortalecer el ecosistema educativo proporcionando respuestas precisas basadas en la siguiente documentación oficial:\n\n"
    contexto += "1. REGLAMENTO INTERIOR DE TRABAJO (RIT): Obligaciones, disciplina y condiciones laborales.\n"
    contexto += "2. REGLAMENTO ACADÉMICO: Trámites, derechos y obligaciones de alumnos.\n"
    contexto += "3. CONTRATO COLECTIVO DE TRABAJO (CCT): Derechos sindicales y prestaciones.\n"
    contexto += "4. DIRECTORIO INSTITUCIONAL: Cargos, teléfonos y organigrama.\n"
    contexto += "5. CALENDARIO ESCOLAR: Fechas clave de exámenes y actividades.\n"
    contexto += "6. PLANTELES Y MATRÍCULA: Estadísticas de alumnos por plantel y semestre.\n"
    contexto += "7. INFRAESTRUCTURA: Inventario de salones y distribución de turnos por semestre.\n\n"
    contexto += "BASE DE CONOCIMIENTO UNIFICADA:\n"
    
    for item in datos:
        tipo_doc = item['metadata'].get('tipo_documento', 'Documento General')
        seccion = item['metadata']['sección']
        contenido = item['contenido']
        
        contexto += f"--- [{tipo_doc}] SECCIÓN: {seccion} ---\n"
        contexto += f"{contenido}\n\n"
    
    contexto += "\nINSTRUCCIONES PARA RESPONDER:\n"
    contexto += "1. IDENTIDAD: Preséntate como 'ALTIUS COBAY' si te preguntan quién eres.\n"
    contexto += "2. CLASIFICACIÓN: Identifica si la consulta es Laboral, Académica, Administrativa, Estadística o de Infraestructura.\n"
    contexto += "3. PRECISIÓN: Usa datos exactos del bloque de Matrícula, Calendario o Infraestructura cuando se requieran cifras o fechas.\n"
    contexto += "4. CITA: Menciona siempre la fuente (ej. 'Según el Inventario de Infraestructura...' o 'Con base en el Reglamento Académico...').\n"
    return contexto

SYSTEM_PROMPT = generar_contexto_sistema(DATOS_RAG)

safe_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# ---------------------------------------------------------
# 3. INTERFAZ DE STREAMLIT
# ---------------------------------------------------------
st.set_page_config(page_title="ALTIUS COBAY - Consultoría", page_icon="🎓", layout="wide")

st.title("🎓 ALTIUS COBAY")
st.subheader("Consultoría Inteligente")
st.markdown("**Fortaleciendo el ecosistema educativo del COBAY**")
st.markdown("---")

# --- LÓGICA DE API KEY ---
api_key = None

try:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
except (FileNotFoundError, Exception):
    pass

if not api_key:
    with st.sidebar:
        st.header("Configuración Local")
        api_key = st.text_input("Google API Key", type="password")
        st.caption("ALTIUS requiere credenciales para operar.")

if api_key:
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        st.error(f"Error de configuración: {e}")
else:
    st.info("👋 Bienvenido a ALTIUS COBAY. Por favor ingrese su API Key para comenzar.")
    st.stop()

# --- HISTORIAL Y CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def get_gemini_history():
    gemini_history = []
    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "model"
        gemini_history.append({
            "role": role,
            "parts": [msg["content"]]
        })
    return gemini_history

if prompt := st.chat_input("Consulta a ALTIUS (Ej: ¿Cuántos salones tiene el plantel Acanceh? o ¿Cuándo inician clases?)"):
    
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            model = genai.GenerativeModel(
                model_name='models/gemini-2.5-flash',
                system_instruction=SYSTEM_PROMPT,
                safety_settings=safe_settings
            )
            
            chat = model.start_chat(history=get_gemini_history()[:-1])
            response = chat.send_message(prompt, stream=True)
            
            for chunk in response:
                try:
                    if chunk.text:
                        full_response += chunk.text
                        message_placeholder.markdown(full_response + "▌")
                except Exception:
                    pass
            
            if full_response:
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            else:
                st.error("ALTIUS no pudo generar una respuesta en este momento.")

        except Exception as e:
            st.error(f"Error técnico en el sistema ALTIUS: {e}")
