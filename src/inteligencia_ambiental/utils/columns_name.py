from dataclasses import dataclass

@dataclass
class ColumnName:
    """Class for keeping track of column names."""
    data: str = "Data"
    hora_utc: str = "Hora UTC"
    precipitacao_total_horario: str = "PRECIPITAÇÃO TOTAL, HORÁRIO (mm)"
    pressao_atmosferica_ao_nivel_da_estacao_horaria: str = "PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB)"
    pressao_atmosferica_max_na_hora_ant_aut: str = "PRESSÃO ATMOSFERICA MAX.NA HORA ANT. (AUT) (mB)"
    pressao_atmosferica_min_na_hora_ant_aut: str = "PRESSÃO ATMOSFERICA MIN. NA HORA ANT. (AUT) (mB)"
    radiacao_global: str = "RADIACAO GLOBAL (Kj/m²)"
    temperatura_do_ar_bulbo_seco_horaria: str = "TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)"
    temperatura_do_ponto_de_orvalho: str = "TEMPERATURA DO PONTO DE ORVALHO (°C)"
    temperatura_maxima_na_hora_ant_aut: str = "TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)"
    temperatura_minima_na_hora_ant_aut: str = "TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)"
    temperatura_orvalho_max_na_hora_ant_aut: str = "TEMPERATURA ORVALHO MAX. NA HORA ANT. (AUT) (°C)"
    temperatura_orvalho_min_na_hora_ant_aut: str = "TEMPERATURA ORVALHO MIN. NA HORA ANT. (AUT) (°C)"
    umidade_rel_max_na_hora_ant_aut: str = "UMIDADE REL. MAX. NA HORA ANT. (AUT) (%)"
    umidade_rel_min_na_hora_ant_aut: str = "UMIDADE REL. MIN. NA HORA ANT. (AUT) (%)"
    umidade_relativa_do_ar_horaria: str = "UMIDADE RELATIVA DO AR, HORARIA (%)"
    vento_direcao_horaria: str = "VENTO, DIREÇÃO HORARIA (gr) (° (gr))"
    vento_rajada_maxima: str = "VENTO, RAJADA MAXIMA (m/s)"
    vento_velocidade_horaria: str = "VENTO, VELOCIDADE HORARIA (m/s)"