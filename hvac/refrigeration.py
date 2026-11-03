"""Vapour-compression refrigeration cycle analysis using CoolProp.

State numbering follows the standard cycle:
    1  compressor suction (evaporator exit)
    2  compressor discharge
    3  condenser exit / expansion-valve inlet
    4  evaporator inlet (after throttling)
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import math

import pandas as pd
from CoolProp.CoolProp import PropsSI

TR_KW = 3.5168525

REFRIGERANTS: dict[str, str] = {
    "R134a": "R134a",
    "R410A": "R410A",
    "R32": "R32",
    "R22": "R22",
    "R404A": "R404A",
    "R290 (propane)": "R290",
}


@dataclass(frozen=True)
class CycleInputs:
    refrigerant: str = "R134a"
    evaporating_c: float = 2.0
    condensing_c: float = 45.0
    superheat_k: float = 5.0
    subcooling_k: float = 5.0
    isentropic_efficiency: float = 0.75
    cooling_load_kw: float = 12.0


@dataclass(frozen=True)
class CycleState:
    number: int
    label: str
    temperature_c: float
    pressure_bar: float
    enthalpy_kj_kg: float
    entropy_kj_kgk: float
    quality: float | None


@dataclass(frozen=True)
class CycleResult:
    inputs: CycleInputs
    fluid: str
    suction: CycleState
    discharge: CycleState
    condenser_exit: CycleState
    evaporator_inlet: CycleState
    discharge_isentropic_c: float
    pressure_ratio: float
    specific_refrigeration_kj_kg: float
    volumetric_refrigeration_kj_m3: float
    mass_flow_kg_s: float
    volume_flow_m3_s: float
    cooling_kw: float
    cooling_tr: float
    compressor_kw: float
    condenser_kw: float
    cop: float
    carnot_cop: float
    second_law_efficiency: float
    suction_density_kg_m3: float
    evaporator_pressure_kpa: float
    condenser_pressure_kpa: float
    suction_vapor_quality: float | None
    subcooled_liquid: bool

    def states_table(self) -> pd.DataFrame:
        rows = []
        for state in (
            self.suction,
            self.discharge,
            self.condenser_exit,
            self.evaporator_inlet,
        ):
            rows.append(
                {
                    "State": f"{state.number} - {state.label}",
                    "T (degC)": state.temperature_c,
                    "P (bar)": state.pressure_bar,
                    "h (kJ/kg)": state.enthalpy_kj_kg,
                    "s (kJ/kg.K)": state.entropy_kj_kgk,
                    "Quality": state.quality,
                }
            )
        return pd.DataFrame(rows)

    def summary_table(self) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "Metric": [
                    "Cooling capacity",
                    "Cooling capacity",
                    "Refrigerant mass flow",
                    "Compressor power",
                    "Condenser heat rejection",
                    "Coefficient of performance",
                    "Carnot COP",
                    "Second-law efficiency",
                    "Pressure ratio",
                    "Specific refrigeration effect",
                    "Volumetric refrigeration effect",
                    "Compressor discharge temperature",
                ],
                "Value": [
                    self.cooling_kw,
                    self.cooling_tr,
                    self.mass_flow_kg_s,
                    self.compressor_kw,
                    self.condenser_kw,
                    self.cop,
                    self.carnot_cop,
                    self.second_law_efficiency * 100.0,
                    self.pressure_ratio,
                    self.specific_refrigeration_kj_kg,
                    self.volumetric_refrigeration_kj_m3,
                    self.discharge.temperature_c,
                ],
                "Unit": [
                    "kW",
                    "TR",
                    "kg/s",
                    "kW",
                    "kW",
                    "-",
                    "-",
                    "%",
                    "-",
                    "kJ/kg",
                    "kJ/m3",
                    "degC",
                ],
            }
        )


def _fluid_name(refrigerant: str) -> str:
    try:
        return REFRIGERANTS[refrigerant]
    except KeyError as exc:
        raise ValueError(f"Unsupported refrigerant: {refrigerant}") from exc


def _prop(output: str, key1: str, value1: float, key2: str, value2: float, fluid: str) -> float:
    try:
        return float(PropsSI(output, key1, value1, key2, value2, fluid))
    except Exception as exc:
        raise ValueError("CoolProp could not evaluate this operating point.") from exc


def compute_cycle(inputs: CycleInputs) -> CycleResult:
    """Compute a steady vapour-compression cycle at the stated capacity."""
    fluid = _fluid_name(inputs.refrigerant)
    if not -50.0 <= inputs.evaporating_c <= 30.0:
        raise ValueError("Evaporating temperature must be between -50 and 30 degC.")
    if not -20.0 <= inputs.condensing_c <= 80.0:
        raise ValueError("Condensing temperature must be between -20 and 80 degC.")
    if inputs.condensing_c <= inputs.evaporating_c + 3.0:
        raise ValueError("Condensing temperature must be at least 3 K above evaporating temperature.")
    if not 0.0 <= inputs.superheat_k <= 60.0:
        raise ValueError("Superheat must be between 0 and 60 K.")
    if not 0.0 <= inputs.subcooling_k <= 40.0:
        raise ValueError("Subcooling must be between 0 and 40 K.")
    if not 0.30 <= inputs.isentropic_efficiency <= 1.0:
        raise ValueError("Isentropic efficiency must be between 0.30 and 1.00.")
    if inputs.cooling_load_kw <= 0.0:
        raise ValueError("Cooling load must be positive.")

    t_evap_k = inputs.evaporating_c + 273.15
    t_cond_k = inputs.condensing_c + 273.15
    t_suction_k = t_evap_k + inputs.superheat_k
    t_liquid_k = t_cond_k - inputs.subcooling_k

    try:
        p_evap_pa = float(PropsSI("P", "T", t_evap_k, "Q", 1.0, fluid))
        p_cond_pa = float(PropsSI("P", "T", t_cond_k, "Q", 0.0, fluid))
        t_critical_k = float(PropsSI("Tcrit", fluid))
    except Exception as exc:
        raise ValueError(
            "CoolProp could not establish the saturation states. Check the refrigerant and temperatures."
        ) from exc
    if t_cond_k >= t_critical_k:
        raise ValueError("Condensing temperature is above the refrigerant critical temperature.")

    p_evap_bar = p_evap_pa / 1e5
    p_cond_bar = p_cond_pa / 1e5

    # State 1: superheated vapour at evaporating pressure.  At effectively zero
    # superheat, CoolProp needs the saturated-vapour quality pair to avoid an
    # indeterminate T/P lookup on the saturation boundary.
    saturated_suction = inputs.superheat_k <= 0.01
    if saturated_suction:
        h1 = _prop("H", "P", p_evap_pa, "Q", 1.0, fluid) / 1000.0
        s1 = _prop("S", "P", p_evap_pa, "Q", 1.0, fluid) / 1000.0
        rho1 = _prop("D", "P", p_evap_pa, "Q", 1.0, fluid)
        t1_c = inputs.evaporating_c
    else:
        h1 = _prop("H", "T", t_suction_k, "P", p_evap_pa, fluid) / 1000.0
        s1 = _prop("S", "T", t_suction_k, "P", p_evap_pa, fluid) / 1000.0
        rho1 = _prop("D", "T", t_suction_k, "P", p_evap_pa, fluid)
        t1_c = _prop("T", "P", p_evap_pa, "H", h1 * 1000.0, fluid) - 273.15

    # Isentropic compression, then actual discharge via isentropic efficiency.
    h2s = _prop("H", "P", p_cond_pa, "S", s1 * 1000.0, fluid) / 1000.0
    h2 = h1 + (h2s - h1) / inputs.isentropic_efficiency
    t2_c = _prop("T", "P", p_cond_pa, "H", h2 * 1000.0, fluid) - 273.15
    s2 = _prop("S", "P", p_cond_pa, "H", h2 * 1000.0, fluid) / 1000.0
    t2s_c = _prop("T", "P", p_cond_pa, "S", s1 * 1000.0, fluid) - 273.15

    # State 3: compressed liquid at condenser pressure.  At zero subcooling use
    # the saturated-liquid quality pair for the same numerical reason.
    no_subcooling = inputs.subcooling_k <= 0.01
    if no_subcooling:
        h3 = _prop("H", "P", p_cond_pa, "Q", 0.0, fluid) / 1000.0
        s3 = _prop("S", "P", p_cond_pa, "Q", 0.0, fluid) / 1000.0
        t3_c = inputs.condensing_c
    else:
        h3 = _prop("H", "T", t_liquid_k, "P", p_cond_pa, fluid) / 1000.0
        s3 = _prop("S", "T", t_liquid_k, "P", p_cond_pa, fluid) / 1000.0
        t3_c = _prop("T", "P", p_cond_pa, "H", h3 * 1000.0, fluid) - 273.15
    hf_cond = _prop("H", "T", t_cond_k, "Q", 0.0, fluid) / 1000.0
    subcooled = h3 < hf_cond - 1e-6

    # State 4: isenthalpic expansion.
    h4 = h3
    x4 = _prop("Q", "P", p_evap_pa, "H", h4 * 1000.0, fluid)
    if not -1e-6 <= x4 <= 1.000001:
        raise ValueError("Expansion state is outside the two-phase region; adjust subcooling.")
    t4_c = _prop("T", "P", p_evap_pa, "Q", min(1.0, max(0.0, x4)), fluid) - 273.15
    s4 = _prop("S", "P", p_evap_pa, "H", h4 * 1000.0, fluid) / 1000.0

    q_evap = h1 - h4
    w_comp = h2 - h1
    q_cond = h2 - h3
    if q_evap <= 0 or w_comp <= 0:
        raise ValueError("Cycle states are not physically valid. Check operating temperatures.")

    mass_flow = inputs.cooling_load_kw / q_evap
    compressor_kw = mass_flow * w_comp
    condenser_kw = mass_flow * q_cond
    cop = q_evap / w_comp
    carnot_cop = t_evap_k / (t_cond_k - t_evap_k)
    second_law = cop / carnot_cop if carnot_cop > 0 else 0.0
    pressure_ratio = p_cond_pa / p_evap_pa
    v1 = 1.0 / rho1
    q_volumetric = q_evap / v1

    def quality_at(p_pa: float, h_kj: float) -> float | None:
        try:
            q = float(PropsSI("Q", "P", p_pa, "H", h_kj * 1000.0, fluid))
            return q if 0.0 <= q <= 1.0 else None
        except Exception:
            return None

    suction_quality = 1.0 if saturated_suction else quality_at(p_evap_pa, h1)
    suction = CycleState(
        number=1,
        label="Compressor suction",
        temperature_c=t1_c,
        pressure_bar=p_evap_bar,
        enthalpy_kj_kg=h1,
        entropy_kj_kgk=s1,
        quality=suction_quality,
    )
    discharge = CycleState(
        number=2,
        label="Compressor discharge",
        temperature_c=t2_c,
        pressure_bar=p_cond_bar,
        enthalpy_kj_kg=h2,
        entropy_kj_kgk=s2,
        quality=None,
    )
    condenser_exit = CycleState(
        number=3,
        label="Condenser exit (subcooled)" if subcooled else "Condenser exit (saturated liquid)",
        temperature_c=t3_c,
        pressure_bar=p_cond_bar,
        enthalpy_kj_kg=h3,
        entropy_kj_kgk=s3,
        quality=quality_at(p_cond_pa, h3),
    )
    evaporator_inlet = CycleState(
        number=4,
        label="Expansion-valve outlet",
        temperature_c=t4_c,
        pressure_bar=p_evap_bar,
        enthalpy_kj_kg=h4,
        entropy_kj_kgk=s4,
        quality=max(0.0, min(1.0, x4)),
    )

    return CycleResult(
        inputs=inputs,
        fluid=fluid,
        suction=suction,
        discharge=discharge,
        condenser_exit=condenser_exit,
        evaporator_inlet=evaporator_inlet,
        discharge_isentropic_c=t2s_c,
        pressure_ratio=pressure_ratio,
        specific_refrigeration_kj_kg=q_evap,
        volumetric_refrigeration_kj_m3=q_volumetric,
        mass_flow_kg_s=mass_flow,
        volume_flow_m3_s=mass_flow * v1,
        cooling_kw=inputs.cooling_load_kw,
        cooling_tr=inputs.cooling_load_kw / TR_KW,
        compressor_kw=compressor_kw,
        condenser_kw=condenser_kw,
        cop=cop,
        carnot_cop=carnot_cop,
        second_law_efficiency=second_law,
        suction_density_kg_m3=rho1,
        evaporator_pressure_kpa=p_evap_pa / 1000.0,
        condenser_pressure_kpa=p_cond_pa / 1000.0,
        suction_vapor_quality=quality_at(p_evap_pa, h1),
        subcooled_liquid=subcooled,
    )


def sensitivity_sweep(
    base: CycleInputs,
    variable: str,
    values: list[float] | tuple[float, ...],
) -> pd.DataFrame:
    """Recompute the cycle while varying superheat or subcooling."""
    if variable not in {"superheat_k", "subcooling_k"}:
        raise ValueError("Sensitivity variable must be superheat_k or subcooling_k.")
    if len(values) < 2:
        raise ValueError("Provide at least two sensitivity values.")
    rows: list[dict[str, float]] = []
    for value in values:
        trial = replace(base, **{variable: float(value)})
        result = compute_cycle(trial)
        rows.append(
            {
                variable: float(value),
                "COP": result.cop,
                "Cooling kW": result.cooling_kw,
                "Compressor kW": result.compressor_kw,
                "Specific refrigeration kJ/kg": result.specific_refrigeration_kj_kg,
                "Mass flow kg/s": result.mass_flow_kg_s,
                "Discharge temperature C": result.discharge.temperature_c,
                "Second-law efficiency %": result.second_law_efficiency * 100.0,
            }
        )
    return pd.DataFrame(rows)


def saturation_dome(
    refrigerant: str,
    temperature_min_c: float,
    temperature_max_c: float,
    points: int = 120,
) -> tuple[list[float], list[float], list[float]]:
    """Saturation-dome enthalpy (kJ/kg) and pressure (bar) arrays."""
    fluid = _fluid_name(refrigerant)
    try:
        t_critical = float(PropsSI("Tcrit", fluid)) - 273.15
    except Exception as exc:
        raise ValueError("CoolProp could not provide refrigerant data.") from exc
    high = min(float(temperature_max_c), t_critical - 0.2)
    low = max(float(temperature_min_c), -70.0)
    if high <= low:
        raise ValueError("Saturation dome temperature range is invalid.")
    temps = [low + (high - low) * i / (points - 1) for i in range(points)]

    h_liquid: list[float] = []
    h_vapor: list[float] = []
    pressures: list[float] = []
    for t_c in temps:
        t_k = t_c + 273.15
        try:
            p = float(PropsSI("P", "T", t_k, "Q", 0.0, fluid))
            hf = float(PropsSI("H", "T", t_k, "Q", 0.0, fluid)) / 1000.0
            hg = float(PropsSI("H", "T", t_k, "Q", 1.0, fluid)) / 1000.0
        except Exception:
            continue
        pressures.append(p / 1e5)
        h_liquid.append(hf)
        h_vapor.append(hg)
    if not pressures:
        raise ValueError("No saturation data could be generated for this range.")
    return h_liquid, h_vapor, pressures
