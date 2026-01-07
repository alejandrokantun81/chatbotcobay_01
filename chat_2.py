import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import os

# ---------------------------------------------------------
# 1. BASE DE CONOCIMIENTO MAESTRA (RIT + ACADÉMICO + CCT)
# ---------------------------------------------------------
DATOS_RAG = [
    # ... (Se mantiene la misma base de datos, no es necesario repetirla toda visualmente aquí
    # pero asegúrate de que al copiar, COPIES TODO EL BLOQUE DE ABAJO QUE SÍ LA INCLUYE) ...
    # PARA TU COMODIDAD, HE INCLUIDO TODO EL CÓDIGO COMPLETO ABAJO:
    
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
    }
]

# ---------------------------------------------------------
# 2. CONFIGURACIÓN DEL SISTEMA
# ---------------------------------------------------------
def generar_contexto_sistema(datos):
    contexto = "ERES UN EXPERTO JURÍDICO Y NORMATIVO DEL COBAY (Colegio de Bachilleres del Estado de Yucatán).\n"
    contexto += "Tu función es asesorar con precisión basándote en TRES documentos rectores:\n\n"
    contexto += "1. REGLAMENTO INTERIOR DE TRABAJO (RIT): Obligaciones, disciplina y condiciones generales.\n"
    contexto += "2. REGLAMENTO ACADÉMICO: Trámites escolares, derechos y obligaciones de alumnos.\n"
    contexto += "3. CONTRATO COLECTIVO DE TRABAJO (CCT): Derechos sindicales, tabuladores salariales y prestaciones económicas exclusivas.\n\n"
    contexto += "BASE DE CONOCIMIENTO UNIFICADA:\n"
    
    for item in datos:
        tipo_doc = item['metadata'].get('tipo_documento', 'Documento General')
        seccion = item['metadata']['sección']
        contenido = item['contenido']
        
        contexto += f"--- [{tipo_doc}] SECCIÓN: {seccion} ---\n"
        contexto += f"{contenido}\n\n"
    
    contexto += "\nINSTRUCCIONES PARA RESPONDER:\n"
    contexto += "1. CLASIFICA LA CONSULTA: Determina si el usuario es Trabajador (usa RIT o CCT) o Alumno (usa Académico).\n"
    contexto += "2. JERARQUÍA NORMATIVA: Si hay discrepancia, el Contrato Colectivo (CCT) suele prevalecer para trabajadores.\n"
    contexto += "3. PRECISIÓN: Cita siempre el Documento y la Cláusula/Artículo específico.\n"
    return contexto

SYSTEM_PROMPT = generar_contexto_sistema(DATOS_RAG)

safe_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# ---------------------------------------------------------
# 3. INTERFAZ DE STREAMLIT (CON CORRECCIÓN DE SECRETOS)
# ---------------------------------------------------------
st.set_page_config(page_title="Asesor Normativo COBAY", page_icon="🏛️", layout="wide")

st.title("🏛️ Asesor Integral COBAY")
st.markdown("### Laboral • Académico • Sindical")
st.markdown("---")

# --- LÓGICA DE API KEY CORREGIDA (TRY-EXCEPT) ---
api_key = None

try:
    # Intenta leer secreto (Solo funcionará en la Nube de Streamlit)
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
except (FileNotFoundError, Exception):
    # Si falla porque estamos en local sin archivo de secretos, ignoramos el error
    pass

# Si no se encontró clave en secretos, mostramos la barra lateral (Modo Local)
if not api_key:
    with st.sidebar:
        st.header("Configuración Local")
        api_key = st.text_input("Google API Key", type="password")
        st.caption("Nota: En la versión web final, esta barra desaparecerá.")

# Validación
if api_key:
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        st.error(f"Error de configuración: {e}")
else:
    st.info("👋 Para comenzar, ingrese su API Key en la barra lateral.")
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

if prompt := st.chat_input("Escribe tu consulta aquí..."):
    
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
                st.error("El modelo no pudo generar una respuesta.")

        except Exception as e:
            st.error(f"Error técnico: {e}")