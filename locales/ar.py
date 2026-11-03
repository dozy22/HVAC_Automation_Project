# -*- coding: utf-8 -*-
"""Arabic copy for the HVAC Design Studio interface.

Canonical values remain English.  Every visible English string that appears in
the interface is translated here; numeric sentence templates live in PATTERNS.
"""

TRANSLATIONS: dict[str, str] = {
    # ------------------------------------------------------------------ pages
    "Overview": "نظرة عامة",
    "01 - Cooling load": "01 - حمل التبريد",
    "02 - Psychrometrics & AHU": "02 - السيكرومترية ووحدة مناولة الهواء",
    "03 - Refrigeration cycle": "03 - دورة التبريد",
    "04 - Comfort control": "04 - الراحة والتحكم",
    "Workspace": "مساحة العمل",
    "Workspace page": "صفحة مساحة العمل",
    "Language": "اللغة",
    "Appearance": "المظهر",
    "Dark mode": "الوضع الداكن",
    "Light mode": "الوضع الفاتح",
    "Switch between the warm paper theme and a low-light drawing-board theme.":
        "بدّل بين السمة الورقية الدافئة وسمة لوح الرسم منخفضة الإضاءة.",
    "Choose the language of the interface. Calculations are unchanged.":
        "اختر لغة الواجهة. لا تتغير الحسابات.",
    "Reset workspace": "إعادة ضبط مساحة العمل",
    "Return every module to the prepared classroom demonstration case.":
        "أعد كل الوحدات إلى حالة العرض الصفية المحضّرة.",
    "Live design case": "حالة التصميم المباشرة",
    "Space": "المساحة",
    "OA flow": "تدفق هواء التهوية",
    "Case": "الحالة",
    "Session": "الجلسة",
    "Advanced HVAC & Psychrometric Automation": "نظام الأتمتة المتقدم للتدفئة والتهوية والتكييف والسيكرومترية",
    "B.Sc. Mechanical Engineering · 2026": "بكالوريوس هندسة ميكانيكية · 2026",
    "Built with Python · Streamlit · CoolProp": "مبني باستخدام Python · Streamlit · CoolProp",

    # --------------------------------------------------------------- UI helpers
    "Module": "الوحدة",
    "Design check": "فحص التصميم",
    "Educational design tool · Verify final equipment selections against project standards":
        "أداة تصميم تعليمية · تحقق من اختيارات المعدات النهائية وفق معايير المشروع",
    "Designed by (HALF ENGINEERS)": "صمم بواسطة (HALF ENGINEERS)",
    "© 2026 HALF ENGINEERS · All rights reserved": "© 2026 HALF ENGINEERS · جميع الحقوق محفوظة",
    "Advanced HVAC & Psychrometric Automation System":
        "نظام الأتمتة المتقدم للتدفئة والتهوية والتكييف والسيكرومترية",
    "Download": "تنزيل",
    "Last result": "آخر نتيجة",
    "Awaiting valid inputs": "بانتظار مدخلات صالحة",
    "Ready to simulate": "جاهز للمحاكاة",
    "Open module": "افتح الوحدة",
    "Open Module 1 to resolve the design case": "افتح الوحدة 1 لإنهاء حالة التصميم",
    "Run Module 4 to populate": "شغّل الوحدة 4 لملء النتائج",
    "Open the AHU module": "افتح وحدة مناولة الهواء",
    "Open the refrigeration module": "افتح وحدة التبريد",
    "Awaiting a valid Module 1 case": "بانتظار حالة صالحة من الوحدة 1",
    "People": "الأشخاص",
    "Zone": "المنطقة",

    # ----------------------------------------------------------------- overview
    "The presentation route": "مسار العرض",
    "Four speakers · one connected case": "أربعة متحدثين · حالة واحدة مترابطة",
    "Each speaker owns one calculation layer, but the output of each module becomes the input of the next. Open any module to recalculate live.":
        "يتولى كل متحدث طبقة حسابية واحدة، لكن ناتج كل وحدة يصبح مدخلًا للوحدة التالية. افتح أي وحدة لإعادة الحساب مباشرة.",
    "One calculation chain": "سلسلة حسابية واحدة",
    "System architecture": "بنية النظام",
    "The hand-off is deliberately explicit: room states and loads feed the AHU; the coil duty sizes the refrigeration cycle; the cycle COP informs the control dashboard.":
        "التسليم بين الوحدات صريح ومقصود: حالات الغرفة والأحمال تغذي وحدة مناولة الهواء؛ وحمولة الملف تحدد سعة دورة التبريد؛ ومعامل أداء الدورة يغذي لوحة التحكم.",
    "The design case": "حالة التصميم",
    "Common assumptions": "الافتراضات المشتركة",
    "A single 96 m² classroom case anchors the presentation. Every module can be changed independently, and all downstream calculations follow.":
        "حالة صفية واحدة بمساحة 96 m² هي محور العرض. يمكن تغيير كل وحدة بصورة مستقلة، وتتبع الحسابات اللاحقة التغيير.",
    "Resolve the Module 1 input case to populate the project record.":
        "أكمل مدخلات الوحدة 1 لملء سجل المشروع.",
    "Built for a live demonstration": "مصمم لعرض حي",
    "What is under the hood": "ما يجري في الخلفية",
    "Peak design load": "حمل التصميم الأقصى",
    "Room gains plus outdoor-air ventilation at the design condition.":
        "مكاسب الغرفة مضافًا إليها حمل تهوية الهواء الخارجي عند ظرف التصميم.",
    "Coil load": "حمل ملف التبريد",
    "Mixing and coil design from Module 2. Can differ from the Module 1 design load when the mixing fraction changes.":
        "تصميم الخلط والملف من الوحدة 2. قد يختلف عن حمل تصميم الوحدة 1 عند تغير نسبة الخلط.",
    "Plant COP": "معامل أداء المنظومة",
    "Real-fluid vapour-compression cycle coefficient of performance.":
        "معامل أداء دورة انضغاط بخاري بمائع حقيقي.",
    "Comfort maintained": "الراحة المحققة",
    "Percentage of final-half control samples inside both the ET* and 30–70% RH acceptance criteria.":
        "نسبة عينات التحكم في النصف الأخير من التشغيل التي تحقق في الوقت نفسه معيار ET* ونطاق الرطوبة 30–70%.",
    "How to read the number": "كيف تقرأ الرقم",
    "Wall / roof": "الجدار / السقف",
    "Outdoor design": "ظرف التصميم الخارجي",
    "Indoor design": "ظرف التصميم الداخلي",
    "Internal gains": "المكاسب الداخلية",
    "Current design case": "حالة التصميم الحالية",
    "Floor area": "مساحة الأرضية",
    "Occupancy": "الإشغال",
    "Room RSHF": "عامل الحرارة المحسوسة للغرفة",
    "Room gains plus outdoor-air ventilation at the design condition.":
        "مكاسب الغرفة مضافًا إليها حمل تهوية الهواء الخارجي عند ظرف التصميم.",
    "Download live design record (.md)": "تنزيل سجل التصميم المباشر (.md)",
    "Current results from every module in one Markdown record.":
        "النتائج الحالية من كل الوحدات في سجل Markdown واحد.",
    "Go to": "انتقل إلى",
    "Four interactive modules": "أربع وحدات تفاعلية",
    "ASHRAE-based moist air": "هواء رطب وفق ASHRAE",
    "CoolProp real fluids": "موائع حقيقية بـ CoolProp",
    "Presentation-ready": "جاهز للعرض",
    "Air, heat and control": "الهواء والحرارة والتحكم",
    "designed as one system.": "مصممة كنظام واحد.",
    "Advanced HVAC &amp; Psychrometric Automation": "نظام الأتمتة المتقدم للتدفئة والتهوية والتكييف والسيكرومترية",
    "A four-part engineering studio that carries one classroom design case from cooling load to psychrometric coil, refrigeration plant and closed-loop comfort control. Every number is calculated live, and every module explains the physics behind it.":
        "استوديو هندسي من أربعة أجزاء يأخذ حالة تصميم صفية واحدة من حمل التبريد إلى الملف السيكرومتري ومنظومة التبريد والتحكم المغلق في الراحة. كل رقم يُحسب مباشرة، وكل وحدة تشرح الفيزياء وراءه.",
    "01 · LOADS": "01 · الأحمال",
    "Room demand": "طلب الغرفة",
    "Envelope, solar, people, lighting, equipment and outdoor air establish sensible and latent load.":
        "الغلاف والإشعاع الشمسي والأشخاص والإضاءة والمعدات والهواء الخارجي تحدد الحمل المحسوس والكامن.",
    "02 · AIR": "02 · الهواء",
    "Coil duty": "حمولة الملف",
    "Mixing, supply state, ADP and BPF locate the process and establish the coil load.":
        "الخلط وحالة الإمداد وADP وBPF تحدد مسار العملية وحمل الملف.",
    "03 · PLANT": "03 · المنظومة",
    "Refrigeration": "التبريد",
    "Real-fluid cycle converts coil duty into compressor power, mass flow and COP.":
        "دورة المائع الحقيقي تحول حمولة الملف إلى قدرة ضاغط وتدفق كتلي ومعامل أداء.",
    "04 · CONTROL": "04 · التحكم",
    "Comfort loop": "حلقة الراحة",
    "PID or threshold action modulates capacity and holds ET* and RH inside the band.":
        "إجراء PID أو العتبة يعدّل السعة ويحافظ على ET* والرطوبة داخل النطاق.",
    "Thermodynamic core": "النواة الترموديناميكية",
    "Properties that close": "خصائص متسقة",
    "Saturation pressure, humidity ratio, enthalpy, specific volume, dew point and wet bulb are mutually consistent at the stated pressure.":
        "ضغط التشبع ونسبة الرطوبة والإنثالبي والحجم النوعي ونقطة الندى والحرارة الرطبة متسقة فيما بينها عند الضغط المحدد.",
    "Plant physics": "فيزياء المنظومة",
    "Real refrigerant states": "حالات مبرد حقيقية",
    "CoolProp resolves every cycle state. Coil ADP is found from the actual saturation-line intersection, not a table lookup.":
        "يحل CoolProp كل حالة في الدورة. تُحدد نقطة الندى الظاهرية للملف من تقاطع خط التشبع الفعلي، لا من جدول جاهز.",
    "Honest scope": "نطاق صريح",
    "Teaching model, clear limits": "نموذج تعليمي بحدود واضحة",
    "Steady peak loads and a reduced-order control zone. The comfort proxy and 30–70% RH gate are labelled as project criteria.":
        "أحمال ذروة في الحالة المستقرة ومنطقة تحكم مبسطة. بديل الراحة وبوابة الرطوبة 30–70% موسومان كمعيارين للمشروع.",
    "The hand-off is deliberately explicit: room states and loads feed the AHU; the coil duty sizes the refrigeration cycle; the cycle COP informs the control dashboard.":
        "التسليم بين الوحدات صريح ومقصود: حالات الغرفة والأحمال تغذي وحدة مناولة الهواء؛ وحمولة الملف تحدد سعة دورة التبريد؛ ومعامل أداء الدورة يغذي لوحة التحكم.",
    "Cooling load calculation": "حساب حمل التبريد",
    "Peak envelope, solar, occupancy, lighting and ventilation loads with room sensible heat factor.":
        "أحمال الغلاف والإشعاع الشمسي والإشغال والإضاءة والتهوية مع عامل الحرارة المحسوسة للغرفة.",
    "Psychrometrics & AHU": "السيكرومترية ووحدة مناولة الهواء",
    "Every moist-air property, adiabatic mixing, coil ADP and bypass factor, heating and humidification.":
        "كل خصائص الهواء الرطب والخلط الكظومي ونقطة الندى الظاهرية للملف وعامل التجاوز والتدفئة والترطيب.",
    "Vapour-compression cycle": "دورة الانضغاط البخاري",
    "Real-fluid P–h cycle, kW and tons, COP, mass flow, superheat and subcooling sensitivity.":
        "دورة P–h بمائع حقيقي، kW والأطنان وCOP والتدفق الكتلي وحساسية التسخين والتبريد الفائقين.",
    "Comfort & automatic control": "الراحة والتحكم الآلي",
    "PID or threshold control of valve position or supply temperature against an ET* and RH comfort gate.":
        "تحكم PID أو العتبة في موضع الصمام أو حرارة الإمداد وفق بوابة راحة تعتمد ET* والرطوبة النسبية.",
    "Cooling load": "حمل التبريد",
    "Where the heat comes from": "من أين تأتي الحرارة",
    "Load breakdown": "تفصيل الأحمال",
    "Room components are shown in teal and the separate outdoor-air ventilation load in amber. The design coil load is the sum of both scopes.":
        "تظهر مكونات الغرفة باللون الأخضر المزرق، ويظهر حمل تهوية الهواء الخارجي المنفصل باللون الكهرماني. حمل ملف التصميم هو مجموع النطاقين.",
    "The room load is": "حمل الغرفة هو",
    "kW with RSHF": "kW بعامل RSHF",
    "The design coil load rises to": "يرتفع حمل ملف التصميم إلى",
    "once": "بعد",
    "m³/h of outdoor ventilation air is conditioned.": "m³/h من هواء التهوية الخارجي يتم تكييفه.",
    "The result is a peak steady-state estimate. It is appropriate for teaching equipment sizing logic, not for a construction issue without hourly load analysis, duct gains and fan heat.":
        "النتيجة تقدير ذروة في الحالة المستقرة. وهي مناسبة لتعليم منطق اختيار المعدات، وليست صالحة لإصدار تنفيذي دون تحليل أحمال ساعية ومكاسب مجاري وحرارة مراوح.",

    # ------------------------------------------------------------- module 1
    "Deliverable": "المخرج",
    "Method": "الطريقة",
    "Thermal load calculation": "حساب الحمل الحراري",
    "Chapter 4 · Load estimating": "الفصل 4 · تقدير الأحمال",
    "calculation": "الحسابي",
    "Build the peak design case from the envelope outward. Room sensible and latent gains, ventilation air and the resulting room sensible heat factor are evaluated together so the psychrometric design stays honest.":
        "ابنِ حالة التصميم القصوى من الغلاف إلى الداخل. تُقيَّم مكاسب الغرفة المحسوسة والكامنة وهواء التهوية وعامل الحرارة المحسوسة الناتج معًا ليبقى التصميم السيكرومتري متسقًا.",
    "Design inputs": "مدخلات التصميم",
    "Space & ventilation": "المساحة والتهوية",
    "Zone definition": "تعريف المنطقة",
    "Project / room name": "اسم المشروع / الغرفة",
    "Used on the exported calculation record and in the sidebar.":
        "يُستخدم في سجل الحساب المُصدَّر وفي الشريط الجانبي.",
    "Length (m)": "الطول (m)",
    "Width (m)": "العرض (m)",
    "Height (m)": "الارتفاع (m)",
    "Exposed wall fraction": "نسبة الجدار المكشوف",
    "Occupants": "عدد الأشخاص",
    "Ventilation (L/s·person)": "التهوية (L/s·شخص)",
    "Infiltration (ACH)": "التسرب (ACH)",
    "Internal room length. The floor area is used for roof, lighting and occupancy gains.":
        "الطول الداخلي للغرفة. تُستخدم مساحة الأرضية لحسابات السقف والإضاءة والإشغال.",
    "Internal room width.": "العرض الداخلي للغرفة.",
    "Floor-to-ceiling height; sets the room volume and infiltration flow.":
        "الارتفاع من الأرض إلى السقف؛ يحدد حجم الغرفة وتدفق التسرب.",
    "Fraction of the perimeter wall exposed to outdoor conditions.":
        "نسبة الجدار المحيطي المعرض للظروف الخارجية.",
    "People contribute both sensible and latent heat; the count also fixes ventilation airflow.":
        "يساهم الأشخاص بحرارة محسوسة وكامنة، ويحدد العدد أيضًا تدفق هواء التهوية.",
    "Outdoor-air ventilation rate per person. This becomes the coil outdoor-air load.":
        "معدل تهوية الهواء الخارجي لكل شخص. يصبح هذا حمل الهواء الخارجي على الملف.",
    "Air changes per hour through the envelope. This is an additional untempered load.":
        "عدد تغيرات الهواء في الساعة عبر الغلاف. حمل إضافي غير معالج.",
    "Envelope & glazing": "الغلاف والزجاج",
    "Opaque + transparent": "معتم + شفاف",
    "Wall construction": "تركيب الجدار",
    "Roof construction": "تركيب السقف",
    "Glazing type": "نوع الزجاج",
    "Environment & activity": "البيئة والنشاط",
    "Design conditions": "ظروف التصميم",
    "Weather preset": "إعداد الطقس المسبق",
    "Occupant activity": "نشاط شاغلي المكان",
    "Solar exposure": "التعرض الشمسي",
    "Selecting a construction updates the default U-value and solar absorptivity.":
        "اختيار التركيب يحدث قيمة U الافتراضية ومعامل الامتصاص الشمسي.",
    "Wall U (W/m²·K)": "معامل U للجدار (W/m²·K)",
    "Wall absorptivity": "امتصاصية الجدار",
    "Roof U-value and absorptivity are set by this selection.":
        "تُضبط قيمة U للسقف والامتصاصية بهذا الاختيار.",
    "Roof U (W/m²·K)": "معامل U للسقف (W/m²·K)",
    "Roof absorptivity": "امتصاصية السقف",
    "Selecting glass updates its U-value and solar heat gain coefficient (SHGC).":
        "اختيار الزجاج يحدث قيمة U ومعامل الكسب الحراري الشمسي (SHGC).",
    "Window U (W/m²·K)": "معامل U للنافذة (W/m²·K)",
    "SHGC (–)": "SHGC (–)",
    "Window area (m²)": "مساحة النافذة (m²)",
    "Shading factor (–)": "عامل التظليل (–)",
    "Illustrative teaching conditions, not a weather-file design day.":
        "ظروف تعليمية توضيحية، وليست يوم تصميم من ملف طقس.",
    "Outdoor DB (°C)": "حرارة الهواء الخارجي الجافة (°C)",
    "Outdoor WB (°C)": "حرارة الهواء الخارجي الرطبة (°C)",
    "Indoor DB (°C)": "حرارة الهواء الداخلي الجافة (°C)",
    "Indoor RH (%)": "الرطوبة النسبية الداخلية (%)",
    "ASHRAE-style activity profiles with sensible and latent heat per person.":
        "ملفات نشاط بأسلوب ASHRAE مع حرارة محسوسة وكامنة لكل شخص.",
    "Lighting (W/m²)": "الإضاءة (W/m²)",
    "Equipment (W)": "المعدات (W)",
    "Façade orientation sets the peak solar irradiance used for the wall and glazing.":
        "اتجاه الواجهة يحدد ذروة الإشعاع الشمسي المستخدم للجدار والزجاج.",
    "Wall solar (W/m²)": "شمس الجدار (W/m²)",
    "Roof solar (W/m²)": "شمس السقف (W/m²)",
    "Advanced surface & psychrometric settings": "إعدادات متقدمة للسطح والسيكرومترية",
    "Outdoor film coefficient (W/m²·K)": "معامل الغشاء الخارجي (W/m²·K)",
    "Atmospheric pressure (kPa)": "الضغط الجوي (kPa)",
    "The default case models a 96 m², 20-person space with a hot-dry 45 °C design day. Use it as the common thread across all four modules.":
        "تمثل الحالة الافتراضية مساحة 96 m² و20 شخصًا في يوم تصميم حار جاف عند 45 °C. استخدمها خيطًا مشتركًا بين الوحدات الأربع.",
    "Check that the outdoor wet bulb is below the outdoor dry bulb, the window area fits the exposed wall, and the design condition creates a positive load.":
        "تحقق من أن الحرارة الرطبة الخارجية أقل من الجافة، وأن مساحة النافذة تناسب الجدار المكشوف، وأن ظرف التصميم ينتج حملًا موجبًا.",
    "Internal room length. The floor area is used for roof, lighting and occupancy gains.":
        "الطول الداخلي للغرفة. تُستخدم مساحة الأرضية لحسابات السقف والإضاءة والإشغال.",
    "Overall wall heat-transfer coefficient. Override the material default when you have a project value.":
        "معامل انتقال الحرارة الكلي للجدار. تجاوز قيمة المادة الافتراضية عند توفر قيمة المشروع.",
    "Solar absorptivity used in the sol-air temperature calculation.":
        "الامتصاصية الشمسية المستخدمة في حساب حرارة الهواء الشمسية المكافئة.",
    "Overall roof heat-transfer coefficient.": "معامل انتقال الحرارة الكلي للسقف.",
    "Solar absorptivity used in the roof sol-air temperature.":
        "الامتصاصية الشمسية المستخدمة في حرارة السقف الشمسية المكافئة.",
    "Glazing conduction coefficient.": "معامل التوصيل الحراري للزجاج.",
    "Solar heat gain coefficient: the fraction of incident solar radiation admitted.":
        "معامل الكسب الحراري الشمسي: نسبة الإشعاع الشمسي الساقط التي ينفذ إلى الداخل.",
    "Total glazed area; must not exceed the exposed opaque wall area.":
        "إجمالي مساحة الزجاج؛ يجب ألا يتجاوز مساحة الجدار المعتم المكشوف.",
    "1.00 is unshaded; lower values represent blinds, overhangs or external shading.":
        "القيمة 1.00 تعني دون تظليل؛ القيم الأقل تمثل الستائر أو البروزات أو التظليل الخارجي.",
    "Peak outdoor dry-bulb design temperature.": "ذروة حرارة التصميم الجافة للهواء الخارجي.",
    "Coincident outdoor wet-bulb temperature. Must be below the outdoor dry bulb.":
        "حرارة الهواء الخارجي الرطبة المتزامنة. يجب أن تكون أقل من الجافة.",
    "Room cooling setpoint used as the indoor design dry bulb.":
        "ضبط التبريد للغرفة المستخدم كحرارة التصميم الداخلية الجافة.",
    "Indoor design relative humidity; fixes the room humidity ratio.":
        "الرطوبة النسبية للتصميم الداخلي؛ تحدد نسبة رطوبة الغرفة.",
    "Connected lighting power density. All of it is treated as a room sensible gain.":
        "كثافة قدرة الإضاءة الموصلة. تُعامل كلها كمكسب محسوس للغرفة.",
    "Total equipment and plug-load heat gain in the room.":
        "إجمالي الكسب الحراري للمعدات والأحمال الموصولة في الغرفة.",
    "Incident solar irradiance on the exposed wall and glazing.":
        "الإشعاع الشمسي الساقط على الجدار المكشوف والزجاج.",
    "Incident solar irradiance on the roof surface.":
        "الإشعاع الشمسي الساقط على سطح السقف.",
    "External convective coefficient used to convert absorbed solar radiation into sol-air temperature.":
        "معامل الحمل الحراري الخارجي المستخدم لتحويل الإشعاع الشمسي الممتص إلى حرارة هواء شمسية مكافئة.",
    "Site atmospheric pressure used in all psychrometric property calculations.":
        "الضغط الجوي للموقع المستخدم في كل حسابات الخصائص السيكرومترية.",
    "Room sensible heat": "حرارة الغرفة المحسوسة",
    "Room latent heat": "حرارة الغرفة الكامنة",
    "Room sensible heat factor": "عامل الحرارة المحسوسة للغرفة",
    "Design cooling load": "حمل التبريد التصميمي",
    "Envelope, solar, people, lighting, equipment": "الغلاف، الشمس، الأشخاص، الإضاءة، المعدات",
    "Sensible room gain only. The outdoor-air ventilation load is reported separately.":
        "مكسب الغرفة المحسوس فقط. يُعرض حمل تهوية الهواء الخارجي منفصلًا.",
    "Moisture gain from occupants and infiltration, expressed as an equivalent latent cooling load.":
        "مكسب الرطوبة من الشاغلين والتسرب، معبرًا عنه كحمل تبريد كامن مكافئ.",
    "RSH ÷ (RSH + RLH), room loads only": "RSH ÷ (RSH + RLH)، أحمال الغرفة فقط",
    "RSHF locates the room-load line on the psychrometric chart. A high value means a mostly sensible load.":
        "يحدد RSHF خط حمل الغرفة على المخطط السيكرومتري. القيمة العالية تعني حملًا محسوسًا في معظمه.",
    "Room gains plus the outdoor-air ventilation load at the design condition. Fan power and duct gain are excluded.":
        "مكاسب الغرفة مضافًا إليها حمل تهوية الهواء الخارجي عند ظرف التصميم. قدرة المروحة ومكسب المجاري غير مشمولين.",
    "Net wall": "الجدار الصافي",
    "Outdoor": "الخارج",
    "Room": "الغرفة",
    "Ventilation": "التهوية",
    "Volume": "الحجم",
    "Design summary": "ملخص التصميم",
    "Peak condition": "حالة الذروة",
    "Component audit table & export": "جدول تدقيق المكونات والتصدير",
    "Download component schedule (CSV)": "تنزيل جدول المكونات (CSV)",
    "Every load component with its calculation basis.":
        "كل مكون حمل مع أساس حسابه.",
    "Download design summary (CSV)": "تنزيل ملخص التصميم (CSV)",
    "Method notes and assumptions": "ملاحظات المنهج والافتراضات",
    "Advanced surface & psychrometric settings": "إعدادات متقدمة للسطح والسيكرومترية",
    "Load breakdown": "تفصيل الأحمال",
    "Engineering reading": "القراءة الهندسية",
    "RSH · RLH · RSHF": "RSH · RLH · RSHF",
    "Sol-air envelope": "غلاف بحرارة شمسية مكافئة",
    "Room states → Module 2": "حالات الغرفة → الوحدة 2",

    # ----------------------------------------------------------- table labels
    "Metric": "البند",
    "Value": "القيمة",
    "Unit": "الوحدة",
    "State": "الحالة",
    "Refrigerant": "المبرد",
    "Controller": "المتحكم",
    "RH in band (%)": "الرطوبة ضمن النطاق (%)",
    "Cooling (kWh)": "التبريد (kWh)",
    "Electricity (kWh)": "الكهرباء (kWh)",
    "Comfort (%)": "الراحة (%)",
    "Switches": "مرات التبديل",
    "T (degC)": "T (°C)",
    "P (bar)": "P (bar)",
    "h (kJ/kg)": "h (kJ/kg)",
    "s (kJ/kg.K)": "s (kJ/kg·K)",
    "Quality": "الجودة",
    "Sensible (kW)": "محسوس (kW)",
    "Latent (kW)": "كامن (kW)",
    "Total (kW)": "الإجمالي (kW)",
    "DBT (°C)": "DBT (°C)",
    "WBT (°C)": "WBT (°C)",
    "RH (%)": "RH (%)",
    "W (g/kg)": "W (g/kg)",
    "h (kJ/kg)": "h (kJ/kg)",
    "v (m³/kg)": "v (m³/kg)",
    "COP (–)": "COP (–)",
    "Compressor (kW)": "الضاغط (kW)",
    "Mass flow (kg/s)": "التدفق الكتلي (kg/s)",
    "Discharge (°C)": "حرارة الطرد (°C)",
    "Pressure ratio": "نسبة الضغط",
    "Comfort last half (%)": "الراحة في النصف الأخير (%)",
    "Humidity in band (%)": "الرطوبة ضمن النطاق (%)",
    "Delivered cooling (kWh)": "التبريد المسلّم (kWh)",
    "Estimated electricity (kWh)": "الكهرباء المقدّرة (kWh)",
    "Switch changes": "مرات تبديل المشغل",

    # ---------------------------------------------------------------- common
    "Thermal load calculation": "حساب الحمل الحراري",
    "Design review": "مراجعة التصميم",
    "Supply air": "هواء الإمداد",
    "Outdoor air": "الهواء الخارجي",
    "Return air": "هواء الرجوع",
    "Mixed air": "الهواء المخلوط",
    "Sensible": "محسوس",
    "Latent": "كامن",
    "Total": "الإجمالي",
    "Custom": "مخصص",
    "Coefficient of performance": "معامل الأداء",
    "Pressure–enthalpy cycle": "دورة الضغط–الإنثالبي",
}

