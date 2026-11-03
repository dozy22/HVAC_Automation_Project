# -*- coding: utf-8 -*-
"""Arabic labels for the Plotly drawings.

Placeholders such as ``%{x:.1f}`` are deliberately preserved so hover values
keep their numeric formatting after translation.
"""

TRANSLATIONS: dict[str, str] = {
    "Saturation": "التشبع",
    "Saturation<br>T=%{x:.1f} degC<br>W=%{y:.2f} g/kg<extra></extra>":
        "التشبع<br>T=%{x:.1f} °C<br>W=%{y:.2f} g/kg<extra></extra>",
    "Comfort zone": "منطقة الراحة",
    "Indicative summer comfort zone<br>23-26 degC, 30-70% RH<extra></extra>":
        "منطقة راحة صيفية إرشادية<br>23–26 °C، رطوبة 30–70%<extra></extra>",
    "Dry-bulb temperature (degC)": "درجة الحرارة الجافة (°C)",
    "Humidity ratio (g water / kg dry air)": "نسبة الرطوبة (g ماء / kg هواء جاف)",
    "Mixing line": "خط الخلط",
    "Outdoor-to-return mixing locus<extra></extra>": "مسار الخلط من الخارج إلى الرجوع<extra></extra>",
    "Coil process / ADP": "عملية الملف / ADP",
    "Cooling and dehumidification<br>T=%{x:.1f} degC<br>W=%{y:.2f} g/kg<extra></extra>":
        "تبريد وإزالة رطوبة<br>T=%{x:.1f} °C<br>W=%{y:.2f} g/kg<extra></extra>",
    "Space load (RSHF)": "حمل الغرفة (RSHF)",
    "Room sensible-heat-factor line<extra></extra>": "خط عامل الحرارة المحسوسة للغرفة<extra></extra>",
    "Outdoor air": "الهواء الخارجي",
    "Return air": "هواء الرجوع",
    "Mixed air": "الهواء المخلوط",
    "Supply air": "هواء الإمداد",
    "Apparatus dew point": "نقطة الندى الظاهرية للملف",
    "coil": "الملف",
    "room load": "حمل الغرفة",
    "Sensible heating": "تسخين محسوس",
    "Sensible heating (constant W)<br>T=%{x:.1f} degC<extra></extra>":
        "تسخين محسوس (W ثابت)<br>T=%{x:.1f} °C<extra></extra>",
    "Steam humidification": "ترطيب بالبخار",
    "Controlled humidification<br>W=%{y:.2f} g/kg<extra></extra>":
        "ترطيب متحكم به<br>W=%{y:.2f} g/kg<extra></extra>",
    "Total (kW)": "الإجمالي (kW)",
    "Heat gain (kW)": "الكسب الحراري (kW)",
    "Refrigeration cycle": "دورة التبريد",
    "State %{customdata[0]}<br>T %{customdata[1]:.1f} degC<br>P %{y:.2f} bar<br>h %{x:.1f} kJ/kg<extra></extra>":
        "الحالة %{customdata[0]}<br>T %{customdata[1]:.1f} °C<br>P %{y:.2f} bar<br>h %{x:.1f} kJ/kg<extra></extra>",
    "2s isentropic": "2s أيزونتروبي",
    "Isentropic discharge<br>T=%{text} degC<extra></extra>":
        "طرد أيزونتروبي<br>T=%{text} °C<extra></extra>",
    "Saturation dome": "قبة التشبع",
    "Pressure (bar, logarithmic)": "الضغط (bar، مقياس لوغاريتمي)",
    "Refrigerant enthalpy (kJ/kg)": "إنثالبي المبرد (kJ/kg)",
    "Coefficient of performance": "معامل الأداء",
    "Compressor discharge temperature": "حرارة طرد الضاغط",
    "COP (-)": "COP (–)",
    "degC": "°C",
    "Outdoor": "الخارج",
    "Room": "الغرفة",
    "Setpoint": "نقطة الضبط",
    "Room RH": "رطوبة الغرفة",
    "ET* proxy": "بديل ET*",
    "%{y:.1f} degC outdoor<extra></extra>": "خارجي %{y:.1f} °C<extra></extra>",
    "Room %{y:.2f} degC<extra></extra>": "الغرفة %{y:.2f} °C<extra></extra>",
    "RH %{y:.1f}%<extra></extra>": "الرطوبة %{y:.1f}%<extra></extra>",
    "ET* %{y:.2f} degC<extra></extra>": "ET* %{y:.2f} °C<extra></extra>",
    "Time of day": "وقت اليوم",
    "Valve position (%)": "موضع الصمام (%)",
    "Supply-air temperature (degC)": "حرارة هواء الإمداد (°C)",
    "Chilled-water valve": "صمام الماء المبرد",
    "Comfort trajectory": "مسار الراحة",
    "Elapsed h": "الزمن المنقضي h",
    "Effective temperature ET* (degC)": "درجة الحرارة الفعالة ET* (°C)",
    "Relative humidity (%)": "الرطوبة النسبية (%)",
    "Start": "البداية",
    "End": "النهاية",
    "END": "النهاية",
    "Valve %{y:.0f}%<extra></extra>": "الصمام %{y:.0f}%<extra></extra>",
    "Supply %{y:.1f} degC<extra></extra>": "الإمداد %{y:.1f} °C<extra></extra>",
    "ET %{x:.2f} degC<br>RH %{y:.1f}%<br>DBT %{customdata[0]:.1f} degC<br>Hour %{customdata[1]:.1f}<extra></extra>":
        "ET %{x:.2f} °C<br>الرطوبة %{y:.1f}%<br>DBT %{customdata[0]:.1f} °C<br>الساعة %{customdata[1]:.1f}<extra></extra>",
    "%{y}<br>Sensible %{x:.2f} kW<extra></extra>":
        "%{y}<br>محسوس %{x:.2f} kW<extra></extra>",
    "%{y}<br>Latent %{x:.2f} kW<extra></extra>":
        "%{y}<br>كامن %{x:.2f} kW<extra></extra>",
    "Room sensible": "محسوس الغرفة",
    "Room latent": "كامن الغرفة",
    "Outdoor air sensible": "محسوس الهواء الخارجي",
    "Outdoor air latent": "كامن الهواء الخارجي",
    "OA sensible": "محسوس الهواء الخارجي",
    "OA latent": "كامن الهواء الخارجي",
    "Outdoor ventilation, sensible": "تهوية خارجية — محسوس",
    "Outdoor ventilation, latent": "تهوية خارجية — كامن",
    "Subcooling (K)": "التبريد الفائق (K)",
    "Superheat (K)": "التسخين الفائق (K)",
}
