# -*- coding: utf-8 -*-
"""Arabic prose for method notes, captions, table cells and chart labels.

The strings in this module are complete, whitespace-normalised paragraphs.  The
translation engine first tries a whole paragraph before it falls back to lines,
so long method notes stay coherent and keep their Markdown emphasis, inline
code and equations intact.
"""

TRANSLATIONS: dict[str, str] = {
    # ------------------------------------------------------ module 1 method notes
    "**Opaque envelope.** Wall and roof gains use sol-air temperature, `T_sol = T_out + α·G / h_o`, so absorbed solar radiation is represented without a separate radiant model.":
        "**الغلاف المعتم.** تُحسب مكاسب الجدار والسقف باستخدام حرارة الهواء الشمسية، `T_sol = T_out + α·G / h_o`، لذا تُمثَّل الطاقة الشمسية الممتصة دون نموذج إشعاعي منفصل.",
    "**Glazing.** Conduction uses `U·A·(T_out − T_in)`. Solar transmission uses `SHGC·A·G·SC`, where the shading factor reduces the incident irradiance.":
        "**الزجاج.** يُحسب التوصيل بالعلاقة `U·A·(T_out − T_in)`. ويُحسب الانتقال الشمسي بالعلاقة `SHGC·A·G·SC`، حيث يخفض معامل التظليل الإشعاع الساقط.",
    "**Room versus coil load.** Internal, envelope and infiltration gains form the room load and set RSHF. Ventilation outdoor air is a separate coil load and is added afterward for equipment sizing.":
        "**حمل الغرفة مقابل حمل الملف.** تُشكّل المكاسب الداخلية ومكاسب الغلاف والتسرب حمل الغرفة وتحدد RSHF. أما هواء التهوية الخارجي فهو حمل منفصل للملف ويُضاف لاحقًا لاختيار سعة المعدات.",
    "**Scope.** This is a steady peak estimate. It does not model thermal lag, fan heat, duct gain, or hour-by-hour solar and occupancy profiles.":
        "**النطاق.** هذا تقدير ذروة في الحالة المستقرة، ولا يمثل التأخير الحراري أو حرارة المروحة أو مكاسب القنوات أو تغير الشمس والإشغال ساعة بساعة.",

    # ------------------------------------------------------ module 2 method notes
    "**Mixing.** Outdoor and return air combine adiabatically on a dry-air mass basis: `W_mix = f·W_OA + (1−f)·W_RA` and `h_mix = f·h_OA + (1−f)·h_RA`.":
        "**الخلط.** يمتزج الهواء الخارجي وهواء الرجوع بشكل كظومي على أساس كتلة الهواء الجاف: `W_mix = f·W_OA + (1−f)·W_RA` و`h_mix = f·h_OA + (1−f)·h_RA`.",
    "**Supply state.** Sensible room load sets the dry-air mass flow, `m = Q_s / [c_p,m·(T_RA − T_SA)]`. Latent room load then places the supply humidity ratio: `W_SA = W_RA − Q_l / (m·h_fg)`.":
        "**حالة الإمداد.** يحدد الحمل المحسوس للغرفة التدفق الكتلي للهواء الجاف، `m = Q_s / [c_p,m·(T_RA − T_SA)]`. ثم يحدد الحمل الكامن للغرفة نسبة رطوبة الإمداد: `W_SA = W_RA − Q_l / (m·h_fg)`.",
    "**ADP and BPF.** The straight line from mixed air through supply air is extended to its nearest intersection with the saturation curve. BPF is the humidity-ratio distance ratio `(W_MA − W_SA) / (W_MA − W_ADP)`.":
        "**ADP وBPF.** يمتد الخط المستقيم من الهواء المخلوط عبر هواء الإمداد إلى أقرب تقاطع له مع منحنى التشبع. وBPF هو نسبة مسافة نسبة الرطوبة `(W_MA − W_SA) / (W_MA − W_ADP)`.",
    "**Contact factor.** Reported as `1 − BPF`. A real coil also has air-side and refrigerant-side resistances, which this chart-level model does not resolve.":
        "**عامل التلامس.** يُعرض على أنه `1 − BPF`. للملف الحقيقي أيضًا مقاومات على جانب الهواء وجانب المبرد لا يفصلها هذا النموذج بمستوى الرسم البياني.",

    # ------------------------------------------------------ module 4 method notes
    "**Effective-temperature proxy.** The dashboard uses `ET* = T_db + 0.04·(RH − 50)`, anchored so that dry-bulb and ET* coincide at 50% RH. It captures the direction and rough magnitude of humidity's effect on warmth but is not the full ASHRAE ET*.":
        "**بديل درجة الحرارة الفعالة.** تستخدم اللوحة `ET* = T_db + 0.04·(RH − 50)`، مع تثبيت المرجع بحيث تتطابق الحرارة الجافة وET* عند رطوبة 50%. ويعكس البديل اتجاه تأثير الرطوبة على الإحساس بالدفء ومقداره التقريبي، لكنه ليس ET* الكامل وفق ASHRAE.",
    "**Comfort gate.** A sample is comfortable only when ET* is inside its band and RH is between 30% and 70%. The relative-humidity band is a project/teaching criterion supplied with this brief. ASHRAE Standard 55 does not impose one universal lower RH limit; full compliance requires PMV/PPD with air temperature, mean radiant temperature, air speed, humidity, clothing and metabolic rate.":
        "**بوابة الراحة.** تكون العينة مريحة فقط عندما تقع ET* داخل نطاقها وتكون RH بين 30% و70%. ونطاق الرطوبة النسبية معيار مشروع/تعليمي مرفق بهذا الموجز. ولا تفرض ASHRAE Standard 55 حدًا أدنى عالميًا واحدًا للرطوبة النسبية؛ ويتطلب الامتثال الكامل حساب PMV/PPD مع حرارة الهواء ومتوسط حرارة الإشعاع وسرعة الهواء والرطوبة والملابس ومعدل الأيض.",
    "**Controllers.** PID uses measurement-based derivative action and conditional-integration anti-windup. Threshold control uses a deadband and hysteresis. The chilled-water valve scales rated sensible capacity; the supply-air actuator blends between minimum and maximum supply temperature.":
        "**المتحكمات.** يستخدم PID إجراءً تفاضليًا قائمًا على القياس ومنعًا شرطيًا لتراكم الحد التكاملي. ويستخدم التحكم العتبي نطاقًا ميتًا وتخلفًا. يغيّر صمام الماء المبرد السعة المحسوسة المقدرة؛ ويمزج مشغل هواء الإمداد بين أدنى وأعلى حرارة إمداد.",
    "**Zone model.** A lumped energy balance and moisture balance are integrated at 60 s steps: `C·dT/dt = Q_internal + UA·(T_out − T_room) + Q_infiltration − Q_cool`. Latent removal uses a simplified wet-coil bypass model. Thermal mass, infiltration, internal gains and weather are illustrative rather than a calibrated building-energy model.":
        "**نموذج المنطقة.** يُدمج توازن طاقة مجمّع وتوازن رطوبة بخطوات زمنية قدرها 60 ثانية: `C·dT/dt = Q_internal + UA·(T_out − T_room) + Q_infiltration − Q_cool`. وتستخدم الإزالة الكامنة نموذج تجاوز مبسطًا للملف المبلل. الكتلة الحرارية والتسرب والمكاسب الداخلية والطقس توضيحية وليست نموذجًا معايرًا لطاقة المبنى.",

    # ----------------------------------------------------------- captions and labels
    "ET* is a transparent humidity-adjusted teaching proxy. The 30–70% RH band is a project criterion, not a universal Standard 55 requirement.":
        "ET* بديل تعليمي شفاف معدّل بالرطوبة. ونطاق الرطوبة النسبية 30–70% معيار مشروع، وليس متطلبًا عالميًا في Standard 55.",
    "Room design": "ظرف الغرفة التصميمي",
    "Room loads": "أحمال الغرفة",
    "Calculated state": "الحالة المحسوبة",
    "Zone temperature": "حرارة المنطقة",
    "Effective temperature": "درجة الحرارة الفعالة",
    "Relative humidity": "الرطوبة النسبية",
    "Wet bulb": "الحرارة الرطبة",
    "Parameter": "البند",
    "Scope": "النطاق",
    "Category": "الفئة",
    "Item": "العنصر",
    "Basis": "الأساس",
    "Outdoor air": "الهواء الخارجي",
    "Envelope": "الغلاف",
    "Solar": "شمسي",
    "Internal": "داخلي",
    "Infiltration": "التسرب",
    "Project": "المشروع",
    "Geometry": "الأبعاد",
    "Wall / roof": "الجدار / السقف",
    "Glazing": "الزجاج",
    "Outdoor design": "ظرف التصميم الخارجي",
    "Indoor design": "ظرف التصميم الداخلي",
    "Occupancy": "الإشغال",
    "Internal gains": "المكاسب الداخلية",
    "Hand-off": "التسليم بين الوحدات",
    "kW · TR · COP · mass flow": "kW · TR · COP · التدفق الكتلي",
    "Advanced HVAC & Psychrometric Automation System":
        "نظام الأتمتة المتقدم للتدفئة والتهوية والتكييف والسيكرومترية",
    "Indicative summer comfort zone": "منطقة الراحة الصيفية الإرشادية",
    "Outdoor-to-return mixing locus": "مسار خلط الهواء الخارجي والراجع",
    "Cooling and dehumidification": "تبريد وإزالة رطوبة",
    "Room sensible-heat-factor line": "خط عامل الحرارة المحسوسة للغرفة",
    "Sensible heating (constant W)": "تسخين محسوس (W ثابت)",
    "Controlled humidification": "ترطيب مضبوط",
    "Isentropic discharge": "طرد أيزونتروبي",
    "Discharge temperature": "حرارة الطرد",
    "Time of day": "وقت اليوم",
    "COP (-)": "COP (–)",

    # ---------------------------------------------------------- module 1 tables
    "Room sensible heat (RSH)": "الحمل المحسوس للغرفة (RSH)",
    "Room latent heat (RLH)": "الحمل الكامن للغرفة (RLH)",
    "Room total heat": "الحمل الكلي للغرفة",
    "Room sensible heat factor (RSHF)": "عامل الحرارة المحسوسة للغرفة (RSHF)",
    "Outdoor ventilation sensible": "الهواء الخارجي للتهوية — محسوس",
    "Outdoor ventilation latent": "الهواء الخارجي للتهوية — كامن",
    "Design sensible heat (incl. OA)": "الحمل المحسوس التصميمي (شامل الهواء الخارجي)",
    "Design latent heat (incl. OA)": "الحمل الكامن التصميمي (شامل الهواء الخارجي)",
    "Design load in tons of refrigeration": "حمل التصميم بالأطنان التبريدية",
    "Wall conduction": "التوصيل عبر الجدار",
    "Roof conduction": "التوصيل عبر السقف",
    "Window conduction": "التوصيل عبر الزجاج",
    "Window solar transmission": "الانتقال الشمسي عبر الزجاج",
    "Occupants, sensible": "الأشخاص — محسوس",
    "Occupants, latent": "الأشخاص — كامن",
    "Lighting": "الإضاءة",
    "Equipment": "المعدات",
    "Infiltration, sensible": "التسرب — محسوس",
    "Infiltration, latent": "التسرب — كامن",
    "Outdoor ventilation, sensible": "الهواء الخارجي للتهوية — محسوس",
    "Outdoor ventilation, latent": "الهواء الخارجي للتهوية — كامن",
    "Connected equipment heat gain": "الكسب الحراري للمعدات الموصولة",
    "T (degC)": "T (°C)",
    "s (kJ/kg.K)": "s (kJ/kg·K)",

    # ---------------------------------------------------------- module 3 tables
    "1 - Compressor suction": "1 - سحب الضاغط",
    "2 - Compressor discharge": "2 - طرد الضاغط",
    "3 - Condenser exit (subcooled)": "3 - خروج المكثف (مبرد فائق)",
    "3 - Condenser exit (saturated liquid)": "3 - خروج المكثف (سائل مشبع)",
    "4 - Expansion-valve outlet": "4 - خروج صمام التمدد",
}