OPTION_LABELS: dict[str, str] = {
    # navigation
    "Overview": "نظرة عامة",
    "01 - Cooling load": "01 - حمل التبريد",
    "02 - Psychrometrics & AHU": "02 - السيكرومترية ووحدة مناولة الهواء",
    "03 - Refrigeration cycle": "03 - دورة التبريد",
    "04 - Comfort control": "04 - الراحة والتحكم",
    # walls
    "Brick wall, 200 mm, uninsulated": "جدار طابوق 200 mm دون عزل",
    "Brick + 50 mm insulation": "طابوق + عزل 50 mm",
    "Concrete + 50 mm insulation": "خرسانة + عزل 50 mm",
    "Insulated sandwich panel": "لوح ساندويتش معزول",
    "Glazed curtain wall": "واجهة زجاجية ستائرية",
    # roofs
    "Concrete roof, 150 mm, uninsulated": "سقف خرساني 150 mm دون عزل",
    "Concrete + 50 mm insulation": "خرسانة + عزل 50 mm",
    "Concrete + 75 mm insulation": "خرسانة + عزل 75 mm",
    "Metal deck + insulation": "سطح معدني + عزل",
    # glazing
    "Single clear glass": "زجاج مفرد شفاف",
    "Double clear glass": "زجاج مزدوج شفاف",
    "Double low-e glass": "زجاج مزدوج منخفض الانبعاثية",
    "Triple low-e glass": "زجاج ثلاثي منخفض الانبعاثية",
    # weather and activity
    "Hot dry example": "مثال حار جاف",
    "Hot humid example": "مثال حار رطب",
    "Mild example": "مثال معتدل",
    "Custom": "مخصص",
    "Seated, quiet": "جالس، هادئ",
    "Office work": "عمل مكتبي",
    "Standing / light work": "واقف / عمل خفيف",
    "Light bench work": "عمل طاولة خفيف",
    "Moderate activity": "نشاط متوسط",
    "Heavy work": "عمل شاق",
    "Hot afternoon": "بعد ظهر حار",
    "Peak summer": "ذروة الصيف",
    "Hot humid": "حار رطب",
    "Mild day": "يوم معتدل",
    # facades
    "West facade (afternoon peak)": "واجهة غربية (ذروة بعد الظهر)",
    "South facade": "واجهة جنوبية",
    "East facade (morning peak)": "واجهة شرقية (ذروة الصباح)",
    "North facade": "واجهة شمالية",
    "Custom / user value": "مخصص / قيمة المستخدم",
    # psychrometrics, cycle and control
    "Relative humidity": "الرطوبة النسبية",
    "Wet bulb": "الحرارة الرطبة",
    "Subcooling": "التبريد الفائق",
    "Superheat": "التسخين الفائق",
    "PID": "PID",
    "Threshold (on/off)": "عتبة (تشغيل/إيقاف)",
    "Chilled-water valve": "صمام الماء المبرد",
    "Supply-air temperature": "حرارة هواء الإمداد",
    "R290 (propane)": "R290 (بروبان)",
    # table categories
    "Outdoor air (OA)": "الهواء الخارجي (OA)",
    "Return air (RA)": "هواء الرجوع (RA)",
    "Mixed air (MA)": "الهواء المخلوط (MA)",
    "Supply air (SA)": "هواء الإمداد (SA)",
    "Apparatus dew point": "نقطة الندى الظاهرية للملف",
    "Cooling capacity": "سعة التبريد",
    "Specific refrigeration effect": "تأثير التبريد النوعي",
    "Refrigerant mass flow": "التدفق الكتلي للمبرد",
    "Volumetric refrigeration effect": "تأثير التبريد الحجمي",
    "Compressor power": "قدرة الضاغط",
    "Condenser heat rejection": "طرد الحرارة من المكثف",
    "Carnot COP": "COP كارنو",
    "Second-law efficiency": "كفاءة القانون الثاني",
    "Compressor discharge temperature": "حرارة طرد الضاغط",
    "Coil total load": "الحمل الكلي للملف",
    "Coil sensible load": "الحمل المحسوس للملف",
    "Coil latent load": "الحمل الكامن للملف",
    "Coil sensible heat ratio": "نسبة الحرارة المحسوسة للملف",
    "Supply-air mass flow": "التدفق الكتلي لهواء الإمداد",
    "Supply-air volume flow": "التدفق الحجمي لهواء الإمداد",
    "Outdoor-air fraction": "نسبة الهواء الخارجي",
    "Bypass factor": "عامل التجاوز",
    "Contact factor": "عامل التلامس",
    "Module 2 cooling-coil design load": "حمل تصميم ملف التبريد من الوحدة 2",
    "Module 1 design cooling load": "حمل التبريد التصميمي من الوحدة 1",
    "default demonstration load": "حمل العرض الافتراضي",
    "Room": "الغرفة",
    "Outdoor": "الخارج",
    "Sensible": "محسوس",
    "Latent": "كامن",
    "Supply-air": "هواء الإمداد",
}

