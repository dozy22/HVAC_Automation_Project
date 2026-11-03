# -*- coding: utf-8 -*-
"""Arabic templates for sentences assembled from live numbers.

Every pattern is anchored with ``fullmatch`` by the translation engine.  The
replacement strings therefore use the same numbered captures (``\\1``) and keep
the numbers exactly where they appeared in the English sentence.
"""

PATTERNS: list[tuple[str, str]] = [
    # ------------------------------------------------------------ module cards
    (r"([\d.,]+) kW · ([\d.,]+) TR", r"\1 كيلوواط · \2 طن تبريد"),
    (r"BPF ([\d.]+) · ([\d.,]+) kW coil", r"BPF \1 · ملف \2 كيلوواط"),
    (r"COP ([\d.]+) · (.+)", r"COP \1 · \2"),
    (r"([\d.]+)% comfort · ([\d.]+) switches", r"\1% راحة · \2 تبديلات"),
    (r"([\d.]+) TR · includes outdoor-air ventilation",
     r"\1 طن تبريد · يشمل تهوية الهواء الخارجي"),
    (r"BPF ([\d.]+) · ([\d.]+) kW coil", r"BPF \1 · ملف \2 كيلوواط"),

    # ----------------------------------------------------------- overview detail
    (
        r"The room load is ([\d.,]+) kW with RSHF ([\d.]+)%\. "
        r"The design coil load rises to ([\d.,]+) kW \(([\d.,]+) TR\) once "
        r"([\d.,]+) m³/h of outdoor ventilation air is conditioned\.",
        r"حمل الغرفة \1 كيلوواط وبعامل حرارة محسوسة RSHF \2%. ويرتفع حمل ملف "
        r"التبريد التصميمي إلى \3 كيلوواط (\4 طن تبريد) عند تكييف \5 م³/ساعة "
        r"من هواء التهوية الخارجي.",
    ),
    (
        r"(\d+) people · (.+)",
        r"\1 شخصًا · \2",
    ),
    (
        r"([\d.]+) L/s·person · ([\d.]+) ACH infiltration",
        r"\1 L/s·شخص · تسرب \2 ACH",
    ),
    (
        r"([\d.]+) W/m² lighting · ([\d.]+) W equipment",
        r"إضاءة \1 W/m² · معدات \2 W",
    ),
    (
        r"([\d.]+) × ([\d.]+) × ([\d.]+) m \(([\d.]+) m², ([\d.]+) m³\)",
        r"\1 × \2 × \3 m (\4 م²، \5 م³)",
    ),
    (r"U ([\d.]+) / ([\d.]+) W/m²·K", r"U \1 / \2 W/m²·K"),
    (
        r"([\d.]+) m², U ([\d.]+), SHGC ([\d.]+)",
        r"\1 م²، U \2، SHGC \3",
    ),
    (r"ADP ([\d.]+) °C · BPF ([\d.]+)", r"ADP \1 °C · BPF \2"),
    (r"(.+) · η_II ([\d.]+)%", r"\1 · η_II \2%"),
    (r"([\d.]+)/([\d.]+) °C", r"\1/\2 °C"),
    (r"([\d.]+) people", r"\1 شخصًا"),

    # ------------------------------------------------------------- module 1 feet
    (
        r"([\d.]+) people \+ ([\d.]+) ACH infiltration",
        r"\1 شخصًا + تسرب \2 ACH",
    ),
    (r"([\d.]+) TR including outdoor air",
     r"\1 طن تبريد شاملة الهواء الخارجي"),
    (
        r"The room RSHF is ([\d.]+)%, so the space-load line is steep: only "
        r"([\d.]+)% of the room gain is latent\. Adding outdoor air raises the "
        r"coil load to ([\d.]+) kW \(([\d.]+) TR\) with a coil SHR of ([\d.]+)%\.",
        r"عامل الحرارة المحسوسة للغرفة RSHF هو \1%، لذا فإن خط حمل الغرفة شديد "
        r"الميل: \2% فقط من مكاسب الغرفة كامنة. وترفع إضافة الهواء الخارجي حمل "
        r"الملف إلى \3 كيلوواط (\4 طن تبريد) بعامل حرارة محسوسة للملف SHR "
        r"قدره \5%.",
    ),

    # ------------------------------------------------------------- module 2 text
    (
        r"Connected: \*\*([\d.]+) kW sensible\*\* and \*\*([\d.]+) kW latent\*\*\. "
        r"These set the supply airflow and the room-load direction\.",
        r"متصل: **\1 كيلوواط محسوس** و**\2 كيلوواط كامن**. وهذان يحددان تدفق "
        r"هواء الإمداد واتجاه حمل الغرفة.",
    ),
    (
        r"The independently sized Module 1 design load is ([\d.]+) kW; the selected "
        r"mixing and supply condition gives ([\d.]+) kW \(([+-][\d.]+) kW difference\)\.",
        r"حمل التصميم المستقل من الوحدة 1 هو \1 كيلوواط؛ بينما يعطي الخلط وظرف "
        r"الإمداد المختاران \2 كيلوواط (فرق \3 كيلوواط).",
    ),
    (
        r"A high bypass factor of ([\d.]+) means the coil process stays far from the "
        r"saturation curve while still meeting a mostly sensible load\. The ADP is "
        r"therefore well below the supply dry bulb\.",
        r"عامل تجاوز مرتفع قدره \1 يعني أن عملية الملف تبقى بعيدة عن منحنى التشبع "
        r"مع تلبية حمل محسوس في معظمه. لذلك تقع نقطة الندى الظاهرية للملف ADP أدنى "
        r"بكثير من درجة حرارة الإمداد الجافة.",
    ),
    (
        r"With BPF ([\d.]+), a meaningful share of the air reaches the coil surface, "
        r"so the process bends toward the ADP and removes more moisture\.",
        r"مع عامل تجاوز BPF قدره \1، تصل حصة معتبرة من الهواء إلى سطح الملف، لذا "
        r"تنحني العملية نحو ADP وتزيل رطوبة أكبر.",
    ),
    (
        r"A ([\d.]+)% outdoor-air mass fraction produces mixed air at ([\d.]+) °C / "
        r"([\d.]+)% RH\.",
        r"نسبة كتلية للهواء الخارجي \1% تنتج هواءً مخلوطًا عند \2 °C / رطوبة "
        r"نسبية \3%.",
    ),
    (
        r"Room RSHF is ([\d.]+)%, while the coil SHR is ([\d.]+)%: the difference is "
        r"the psychrometric effect of conditioning the outdoor air\.",
        r"عامل الحرارة المحسوسة للغرفة RSHF هو \1%، بينما عامل الحرارة المحسوسة "
        r"للملف SHR هو \2%: والفرق هو الأثر السيكرومتري لتكييف الهواء الخارجي.",
    ),
    (
        r"The air is first heated from ([\d.]+) °C to ([\d.]+) °C without changing "
        r"its moisture content\. Steam then raises the supply humidity ratio by "
        r"([\d.]+) g/kg, using ([\d.]+) kg/h of moisture\.",
        r"يُسخَّن الهواء أولًا من \1 °C إلى \2 °C دون تغيير محتواه الرطوبي. ثم "
        r"يرفع البخار نسبة رطوبة الإمداد بمقدار \3 g/kg، مستخدمًا \4 kg/h من "
        r"الرطوبة.",
    ),
    (
        r"At ([\d.]+) °C and ([\d.]+)% RH, each kilogram of dry air carries "
        r"([\d.]+) g of water vapour and ([\d.]+) kJ of mixture enthalpy\. The dew "
        r"point is ([\d.]+) °C, so a surface below that temperature will condense "
        r"moisture from this air\.",
        r"عند \1 °C ورطوبة نسبية \2%، يحمل كل كيلوغرام من الهواء الجاف \3 g من بخار "
        r"الماء و\4 kJ من إنثالبي المخلوط. نقطة الندى هي \5 °C، لذا فإن أي سطح أدنى "
        r"من هذه الحرارة سيكثف رطوبة من هذا الهواء.",
    ),
    (r"At ([\d.]+) kPa total pressure", r"عند ضغط كلي \1 kPa"),
    (r"Contact factor ([\d.]+)", r"عامل التلامس \1"),
    (r"([\d.]+) kg/s · ([\d.]+) m³/h", r"\1 kg/s · \2 m³/h"),
    (r"([\d.]+) °C · ([\d.]+)% RH", r"\1 °C · \2% رطوبة"),
    (r"([\d.]+) °C DB · ([\d.]+) °C WB", r"\1 °C جافة · \2 °C رطبة"),
    (r"([\d.]+) kW S \+ ([\d.]+) kW L", r"\1 كيلوواط محسوس + \2 كيلوواط كامن"),
    (r"([\d.]+)% RH · W ([\d.]+) g/kg", r"\1% رطوبة · W \2 g/kg"),

    # ------------------------------------------------------------- module 3 text
    (
        r"Raising subcooling from ([\d.]+) K to ([\d.]+) K changes COP by "
        r"([+-][\d.]+)% and refrigerant mass flow by ([+-][\d.]+)%\. Subcooling "
        r"lowers the expansion-inlet enthalpy, so the evaporator produces more "
        r"refrigeration per kilogram without changing the compressor pressure ratio\.",
        r"رفع التبريد الفائق من \1 K إلى \2 K يغيّر معامل الأداء بنسبة \3% والتدفق "
        r"الكتلي للمبرد بنسبة \4%. فالتبريد الفائق يخفض إنثالبي مدخل الممدد، لذا "
        r"ينتج المبخر تبريدًا أكبر لكل كيلوغرام دون تغيير نسبة ضغط الضاغط.",
    ),
    (
        r"Raising superheat from ([\d.]+) K to ([\d.]+) K changes COP by "
        r"([+-][\d.]+)%, refrigerant mass flow by ([+-][\d.]+)%, and discharge "
        r"temperature from ([\d.]+) °C to ([\d.]+) °C\. Useful superheat protects "
        r"the compressor from liquid slugs, but excessive suction superheat lowers "
        r"suction density and increases discharge temperature\.",
        r"رفع التسخين الفائق من \1 K إلى \2 K يغيّر معامل الأداء بنسبة \3%، والتدفق "
        r"الكتلي للمبرد بنسبة \4%، وحرارة الطرد من \5 °C إلى \6 °C. التسخين الفائق "
        r"المفيد يحمي الضاغط من اندفاع السائل، لكن التسخين الفائق المفرط عند السحب "
        r"يخفض كثافة السحب ويرفع حرارة الطرد.",
    ),
    (
        r"At ([\d.]+) °C evaporating and ([\d.]+) °C condensing, the cycle reaches "
        r"COP ([\d.]+) against a Carnot ceiling of ([\d.]+)\. The compressor rejects "
        r"([\d.]+) kW at the condenser and requires ([\d.]+) kg/s of (.+)\.",
        r"عند تبخير \1 °C وتكثيف \2 °C، تبلغ الدورة معامل أداء COP قدره \3 مقابل "
        r"حد كارنو \4. ويطرد الضاغط \5 كيلوواط في المكثف ويحتاج \6 kg/s من \7.",
    ),
    (
        r"Measured model superheat is ([\d.]+) K and subcooling is ([\d.]+) K\. "
        r"Subcooling buys refrigeration effect after the condenser; suction "
        r"superheat protects the compressor but lowers suction density and raises "
        r"discharge temperature\.",
        r"التسخين الفائق المحسوب في النموذج هو \1 K والتبريد الفائق \2 K. يشتري "
        r"التبريد الفائق تأثيرًا تبريديًا بعد المكثف؛ بينما يحمي التسخين الفائق عند "
        r"السحب الضاغط لكنه يخفض كثافة السحب ويرفع حرارة الطرد.",
    ),
    (r"([\d.]+) tons of refrigeration", r"\1 طن تبريد"),
    (r"Carnot limit ([\d.]+)", r"حد كارنو \1"),
    (r"Pressure ratio ([\d.]+)", r"نسبة الضغط \1"),
    (r"Specific effect ([\d.]+) kJ/kg", r"التأثير النوعي \1 kJ/kg"),
    (r"Isentropic discharge ([\d.]+) °C", r"طرد أيزونتروبي \1 °C"),
    (r"Suction density ([\d.]+) kg/m³", r"كثافة السحب \1 kg/m³"),
    (r"([\d.]+) °C · ([\d.]+) kPa", r"\1 °C · \2 kPa"),
    (r"Connected to \*\*Module 2 cooling-coil design load\*\*\.",
     r"متصل بـ **حمل تصميم ملف التبريد من الوحدة 2**."),
    (r"Connected to \*\*Module 1 design cooling load\*\*\.",
     r"متصل بـ **حمل التبريد التصميمي من الوحدة 1**."),
    (r"Connected to \*\*default demonstration load\*\*\.",
     r"متصل بـ **حمل العرض الافتراضي**."),
    (r"Source: Module 2 cooling-coil design load\.",
     r"المصدر: حمل تصميم ملف التبريد من الوحدة 2."),
    (r"Source: Module 1 design cooling load\.",
     r"المصدر: حمل التبريد التصميمي من الوحدة 1."),
    (r"Source: default demonstration load\.",
     r"المصدر: حمل العرض الافتراضي."),
    (r"Download Subcooling sweep \(CSV\)", r"تنزيل مسار التبريد الفائق (CSV)"),
    (r"Download Superheat sweep \(CSV\)", r"تنزيل مسار التسخين الفائق (CSV)"),
    (r"Subcooling sweep", r"مسار التبريد الفائق"),
    (r"Superheat sweep", r"مسار التسخين الفائق"),
    (r"([\d.]+) sweep", r"مسار \1"),
    (r"PID · maintained in final half", r"PID · محقق في النصف الأخير"),
    (r"Threshold \(on/off\) · maintained in final half",
     r"تحكم عتبي (تشغيل/إيقاف) · محقق في النصف الأخير"),
    (r"([\d.]+) °C / ([\d.]+) °C", r"\1 °C / \2 °C"),
    (r"([\d.]+) °C · ([\d.]+) °C", r"\1 °C · \2 °C"),

    # ------------------------------------------------------------- module 4 text
    (
        r"PID records ([\d]+) actuator switch changes versus ([\d]+) for threshold "
        r"control\. Maintained comfort is ([\d.]+)% and ([\d.]+)% respectively\. "
        r"Continuous modulation reduces mechanical cycling, while on/off control is "
        r"simpler but produces larger swings\.",
        r"يسجل PID عدد \1 تبديلًا لموضع المشغل مقابل \2 للتحكم العتبي. والراحة "
        r"المحققة هي \3% و\4% على الترتيب. التعديل المستمر يقلل الدورات الميكانيكية، "
        r"بينما التحكم بالتشغيل/الإيقاف أبسط لكنه ينتج تذبذبات أكبر.",
    ),
    (r"Setpoint ([\d.]+) °C", r"نقطة الضبط \1 °C"),
    (r"Acceptance ([\d.]+)–([\d.]+)%", r"نطاق القبول \1–\2%"),
    (r"Estimated electricity ([\d.]+) kWh", r"الكهرباء المقدرة \1 kWh"),
    (r"Module 3 · ([\d.]+)", r"الوحدة 3 · \1"),
    (r"([\d.]+) °C / ([\d.]+) °C WB", r"\1 °C / \2 °C رطبة"),
    (r"([\d.]+) °C / ([\d.]+)% RH", r"\1 °C / \2% رطوبة"),

    # --------------------------------------------------------- numbers with units
    (r"([\d.]+) °C · ([\d.]+) m²", r"\1 °C · \2 م²"),
    (r"([\d.]+) m² · ([\d.]+) m³", r"\1 م² · \2 م³"),

    # ----------------------------------------------------- component audit basis
    (
        r"Sol-air ([\d.]+) degC; net wall ([\d.]+) m2",
        r"حرارة الهواء الشمسية \1 °C؛ صافي الجدار \2 م²",
    ),
    (
        r"Sol-air ([\d.]+) degC; roof ([\d.]+) m2",
        r"حرارة الهواء الشمسية \1 °C؛ السقف \2 م²",
    ),
    (r"U=([\d.]+) W/m2K", r"U=\1 W/m²·K"),
    (r"SHGC=([\d.]+); shading=([\d.]+)", r"SHGC=\1؛ التظليل=\2"),
    (
        r"([\d.]+) people; ([\d.]+) W/person",
        r"\1 شخصًا؛ \2 W/شخص",
    ),
    (
        r"([\d.]+) W/m2 over ([\d.]+) m2",
        r"\1 W/m² على مساحة \2 م²",
    ),
    (
        r"Humidity ratio difference ([+-][\d.]+) g/kg",
        r"فرق نسبة الرطوبة \1 g/kg",
    ),
    (r"([\d.]+) L/s per person", r"\1 L/s لكل شخص"),
    (r"([\d.]+) m3/h", r"\1 م³/ساعة"),
]
