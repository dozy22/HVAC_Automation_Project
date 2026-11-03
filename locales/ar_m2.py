# -*- coding: utf-8 -*-
"""Arabic copy for Module 2 — psychrometrics and the air-handling unit."""

TRANSLATIONS: dict[str, str] = {
    "Psychrometric": "العمليات السيكرومترية",
    "processes & AHU": "ووحدة مناولة الهواء",
    "Psychrometric processes & AHU": "العمليات السيكرومترية ووحدة مناولة الهواء",
    "Chapters 2 & 3 · Moist air & air handling": "الفصلان 2 و3 · الهواء الرطب ومناولة الهواء",
    "Chain": "السلسلة",
    "Coil metrics": "مؤشرات الملف",
    "Linked inputs": "مدخلات مرتبطة",
    "Module 1 loads": "أحمال الوحدة 1",
    "Move an airstream through mixing, cooling, dehumidification, heating and humidification while every state remains thermodynamically consistent. The coil solution reports ADP, bypass factor and the true coil SHR.":
        "حرّك تيار الهواء عبر الخلط والتبريد وإزالة الرطوبة والتدفئة والترطيب مع بقاء كل حالة متسقة ترموديناميكيًا. يعرض حل الملف ADP وعامل التجاوز ونسبة الحرارة المحسوسة الفعلية للملف.",
    "Module 1 has no valid design case yet. Open the cooling-load module, resolve any input error, then return here.":
        "لا توجد حالة تصميم صالحة في الوحدة 1 بعد. افتح وحدة حمل التبريد، وعالج أي خطأ في المدخلات، ثم عد إلى هنا.",
    "Cooling & dehumidification": "التبريد وإزالة الرطوبة",
    "Heating & humidification": "التدفئة والترطيب",
    "Moist-air properties": "خصائص الهواء الرطب",
    "AHU process inputs": "مدخلات عملية وحدة مناولة الهواء",
    "Cooling coil": "ملف التبريد",
    "Use Module 1 room loads": "استخدم أحمال الغرفة من الوحدة 1",
    "Connected:": "متصل:",
    "These set the supply airflow and the room-load direction.":
        "تحدد هذه القيم تدفق هواء الإمداد واتجاه حمل الغرفة.",
    "Room sensible load (kW)": "حمل الغرفة المحسوس (kW)",
    "Room latent load (kW)": "حمل الغرفة الكامن (kW)",
    "Supply-air dry-bulb (°C)": "حرارة هواء الإمداد الجافة (°C)",
    "Set outdoor-air fraction from ventilation": "حدد نسبة الهواء الخارجي من التهوية",
    "Outdoor-air fraction (%)": "نسبة الهواء الخارجي (%)",
    "Outdoor-air mass fraction (%)": "نسبة الهواء الخارجي الكتلية (%)",
    "Mass basis, not volume. Adiabatic mixing follows conservation of dry air, water vapour and enthalpy.":
        "الأساس كتلي لا حجمي. يتبع الخلط الكظومي حفظ الهواء الجاف وبخار الماء والإنثالبي.",
    "Keep the psychrometric process consistent with the current cooling-load calculation.":
        "أبقِ العملية السيكرومترية متسقة مع حساب حمل التبريد الحالي.",
    "Sensible load used to size supply airflow for the chosen supply temperature.":
        "الحمل المحسوس المستخدم لتحديد تدفق هواء الإمداد عند حرارة الإمداد المختارة.",
    "Latent load used to place the supply-state humidity ratio on the room RSHF line.":
        "الحمل الكامن المستخدم لتحديد نسبة رطوبة الإمداد على خط RSHF للغرفة.",
    "Coil leaving-air temperature. Colder air reduces airflow but requires a colder coil and more dehumidification.":
        "حرارة الهواء الخارج من الملف. الهواء الأبرد يقلل التدفق لكنه يتطلب ملفًا أبرد وإزالة رطوبة أكثر.",
    "Uses the Module 1 outdoor-air mass flow divided by the estimated supply mass flow.":
        "يستخدم التدفق الكتلي للهواء الخارجي من الوحدة 1 مقسومًا على التدفق الكتلي المقدّر للإمداد.",
    "Automatically calculated from the ventilation mass balance.":
        "يُحسب تلقائيًا من موازنة كتلة التهوية.",
    "Mass fraction of dry outdoor air in the mixed airstream.":
        "نسبة كتلة الهواء الخارجي الجاف في تيار الهواء المخلوط.",
    "Coil design load": "حمل تصميم الملف",
    "Mixed-to-supply enthalpy change": "تغير الإنثالبي من المخلوط إلى الإمداد",
    "Total cooling delivered between the mixed-air and supply-air states.":
        "إجمالي التبريد المسلّم بين حالتَي الهواء المخلوط والإمداد.",
    "Coil sensible heat ratio": "نسبة الحرارة المحسوسة للملف",
    "Sensible ÷ total coil load": "المحسوس ÷ الحمل الكلي للملف",
    "The coil SHR differs from the room RSHF because the mixed-air state and coil process are included.":
        "تختلف نسبة الحرارة المحسوسة للملف عن RSHF للغرفة لأن حالة الهواء المخلوط وعملية الملف مشمولتان.",
    "Intersection with saturation line": "التقاطع مع خط التشبع",
    "ADP is the effective coil-surface condition found by extending the coil process line to saturation.":
        "ADP هي حالة سطح الملف الفعالة الناتجة عن تمديد خط عملية الملف حتى التشبع.",
    "BPF = (W_mixed − W_supply) / (W_mixed − W_ADP). A higher value means more air bypasses the coil surface.":
        "BPF = (W_المخلوط − W_الإمداد) / (W_المخلوط − W_ADP). القيمة الأعلى تعني مرور هواء أكثر حول سطح الملف.",
    "Airflow": "تدفق الهواء",
    "OA fraction": "نسبة الهواء الخارجي",
    "The process line runs outdoor and return air to the mixed point, then through the coil toward ADP. The supply point sits on the room RSHF line.":
        "يمتد خط العملية من الهواء الخارجي والرجوع إلى نقطة الخلط، ثم عبر الملف نحو ADP. وتقع نقطة الإمداد على خط RSHF للغرفة.",
    "Try a warmer supply temperature, lower room latent load, or a lower outdoor-air fraction. The tool will not display a supersaturated state.":
        "جرّب حرارة إمداد أعلى أو حملًا كامنًا أقل للغرفة أو نسبة هواء خارجي أقل. لن تعرض الأداة حالة فوق التشبع.",
    "The process, drawn to scale": "العملية، مرسومة بمقياس صحيح",
    "Psychrometric chart": "المخطط السيكرومتري",
    "Hover any point for dry bulb, humidity ratio, relative humidity, enthalpy and wet bulb. Shaded bands are indicative rather than code-compliance zones.":
        "مرّر المؤشر فوق أي نقطة لقراءة الحرارة الجافة ونسبة الرطوبة والرطوبة النسبية والإنثالبي والحرارة الرطبة. النطاقات المظللة إرشادية وليست نطاقات امتثال كودي.",
    "Coil performance": "أداء الملف",
    "Design point": "نقطة التصميم",
    "State-point properties": "خصائص نقاط الحالة",
    "Moist air": "هواء رطب",
    "Download state points (CSV)": "تنزيل نقاط الحالة (CSV)",
    "Download coil design (CSV)": "تنزيل تصميم الملف (CSV)",
    "A high bypass factor of": "عامل تجاوز مرتفع قدره",
    "means the coil process stays far from the saturation curve while still meeting a mostly sensible load. The ADP is therefore well below the supply dry bulb.":
        "يعني أن عملية الملف تبقى بعيدة عن منحنى التشبع مع تلبية حمل محسوس في معظمه. لذلك تقع ADP أقل بكثير من حرارة الإمداد الجافة.",
    "With BPF": "بعامل BPF",
    "a meaningful share of the air reaches the coil surface, so the process bends toward the ADP and removes more moisture.":
        "تصل نسبة معتبرة من الهواء إلى سطح الملف، فتنحني العملية نحو ADP وتزيل رطوبة أكثر.",
    "outdoor-air mass fraction produces mixed air at": "كتلية من الهواء الخارجي ينتج هواء مخلوط عند",
    "Room RSHF is": "عامل RSHF للغرفة هو",
    "while the coil SHR is": "بينما نسبة الحرارة المحسوسة للملف هي",
    "the difference is the psychrometric effect of conditioning the outdoor air.":
        "والفرق هو الأثر السيكرومتري لتكييف الهواء الخارجي.",
    "The independently sized Module 1 design load is": "حمل التصميم المستقل من الوحدة 1 هو",
    "the selected mixing and supply condition gives": "وحالة الخلط والإمداد المختارة تعطي",
    "kW difference": "kW فرق",
    "Coil construction and method": "تركيب الملف ومنهجه",
    "Mixing.": "الخلط.",
    "Supply state.": "حالة الإمداد.",
    "ADP and BPF.": "ADP وBPF.",
    "Contact factor.": "عامل التلامس.",
    "Winter process": "عملية الشتاء",
    "A winter air-handling process is built here as sensible preheat followed by idealised steam humidification.":
        "تُبنى هنا عملية مناولة هواء شتوية كتسخين محسوس مسبق يتبعه ترطيب بخاري مثالي.",
    "Entering DB (°C)": "حرارة الدخول الجافة (°C)",
    "Entering RH (%)": "الرطوبة النسبية للدخول (%)",
    "Target DB (°C)": "الحرارة الجافة المستهدفة (°C)",
    "Target RH (%)": "الرطوبة النسبية المستهدفة (%)",
    "Supply mass flow (kg/s)": "التدفق الكتلي للإمداد (kg/s)",
    "Air condition before the preheat coil.": "حالة الهواء قبل ملف التسخين المسبق.",
    "Relative humidity before heating.": "الرطوبة النسبية قبل التسخين.",
    "Room supply temperature after heating and humidification.":
        "حرارة هواء الإمداد للغرفة بعد التسخين والترطيب.",
    "Desired relative humidity at the target dry bulb.":
        "الرطوبة النسبية المطلوبة عند الحرارة الجافة المستهدفة.",
    "Dry-air mass flow through the heater and steam humidifier.":
        "تدفق الهواء الجاف عبر السخان ومرطب البخار.",
    "Heating occurs at constant humidity ratio. Steam humidification is shown at approximately constant dry-bulb temperature.":
        "يحدث التسخين عند نسبة رطوبة ثابتة. ويظهر ترطيب البخار عند حرارة جافة شبه ثابتة.",
    "Sensible heating": "التسخين المحسوس",
    "Steam added": "البخار المضاف",
    "Humidifier heat": "حرارة المرطب",
    "Room supply state": "حالة هواء الإمداد للغرفة",
    "Entering air to target dry bulb at constant W":
        "من هواء الدخول إلى الحرارة الجافة المستهدفة عند W ثابت",
    "Actual moisture addition rate": "معدل إضافة الرطوبة الفعلي",
    "Enthalpy added with the steam": "الإنثالبي المضاف مع البخار",
    "Q = m·(h_heated − h_entering) along a constant humidity-ratio line.":
        "Q = m·(h_بعد التسخين − h_الدخول) على خط نسبة رطوبة ثابتة.",
    "m_steam = m_dry_air·(W_target − W_entering), converted to kg/h.":
        "m_البخار = m_الهواء الجاف·(W_الهدف − W_الدخول)، محوّلة إلى kg/h.",
    "Energy carried by the added steam, not the electrical input of a real humidifier.":
        "الطاقة المحمولة بالبخار المضاف، وليست المدخل الكهربائي لمرطب حقيقي.",
    "The target must be warmer than the entering air and its humidity ratio must not be lower than the entering condition.":
        "يجب أن يكون الهدف أدفأ من هواء الدخول وألا تقل نسبة رطوبته عن حالة الدخول.",
    "Heating and humidification path": "مسار التدفئة والترطيب",
    "The terracotta segment is sensible heating at constant W; the blue segment is the idealised steam process that supplies the required moisture.":
        "الجزء التراكوتي هو تسخين محسوس عند W ثابت؛ والجزء الأزرق هو عملية البخار المثالية التي توفر الرطوبة المطلوبة.",
    "The air is first heated from": "يُسخَّن الهواء أولًا من",
    "without changing its moisture content. Steam then raises the supply humidity ratio by":
        "دون تغيير محتوى الرطوبة. ثم يرفع البخار نسبة رطوبة الإمداد بمقدار",
    "kg/h of moisture.": "kg/h من الرطوبة.",
    "A real steam humidifier adds both latent and small sensible heat; the horizontal representation is a standard teaching idealisation.":
        "يضيف مرطب البخار الحقيقي حرارة كامنة وقليلًا من الحرارة المحسوسة؛ والتمثيل الأفقي مثالية تعليمية معتمدة.",
    "Calculate any moist-air state directly from dry-bulb temperature and either relative humidity or wet bulb.":
        "احسب أي حالة للهواء الرطب مباشرة من الحرارة الجافة ومعها الرطوبة النسبية أو الحرارة الرطبة.",
    "Dry-bulb temperature (°C)": "الحرارة الجافة (°C)",
    "Second property": "الخاصية الثانية",
    "Wet-bulb temperature (°C)": "الحرارة الرطبة (°C)",
    "Relative humidity (%)": "الرطوبة النسبية (%)",
    "Thermodynamic dry-bulb temperature at the stated pressure.":
        "درجة الحرارة الجافة الترموديناميكية عند الضغط المحدد.",
    "Choose the moisture property used to fix the thermodynamic state.":
        "اختر خاصية الرطوبة المستخدمة لتثبيت الحالة الترموديناميكية.",
    "Thermodynamic wet-bulb temperature. Must be below the dry bulb.":
        "درجة الحرارة الرطبة الترموديناميكية. يجب أن تكون أقل من الجافة.",
    "Ratio of actual vapour pressure to saturation pressure at the dry bulb.":
        "نسبة ضغط البخار الفعلي إلى ضغط التشبع عند الحرارة الجافة.",
    "Dry bulb": "الحرارة الجافة",
    "Dew point": "نقطة الندى",
    "Humidity ratio": "نسبة الرطوبة",
    "Enthalpy": "الإنثالبي",
    "Specific volume": "الحجم النوعي",
    "Vapour pressure": "ضغط البخار",
    "Thermodynamic WBT": "WBT ترموديناميكية",
    "At constant vapour pressure": "عند ضغط بخار ثابت",
    "W per kg dry air": "W لكل kg هواء جاف",
    "Moist-air mixture basis": "على أساس خليط الهواء الرطب",
    "Per kg dry air": "لكل kg هواء جاف",
    "Calculated moist-air state": "حالة الهواء الرطب المحسوبة",
    "each kilogram of dry air carries": "يحمل كل كيلوغرام من الهواء الجاف",
    "g of water vapour and": "g من بخار الماء و",
    "kJ of mixture enthalpy. The dew point is": "kJ من إنثالبي الخليط. ونقطة الندى هي",
    "so a surface below that temperature will condense moisture from this air.":
        "لذا فإن أي سطح أقل من تلك الحرارة سيكثف رطوبة من هذا الهواء.",
    "The wet bulb must lie below the dry bulb, and both must define a physically possible unsaturated state.":
        "يجب أن تقع الحرارة الرطبة تحت الجافة، وأن تحدد الاثنتان حالة غير مشبعة ممكنة فيزيائيًا.",
    "Property equations used by the engine": "معادلات الخصائص المستخدمة في المحرك",
    "Saturation pressure is evaluated with the Hyland–Wexler correlation. Humidity ratio, enthalpy, specific volume and dew point follow the ASHRAE Fundamentals relations.":
        "يُحسب ضغط التشبع بعلاقة Hyland–Wexler. وتتبع نسبة الرطوبة والإنثالبي والحجم النوعي ونقطة الندى علاقات أساسيات ASHRAE.",
    "Wet bulb is obtained by inverting the thermodynamic wet-bulb relation at the stated pressure; it is not a simple linear estimate. The comfort zone shown on the chart is an indicative teaching band, not a Standard 55 compliance check.":
        "تُحصل الحرارة الرطبة بعكس علاقة الحرارة الرطبة الترموديناميكية عند الضغط المحدد، وليست تقديرًا خطيًا بسيطًا. ومنطقة الراحة على المخطط نطاق تعليمي إرشادي وليست فحص امتثال للمعيار 55.",
}