# Module-specific dictionaries are kept separate so each presentation layer
# remains readable and easy to update.
from .ar_m2 import TRANSLATIONS as _M2_TRANSLATIONS  # noqa: E402
from .ar_m3 import TRANSLATIONS as _M3_TRANSLATIONS  # noqa: E402
from .ar_m4 import TRANSLATIONS as _M4_TRANSLATIONS  # noqa: E402
from .ar_charts import TRANSLATIONS as _CHART_TRANSLATIONS  # noqa: E402
from .ar_notes import TRANSLATIONS as _NOTE_TRANSLATIONS  # noqa: E402
from .ar_patterns import PATTERNS  # noqa: E402
from .ar_design import (  # noqa: E402
    OPTION_LABELS as _DESIGN_OPTIONS,
    PATTERNS as _DESIGN_PATTERNS,
    TRANSLATIONS as _DESIGN_TRANSLATIONS,
)

TRANSLATIONS.update(_M2_TRANSLATIONS)
TRANSLATIONS.update(_M3_TRANSLATIONS)
TRANSLATIONS.update(_M4_TRANSLATIONS)
TRANSLATIONS.update(_CHART_TRANSLATIONS)
TRANSLATIONS.update(_NOTE_TRANSLATIONS)
TRANSLATIONS.update(_DESIGN_TRANSLATIONS)
OPTION_LABELS.update(_DESIGN_OPTIONS)
PATTERNS.extend(_DESIGN_PATTERNS)

