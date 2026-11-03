"""Moist-air property functions implemented from the ASHRAE Fundamentals.

The formulas use SI units:
    temperature           degC
    pressure               kPa
    humidity ratio         kg water / kg dry air
    enthalpy               kJ / kg dry air
    specific volume        m3 / kg dry air

The saturation-pressure equations are the Hyland-Wexler correlations in
ASHRAE Handbook - Fundamentals, Chapter 1 (Psychrometrics).  They are accurate
over the normal HVAC range and are the basis of the chart and AHU calculations.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

P_ATM_STD_KPA = 101.325
R_DRY_AIR = 0.287042  # kJ/(kg.K), also kPa.m3/(kg.K)
CP_DRY_AIR = 1.006  # kJ/(kg.K)
CP_VAPOR = 1.86  # kJ/(kg.K)
H_FG_0 = 2501.0  # kJ/kg at 0 degC
MW_RATIO = 0.621945  # kg water / kg dry air


@dataclass(frozen=True)
class PsychrometricState:
    """A complete moist-air state at a specified total pressure."""

    dry_bulb_c: float
    wet_bulb_c: float
    dew_point_c: float
    relative_humidity_pct: float
    humidity_ratio: float  # kg/kg dry air
    enthalpy_kj_kg: float  # kJ/kg dry air
    specific_volume_m3_kg: float  # m3/kg dry air
    vapor_pressure_kpa: float
    pressure_kpa: float = P_ATM_STD_KPA

    @property
    def humidity_ratio_g_kg(self) -> float:
        return self.humidity_ratio * 1000.0

    @property
    def density_kg_m3(self) -> float:
        """Density of the moist-air mixture per m3 of humid air."""
        return (1.0 + self.humidity_ratio) / self.specific_volume_m3_kg

    @property
    def moisture_content_g_m3(self) -> float:
        return self.humidity_ratio * self.density_kg_m3 * 1000.0

    def as_dict(self) -> dict[str, float]:
        return {
            "Dry-bulb temperature (degC)": self.dry_bulb_c,
            "Wet-bulb temperature (degC)": self.wet_bulb_c,
            "Dew-point temperature (degC)": self.dew_point_c,
            "Relative humidity (%)": self.relative_humidity_pct,
            "Humidity ratio (g/kg da)": self.humidity_ratio_g_kg,
            "Enthalpy (kJ/kg da)": self.enthalpy_kj_kg,
            "Specific volume (m3/kg da)": self.specific_volume_m3_kg,
        }


def _as_float(value: float, name: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a number.") from exc
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite.")
    return result


def saturation_pressure_kpa(dry_bulb_c: float) -> float:
    """Saturation vapour pressure over water or ice, in kPa."""
    t_c = _as_float(dry_bulb_c, "Dry-bulb temperature")
    if t_c <= -100.0 or t_c >= 200.0:
        raise ValueError("Dry-bulb temperature must be between -100 and 200 degC.")
    kelvin = t_c + 273.15

    if t_c <= 0.0:
        ln_pws = (
            -5.6745359e3 / kelvin
            + 6.3925247
            - 9.677843e-3 * kelvin
            + 6.2215701e-7 * kelvin**2
            + 2.0747825e-9 * kelvin**3
            - 9.484024e-13 * kelvin**4
            + 4.1635019 * math.log(kelvin)
        )
    else:
        ln_pws = (
            -5.8002206e3 / kelvin
            + 1.3914993
            - 4.8640239e-2 * kelvin
            + 4.1764768e-5 * kelvin**2
            - 1.4452093e-8 * kelvin**3
            + 6.5459673 * math.log(kelvin)
        )
    return math.exp(ln_pws) / 1000.0


def saturation_pressure_kpa_array(dry_bulb_c: np.ndarray) -> np.ndarray:
    """Vectorised saturation pressure for chart generation."""
    temps = np.asarray(dry_bulb_c, dtype=float)
    kelvin = temps + 273.15
    with np.errstate(invalid="ignore", divide="ignore", over="ignore"):
        ice = np.exp(
            -5.6745359e3 / kelvin
            + 6.3925247
            - 9.677843e-3 * kelvin
            + 6.2215701e-7 * kelvin**2
            + 2.0747825e-9 * kelvin**3
            - 9.484024e-13 * kelvin**4
            + 4.1635019 * np.log(kelvin)
        )
        water = np.exp(
            -5.8002206e3 / kelvin
            + 1.3914993
            - 4.8640239e-2 * kelvin
            + 4.1764768e-5 * kelvin**2
            - 1.4452093e-8 * kelvin**3
            + 6.5459673 * np.log(kelvin)
        )
    result = np.where(temps <= 0.0, ice, water) / 1000.0
    return np.asarray(result, dtype=float)


def _validate_pressure(pressure_kpa: float) -> float:
    pressure = _as_float(pressure_kpa, "Atmospheric pressure")
    if not 40.0 <= pressure <= 120.0:
        raise ValueError("Atmospheric pressure must be between 40 and 120 kPa.")
    return pressure


def saturation_humidity_ratio(
    dry_bulb_c: float, pressure_kpa: float = P_ATM_STD_KPA
) -> float:
    """Humidity ratio of saturated air (kg/kg dry air)."""
    pressure = _validate_pressure(pressure_kpa)
    pws = saturation_pressure_kpa(dry_bulb_c)
    if pws >= pressure:
        return float("inf")
    return MW_RATIO * pws / (pressure - pws)


def humidity_ratio_from_rh(
    dry_bulb_c: float,
    relative_humidity_pct: float,
    pressure_kpa: float = P_ATM_STD_KPA,
) -> float:
    """Humidity ratio from dry-bulb temperature and relative humidity."""
    pressure = _validate_pressure(pressure_kpa)
    rh = _as_float(relative_humidity_pct, "Relative humidity")
    if not 0.0 <= rh <= 100.0:
        raise ValueError("Relative humidity must be between 0 and 100 percent.")
    pws = saturation_pressure_kpa(dry_bulb_c)
    pw = (rh / 100.0) * pws
    if pw >= pressure:
        raise ValueError("Vapour pressure cannot equal or exceed total pressure.")
    return MW_RATIO * pw / (pressure - pw)


def relative_humidity_from_ratio(
    dry_bulb_c: float,
    humidity_ratio: float,
    pressure_kpa: float = P_ATM_STD_KPA,
) -> float:
    """Relative humidity (%) from dry-bulb temperature and humidity ratio."""
    pressure = _validate_pressure(pressure_kpa)
    w = _as_float(humidity_ratio, "Humidity ratio")
    if w < 0.0:
        raise ValueError("Humidity ratio cannot be negative.")
    pw = pressure * w / (MW_RATIO + w)
    pws = saturation_pressure_kpa(dry_bulb_c)
    rh = 100.0 * pw / pws
    return min(100.0, max(0.0, rh))


def enthalpy_from_state(dry_bulb_c: float, humidity_ratio: float) -> float:
    """Moist-air enthalpy relative to dry air and saturated liquid at 0 degC."""
    return CP_DRY_AIR * float(dry_bulb_c) + float(humidity_ratio) * (
        H_FG_0 + CP_VAPOR * float(dry_bulb_c)
    )


def humidity_ratio_from_enthalpy(dry_bulb_c: float, enthalpy_kj_kg: float) -> float:
    """Invert h = 1.006T + W(2501 + 1.86T)."""
    denominator = H_FG_0 + CP_VAPOR * dry_bulb_c
    if abs(denominator) < 1e-9:
        raise ValueError("Dry-bulb temperature is outside the solvable range.")
    return (enthalpy_kj_kg - CP_DRY_AIR * dry_bulb_c) / denominator


def dry_bulb_from_enthalpy_ratio(
    enthalpy_kj_kg: float, humidity_ratio: float
) -> float:
    """Dry-bulb temperature for an enthalpy and humidity-ratio pair."""
    denominator = CP_DRY_AIR + CP_VAPOR * humidity_ratio
    return (enthalpy_kj_kg - H_FG_0 * humidity_ratio) / denominator


def specific_volume(
    dry_bulb_c: float,
    humidity_ratio: float,
    pressure_kpa: float = P_ATM_STD_KPA,
) -> float:
    """Specific volume of moist air, per kg dry air."""
    pressure = _validate_pressure(pressure_kpa)
    t_kelvin = dry_bulb_c + 273.15
    if t_kelvin <= 0:
        raise ValueError("Dry-bulb temperature must be above absolute zero.")
    return R_DRY_AIR * t_kelvin * (1.0 + 1.607858 * humidity_ratio) / pressure


def _wet_bulb_ratio_raw(
    dry_bulb_c: float, wet_bulb_c: float, pressure_kpa: float
) -> float:
    """Raw ASHRAE wet-bulb relation; can be negative outside its physical range."""
    db = dry_bulb_c
    wb = min(wet_bulb_c, dry_bulb_c)
    ws_star = saturation_humidity_ratio(wb, pressure_kpa)
    if not math.isfinite(ws_star):
        raise ValueError("Wet-bulb condition is outside the valid range.")

    if wb >= 0.0:
        numerator = (H_FG_0 - 2.326 * wb) * ws_star - CP_DRY_AIR * (db - wb)
        denominator = H_FG_0 + CP_VAPOR * db - 4.186 * wb
    else:
        numerator = (2830.0 - 0.24 * wb) * ws_star - CP_DRY_AIR * (db - wb)
        denominator = 2830.0 + CP_VAPOR * db - 2.1 * wb
    return numerator / denominator


def humidity_ratio_from_wet_bulb(
    dry_bulb_c: float,
    wet_bulb_c: float,
    pressure_kpa: float = P_ATM_STD_KPA,
) -> float:
    """Humidity ratio from the thermodynamic wet-bulb relation (ASHRAE)."""
    pressure = _validate_pressure(pressure_kpa)
    db = _as_float(dry_bulb_c, "Dry-bulb temperature")
    wb = _as_float(wet_bulb_c, "Wet-bulb temperature")
    if wb > db + 0.02:
        raise ValueError("Wet-bulb temperature cannot exceed dry-bulb temperature.")
    wb = min(wb, db)
    humidity_ratio = _wet_bulb_ratio_raw(db, wb, pressure)
    if humidity_ratio < -1e-9:
        raise ValueError("The supplied wet-bulb temperature gives invalid air.")
    return max(0.0, humidity_ratio)


def wet_bulb_from_rh(
    dry_bulb_c: float,
    relative_humidity_pct: float,
    pressure_kpa: float = P_ATM_STD_KPA,
) -> float:
    """Invert the ASHRAE wet-bulb relation numerically (bisection)."""
    pressure = _validate_pressure(pressure_kpa)
    db = _as_float(dry_bulb_c, "Dry-bulb temperature")
    rh = _as_float(relative_humidity_pct, "Relative humidity")
    if not 0.0 <= rh <= 100.0:
        raise ValueError("Relative humidity must be between 0 and 100 percent.")
    if rh >= 99.999:
        return db

    target_w = humidity_ratio_from_rh(db, rh, pressure)
    high = db
    w_high = _wet_bulb_ratio_raw(db, high, pressure)
    if target_w > w_high + 1e-9:
        raise ValueError("Unable to resolve the wet-bulb temperature for this state.")

    # The raw relation can become negative below its physical domain. Walk
    # downward until the curve lies below the target, then bisect.
    low = db - 1.0
    w_low = _wet_bulb_ratio_raw(db, low, pressure)
    while w_low > target_w and low > -95.0:
        low -= 1.0
        w_low = _wet_bulb_ratio_raw(db, low, pressure)
    if w_low > target_w:
        raise ValueError("Unable to resolve the wet-bulb temperature for this state.")

    for _ in range(120):
        mid = 0.5 * (low + high)
        w_mid = _wet_bulb_ratio_raw(db, mid, pressure)
        if w_mid < target_w:
            low = mid
        else:
            high = mid
        if high - low < 1e-7:
            break
    return 0.5 * (low + high)


def dew_point_from_rh(
    dry_bulb_c: float,
    relative_humidity_pct: float,
    pressure_kpa: float = P_ATM_STD_KPA,
) -> float:
    """Dew-point temperature by inverting the saturation-pressure curve."""
    pressure = _validate_pressure(pressure_kpa)
    db = _as_float(dry_bulb_c, "Dry-bulb temperature")
    rh = _as_float(relative_humidity_pct, "Relative humidity")
    if not 0.0 <= rh <= 100.0:
        raise ValueError("Relative humidity must be between 0 and 100 percent.")
    if rh == 0.0:
        return -95.0

    pws = saturation_pressure_kpa(db)
    pw = rh / 100.0 * pws
    if pw <= 1e-9:
        return -95.0
    if pw >= pressure * 0.999:
        raise ValueError("Dew point is outside the valid pressure range.")

    low, high = -95.0, min(db, 200.0)
    for _ in range(100):
        mid = 0.5 * (low + high)
        if saturation_pressure_kpa(mid) < pw:
            low = mid
        else:
            high = mid
        if high - low < 1e-7:
            break
    return 0.5 * (low + high)


def psychrometric_state(
    dry_bulb_c: float,
    pressure_kpa: float = P_ATM_STD_KPA,
    *,
    relative_humidity_pct: float | None = None,
    humidity_ratio: float | None = None,
    wet_bulb_c: float | None = None,
) -> PsychrometricState:
    """Build a complete moist-air state from one humidity specification."""
    pressure = _validate_pressure(pressure_kpa)
    db = _as_float(dry_bulb_c, "Dry-bulb temperature")
    if not -80.0 <= db <= 90.0:
        raise ValueError("Dry-bulb temperature must be between -80 and 90 degC.")
    inputs = [
        relative_humidity_pct is not None,
        humidity_ratio is not None,
        wet_bulb_c is not None,
    ]
    if sum(inputs) != 1:
        raise ValueError("Specify exactly one of relative humidity, humidity ratio, or wet bulb.")

    if relative_humidity_pct is not None:
        rh = _as_float(relative_humidity_pct, "Relative humidity")
        if not 0.0 <= rh <= 100.0:
            raise ValueError("Relative humidity must be between 0 and 100 percent.")
        w = humidity_ratio_from_rh(db, rh, pressure)
        wb = wet_bulb_from_rh(db, rh, pressure)
    elif humidity_ratio is not None:
        w = _as_float(humidity_ratio, "Humidity ratio")
        if w < 0.0:
            raise ValueError("Humidity ratio cannot be negative.")
        w_sat = saturation_humidity_ratio(db, pressure)
        if w > w_sat + 2e-6:
            raise ValueError("Humidity ratio exceeds saturation at this dry-bulb temperature.")
        rh = relative_humidity_from_ratio(db, w, pressure)
        wb = wet_bulb_from_rh(db, rh, pressure)
    else:
        wb = _as_float(wet_bulb_c, "Wet-bulb temperature")
        w = humidity_ratio_from_wet_bulb(db, wb, pressure)
        rh = relative_humidity_from_ratio(db, w, pressure)

    if w < 0.0 or not math.isfinite(w):
        raise ValueError("The chosen condition is not physically valid.")
    if rh > 100.0 + 1e-6:
        raise ValueError("The chosen condition is supersaturated.")

    rh = min(100.0, max(0.0, rh))
    w = max(0.0, w)
    pw = pressure * w / (MW_RATIO + w)
    h = enthalpy_from_state(db, w)
    v = specific_volume(db, w, pressure)
    dp = dew_point_from_rh(db, rh, pressure)
    return PsychrometricState(
        dry_bulb_c=db,
        wet_bulb_c=wb,
        dew_point_c=dp,
        relative_humidity_pct=rh,
        humidity_ratio=w,
        enthalpy_kj_kg=h,
        specific_volume_m3_kg=v,
        vapor_pressure_kpa=pw,
        pressure_kpa=pressure,
    )


def state_from_enthalpy_humidity_ratio(
    enthalpy_kj_kg: float,
    humidity_ratio: float,
    pressure_kpa: float = P_ATM_STD_KPA,
) -> PsychrometricState:
    """Construct a state from enthalpy and humidity ratio (used for mixing)."""
    w = _as_float(humidity_ratio, "Humidity ratio")
    h = _as_float(enthalpy_kj_kg, "Enthalpy")
    db = dry_bulb_from_enthalpy_ratio(h, w)
    return psychrometric_state(
        db, pressure_kpa, humidity_ratio=w
    )


def moist_air_specific_heat(humidity_ratio: float) -> float:
    """Approximate humid-air specific heat, kJ/(kg dry air.K)."""
    return CP_DRY_AIR + CP_VAPOR * float(humidity_ratio)


def saturation_curve(
    dry_bulb_min_c: float,
    dry_bulb_max_c: float,
    pressure_kpa: float = P_ATM_STD_KPA,
    points: int = 220,
) -> tuple[np.ndarray, np.ndarray]:
    """Saturation curve arrays for psychrometric charts."""
    temps = np.linspace(dry_bulb_min_c, dry_bulb_max_c, points)
    pws = saturation_pressure_kpa_array(temps)
    with np.errstate(divide="ignore", invalid="ignore"):
        ratios = MW_RATIO * pws / (pressure_kpa - pws)
    return temps, ratios


def relative_humidity_curve(
    dry_bulb_min_c: float,
    dry_bulb_max_c: float,
    relative_humidity_pct: float,
    pressure_kpa: float = P_ATM_STD_KPA,
    points: int = 220,
) -> tuple[np.ndarray, np.ndarray]:
    """Constant-relative-humidity curve arrays."""
    temps = np.linspace(dry_bulb_min_c, dry_bulb_max_c, points)
    pws = saturation_pressure_kpa_array(temps)
    pw = relative_humidity_pct / 100.0 * pws
    with np.errstate(divide="ignore", invalid="ignore"):
        ratios = MW_RATIO * pw / (pressure_kpa - pw)
    return temps, ratios


def wet_bulb_curve_arrays(
    wet_bulb_c: float,
    dry_bulb_min_c: float,
    dry_bulb_max_c: float,
    pressure_kpa: float = P_ATM_STD_KPA,
    points: int = 100,
) -> tuple[np.ndarray, np.ndarray]:
    """Constant thermodynamic wet-bulb line for charting."""
    db_min = max(dry_bulb_min_c, wet_bulb_c)
    temps = np.linspace(db_min, dry_bulb_max_c, points)
    ratios = np.array(
        [humidity_ratio_from_wet_bulb(float(t), wet_bulb_c, pressure_kpa) for t in temps]
    )
    return temps, ratios
