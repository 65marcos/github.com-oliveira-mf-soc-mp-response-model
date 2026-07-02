import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict

@dataclass
class PolymerProperties:
    # Propriedades de um polimero agricola
    name: str
    phs: float          # Polymer Hazard Score
    density: float      # g/cm3
    degradation_rate: float  # dias^-1

@dataclass  
class SoilProperties:
    # Propriedades do solo
    texture: str        # arenoso, franco, argiloso
    clay_percent: float # porcentagem argila
    ph: float
    soc_initial: float  # porcentagem

@dataclass
class ClimateProperties:
    # Propriedades climaticas
    regime: str         # arido, temperado, tropical
    uv_dose: float      # MJ/m2/ano
    mean_temp: float    # graus C
    annual_rain: float  # mm

class SOCResponseModel:
    # Modelo de resposta do SOC a contaminacao por MPs e aditivos
    # Implementa as Equacoes S16-S23 do Material Suplementar

    def __init__(self):
        # Coeficientes calibrados (Secao S5.2)
        self.k_P = 0.05   # coeficiente de polimero
        self.k_S = 0.30   # coeficiente de tamanho
        self.k_W = 0.40   # coeficiente de intemperismo
        self.k_A = 0.20   # coeficiente de interacao aditivo
        self.k_T = 0.50   # coeficiente de textura
        self.k_C = 0.15   # coeficiente climatico
        self.k_D = 0.10   # coeficiente temporal

        # Referencias
        self.PHS_ref = 11.0    # PE
        self.S_0 = 200.0       # um
        self.T_0 = 35.0        # porcentagem argila
        self.A_ref = 10.0      # mg/kg
        self.D_0 = 365.0       # dias

    def polymer_factor(self, phs: float) -> float:
        # Calcula o fator polimero (Eq. S18)
        return 1.0 + self.k_P * (phs / self.PHS_ref)

    def size_factor(self, size_um: float) -> float:
        # Calcula o fator tamanho (Eq. S19)
        return 1.0 - self.k_S * np.exp(-size_um / self.S_0)

    def weathering_factor(self, W: float, additive_conc: float) -> float:
        # Calcula o fator intemperismo (Eq. S20)
        return 1.0 + self.k_W * W * (1.0 + self.k_A * additive_conc / self.A_ref)

    def texture_factor(self, clay_percent: float) -> float:
        # Calcula o fator textura (Eq. S21)
        return 1.0 / (1.0 + self.k_T * np.exp(-clay_percent / self.T_0))

    def climate_factor(self, climate_code: int) -> float:
        # Calcula o fator clima (Eq. S22)
        # 1=arido, 2=temperado, 3=tropical
        return 1.0 + self.k_C * (climate_code - 1)

    def duration_factor(self, days: float) -> float:
        # Calcula o fator duracao (Eq. S23)
        return 1.0 + self.k_D * np.log(1.0 + days / self.D_0)

    def calculate_response(self, 
                          phs: float,
                          size_um: float,
                          weathering: float,
                          additive_conc: float,
                          clay_percent: float,
                          climate_code: int,
                          days: float) -> Dict[str, float]:
        # Calcula a resposta completa do SOC (Eq. S17)
        alpha = self.polymer_factor(phs)
        beta = self.size_factor(size_um)
        gamma = self.weathering_factor(weathering, additive_conc)
        epsilon = self.texture_factor(clay_percent)
        zeta = self.climate_factor(climate_code)
        eta = self.duration_factor(days)

        response = alpha * beta * gamma * epsilon * zeta * eta - 1.0

        return {
            'alpha_polymer': alpha,
            'beta_size': beta,
            'gamma_weathering': gamma,
            'epsilon_texture': epsilon,
            'zeta_climate': zeta,
            'eta_duration': eta,
            'delta_soc_fraction': response,
            'delta_soc_percent': response * 100
        }

    def uncertainty_analysis(self, 
                            phs: float, u_phs: float,
                            size_um: float, u_size: float,
                            weathering: float, u_weathering: float,
                            additive_conc: float, u_additive: float,
                            clay_percent: float, u_clay: float,
                            climate_code: int, u_climate: float,
                            days: float, u_days: float) -> Dict[str, float]:
        # Propagacao de incertezas (Eq. S24-S25)
        base = self.calculate_response(phs, size_um, weathering, 
                                       additive_conc, clay_percent, 
                                       climate_code, days)

        # Derivadas parciais por diferencas finitas
        h = 1e-6

        def partial(param_name, param_val):
            kwargs = {
                'phs': phs, 'size_um': size_um, 'weathering': weathering,
                'additive_conc': additive_conc, 'clay_percent': clay_percent,
                'climate_code': climate_code, 'days': days
            }
            kwargs[param_name] = param_val + h

            f_plus = self.calculate_response(**kwargs)['delta_soc_fraction']
            f_base = base['delta_soc_fraction']
            return (f_plus - f_base) / h

        # Incerteza combinada
        uc_sq = 0.0
        params_list = [
            ('phs', phs, u_phs), ('size_um', size_um, u_size),
            ('weathering', weathering, u_weathering),
            ('additive_conc', additive_conc, u_additive),
            ('clay_percent', clay_percent, u_clay),
            ('climate_code', climate_code, u_climate),
            ('days', days, u_days)
        ]

        for name, val, u in params_list:
            deriv = partial(name, val)
            uc_sq += (deriv * u) ** 2

        uc = np.sqrt(uc_sq)

        return {
            'delta_soc_fraction': base['delta_soc_fraction'],
            'combined_uncertainty': uc,
            'ci_95_lower': base['delta_soc_fraction'] - 1.96 * uc,
            'ci_95_upper': base['delta_soc_fraction'] + 1.96 * uc
        }


# ============================================================
# EXEMPLOS DE USO
# ============================================================

if __name__ == "__main__":
    model = SOCResponseModel()

    # Cenario 1: PE fresco, 500 um, solo franco, temperado, 90 dias
    print("=" * 60)
    print("CENARIO 1: PE fresco, 500 um, solo franco, temperado, 90 dias")
    print("=" * 60)
    r1 = model.calculate_response(
        phs=11.0, size_um=500, weathering=0.0, additive_conc=0,
        clay_percent=20, climate_code=2, days=90
    )
    for k, v in r1.items():
        print(f"  {k}: {v:.4f}")

    # Cenario 2: PVC intemperizado, 50 um, solo arenoso, tropical, 3 anos
    print("\n" + "=" * 60)
    print("CENARIO 2: PVC intemperizado, 50 um, solo arenoso, tropical, 3 anos")
    print("=" * 60)
    r2 = model.calculate_response(
        phs=10551.0, size_um=50, weathering=1.0, additive_conc=25.2,
        clay_percent=5, climate_code=3, days=1095
    )
    for k, v in r2.items():
        print(f"  {k}: {v:.4f}")

    # Analise de incerteza para Cenario 1
    print("\n" + "=" * 60)
    print("ANALISE DE INCERTEZA - Cenario 1")
    print("=" * 60)
    u1 = model.uncertainty_analysis(
        phs=11.0, u_phs=2.0,
        size_um=500, u_size=50,
        weathering=0.0, u_weathering=0.0,
        additive_conc=0, u_additive=0,
        clay_percent=20, u_clay=5,
        climate_code=2, u_climate=0.5,
        days=90, u_days=5
    )
    for k, v in u1.items():
        print(f"  {k}: {v:.4f}")