# ---------------------------------------------------------------------------
# Later presentation additions: brand, appearance controls and engineering
# notes that are generated inside the calculation modules.
# ---------------------------------------------------------------------------
TRANSLATIONS.update(
    {
        "HVAC Design Studio": "استوديو تصميم HVAC",
        "Psychrometrics · Loads": "السيكرومترية · الأحمال",
        "Control &amp; Comfort": "التحكم والراحة",
        "4 interactive modules": "4 وحدات تفاعلية",
        "Chapter 4": "الفصل 4",
        "Chapters 2 & 3": "الفصلان 2 و3",
        "Chapter 8": "الفصل 8",
        "Chapters 3 & 11": "الفصلان 3 و11",
        "Technical details": "التفاصيل الفنية",
        "This module could not finish the current calculation. The input state is preserved; reset the workspace if the error repeats.":
            "لم تتمكن هذه الوحدة من إكمال الحساب الحالي. حالة المدخلات محفوظة؛ أعد ضبط مساحة العمل إذا تكرر الخطأ.",
        "The result is a peak steady-state estimate. It is appropriate for teaching equipment sizing logic, not for a construction issue without hourly load analysis, duct gains and fan heat.":
            "النتيجة تقدير حمل ذروة في حالة مستقرة. وهي مناسبة لتعليم منطق تحجيم المعدات، وليست صالحة لإصدار تنفيذي دون تحليل أحمال ساعي واعتبار مكاسب القنوات وحرارة المراوح.",
        "Peak-load estimate uses a steady sol-air temperature for opaque surfaces.":
            "يستخدم تقدير حمل الذروة درجة حرارة شمسية-هوائية مستقرة للأسطح المعتمة.",
        "RSHF uses room gains only; the separate outdoor-air ventilation load is added for the design coil load.":
            "يستخدم RSHF مكاسب الغرفة فقط؛ ويُضاف حمل تهوية الهواء الخارجي المنفصل إلى حمل ملف التبريد التصميمي.",
        "Fan power, duct gain and envelope thermal lag are not included.":
            "لا تُحتسب قدرة المراوح ولا مكاسب القنوات ولا التأخر الحراري للغلاف.",
        "Window-to-wall ratio is high; check solar gain and daylight design.":
            "نسبة النافذة إلى الجدار مرتفعة؛ راجع الكسب الشمسي وتصميم الإضاءة الطبيعية.",
        "Outdoor air is drier than the room, so the outdoor latent component is negative.":
            "الهواء الخارجي أجف من هواء الغرفة، لذا يكون مكوّن الحمل الكامن الخارجي سالبًا.",
        "Psychrometrics · Loads<br>Control &amp; Comfort":
            "السيكرومترية · الأحمال<br>التحكم والراحة",
        "Designed by (HALF ENGINEERS)": "صمم بواسطة (HALF ENGINEERS)",
        "© 2026 HALF ENGINEERS · All rights reserved": "© 2026 HALF ENGINEERS · جميع الحقوق محفوظة",
    }
)

# Re-export the option map for the localisation engine.
__all__ = ["TRANSLATIONS", "OPTION_LABELS", "PATTERNS"]
