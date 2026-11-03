# -*- coding: utf-8 -*-
"""Arabic copy for the quick design studio and the design-day simulation.

Templates keep their numbered placeholders exactly as they appear in English,
because the presentation layer translates the sentence first and interpolates
the live numbers afterwards.
"""

TRANSLATIONS: dict[str, str] = {
    # ---------------------------------------------------------------- hero
    "Quick design studio": "استوديو التصميم السريع",
    "Quick design case": "حالة التصميم السريع",
    "Quick studio + 4 modules": "استوديو سريع + 4 وحدات",
    "A quick studio at the front turns six simple answers into a sized system and a full design day.":
        "يحوّل استوديو سريع في البداية ست إجابات بسيطة إلى نظام محدد الحجم ويوم تصميم كامل.",
    "New: quick design & simulation": "جديد: التصميم والمحاكاة السريعة",
    "Only know the space, the city and the build quality? Six answers are enough.":
        "لا تعرف سوى المساحة والمدينة وجودة البناء؟ ست إجابات تكفي.",
    "The quick studio sizes the cooling, recommends the system and plays the hottest day back hour by hour.":
        "يحدد الاستوديو السريع حجم التبريد، ويوصي بالنظام، ويعيد عرض أحر يوم ساعةً بساعة.",
    "Open the quick studio": "افتح الاستوديو السريع",
    "Start from six simple questions instead of the full engineering input set.":
        "ابدأ من ستة أسئلة بسيطة بدلًا من مجموعة المدخلات الهندسية الكاملة.",
    "6 answers": "6 إجابات",
    "Six answers.": "ست إجابات.",
    "A sized system and a design day.": "نظام محدد الحجم ويوم تصميم كامل.",
    "Say what the space is, where it is and how it is built. The studio calculates the cooling it needs, recommends the most sensible system and runs the hottest day hour by hour. The detailed engineering modules stay one click away.":
        "قل ما هي المساحة وأين تقع وكيف بُنيت. يحسب الاستوديو التبريد المطلوب، ويوصي بأنسب نظام، ويشغّل أحر يوم ساعةً بساعة. وتبقى الوحدات الهندسية التفصيلية على بعد نقرة واحدة.",
    "Inputs": "المدخلات",
    "Physics": "الفيزياء",
    "Chapter-4 load engine": "محرك أحمال الفصل 4",
    "Simulation": "المحاكاة",
    "24 h · 10 min steps": "24 ساعة · خطوات 10 دقائق",
    "View": "العرض",
    "Arabic · English": "العربية · الإنجليزية",

    # ---------------------------------------------------------------- form
    "Tell the studio about the space": "أخبر الاستوديو عن المساحة",
    "Six answers": "ست إجابات",
    "Check the floor area, the glazing ratio and the custom design temperatures.":
        "راجع مساحة الأرضية ونسبة الزجاج ودرجات حرارة التصميم المخصصة.",
    "Type of space": "نوع المساحة",
    "Occupancy density, lighting, equipment, fresh air, infiltration and the daily schedule all follow this choice.":
        "كثافة الإشغال والإضاءة والمعدات والهواء النقي والتسرب والجدول اليومي تتبع هذا الاختيار.",
    "Floor area (m²)": "مساحة الأرضية (م²)",
    "The cooled floor area. Room shape, wall area and roof area are derived from it.":
        "مساحة الأرضية المكيفة. تُشتق منها أبعاد الغرفة ومساحة الجدار والسقف.",
    "City": "المدينة",
    "Sets the outdoor design dry bulb, wet bulb and the day–night swing. Choose Other / custom to enter your own.":
        "تحدد درجة حرارة التصميم الخارجية الجافة والرطبة وتفاوت الليل والنهار. اختر أخرى / مخصص لإدخال ظرفك.",
    "Window area (% of wall)": "مساحة النوافذ (% من الجدار)",
    "Glazed share of the exposed wall. More glass means more daylight and more solar gain.":
        "نسبة الزجاج من الجدار المعرض. الزجاج الأكثر يعني إضاءة طبيعية أكثر وكسبًا شمسيًا أكبر.",
    "Main window orientation": "اتجاه النافذة الرئيسية",
    "The façade that receives the main afternoon or morning sun. West is the harshest in a hot climate.":
        "الواجهة التي تستقبل شمس العصر أو الصباح الأساسية. الغرب هو الأقسى في المناخ الحار.",
    "Build quality": "جودة البناء",
    "Wall, roof and window U-values, shading and infiltration follow this choice.":
        "قيم U للجدار والسقف والنافذة والتظليل والتسرب تتبع هذا الاختيار.",
    "Height, occupancy, lighting, equipment, fresh air and infiltration follow the space type. Open the advanced panel only if you need to change them.":
        "الارتفاع والإشغال والإضاءة والمعدات والهواء النقي والتسرب تتبع نوع المساحة. افتح اللوحة المتقدمة فقط إذا احتجت إلى تغييرها.",
    "Fine-tune the assumptions": "اضبط الافتراضات بدقة",
    "Set occupancy manually": "تحديد عدد الأشخاص يدويًا",
    "Off: the studio counts people from the space type and floor area. On: use your own count.":
        "إيقاف: يحسب الاستوديو عدد الأشخاص من نوع المساحة ومساحتها. تشغيل: استخدم عددك.",
    "Occupants": "عدد الأشخاص",
    "People add both sensible and latent heat and set the fresh-air flow.":
        "يضيف الأشخاص حرارة محسوسة وكامنة ويحددون تدفق الهواء النقي.",
    "Automatic occupancy: {n} people, about one person per {area:.1f} m².":
        "إشغال تلقائي: {n} شخصًا، بمعدل شخص واحد لكل {area:.1f} م² تقريبًا.",
    "Indoor setpoint (°C)": "نقطة ضبط الغرفة (°C)",
    "The dry-bulb temperature the control loop holds while the space is occupied.":
        "درجة الحرارة الجافة التي تحافظ عليها حلقة التحكم أثناء إشغال المساحة.",
    "Indoor relative humidity (%)": "الرطوبة النسبية الداخلية (%)",
    "Design indoor moisture condition. It fixes the room humidity ratio and the latent load.":
        "ظرف الرطوبة الداخلي التصميمي. يحدد نسبة رطوبة الغرفة والحمل الكامن.",
    "System preference": "تفضيل النظام",
    "Leave on Auto to let the studio choose from the size and the space type.":
        "اتركه على تلقائي ليختار الاستوديو حسب الحجم ونوع المساحة.",
    "Selection margin (%)": "هامش الاختيار (%)",
    "Spare capacity above the calculated load for duct gain, fan heat and real-world tolerance.":
        "سعة احتياطية فوق الحمل المحسوب لمكاسب القنوات وحرارة المراوح والتفاوت الواقعي.",
    "Custom outdoor dry bulb (°C)": "درجة الحرارة الجافة الخارجية المخصصة (°C)",
    "Peak design outdoor dry-bulb temperature for your site.":
        "ذروة درجة الحرارة الجافة الخارجية التصميمية لموقعك.",
    "Custom outdoor wet bulb (°C)": "درجة الحرارة الرطبة الخارجية المخصصة (°C)",
    "Coincident outdoor wet bulb. It must stay below the dry bulb.":
        "درجة الحرارة الرطبة الخارجية المصاحبة. يجب أن تبقى أدنى من الجافة.",

    # --------------------------------------------------------- preset notes
    "Domestic room with evening occupancy and a lighter internal gain.":
        "غرفة منزلية بإشغال مسائي ومكاسب داخلية أخف.",
    "Working hours dominate; people and plug loads are the steady gains.":
        "ساعات العمل هي الأساس؛ والأشخاص والأحمال الكهربائية هي المكاسب الثابتة.",
    "High occupant density for a short teaching day.":
        "كثافة إشغال عالية ليوم دراسي قصير.",
    "Tall, open sales floor with strong lighting and door traffic.":
        "صالة عرض مرتفعة ومفتوحة بإضاءة قوية وحركة أبواب.",
    "Kitchen equipment and a long evening schedule drive the load.":
        "معدات المطبخ وجدول مسائي طويل يقودان الحمل.",
    "Large volume, dense prayer peaks and a heavy envelope mass.":
        "حجم كبير وذروات صلاة كثيفة وكتلة غلاف ثقيلة.",
    "Continuous equipment load and a higher fresh-air rate.":
        "حمل معدات مستمر ومعدل هواء نقي أعلى.",
    "Hot dry summer design day.": "يوم تصميم صيفي حار وجاف.",
    "Hot and humid Gulf design day.": "يوم تصميم خليجي حار ورطب.",
    "Hot summer with a wide day–night swing.":
        "صيف حار بتفاوت واسع بين الليل والنهار.",
    "Warm summer and cool nights.": "صيف دافئ وليالٍ باردة.",
    "Hot dry design day.": "يوم تصميم حار وجاف.",
    "Enter your own design condition.": "أدخل ظرف التصميم الخاص بك.",
    "Single glazing and little insulation; expect a heavier load.":
        "زجاج مفرد وعزل قليل؛ توقّع حملًا أكبر.",
    "Insulated wall and double glazing: a common modern build.":
        "جدار معزول وزجاج مزدوج: بناء حديث شائع.",
    "Low-e glazing, good insulation and controlled infiltration.":
        "زجاج منخفض الانبعاثية وعزل جيد وتسرب مضبوط.",
    "Diffuse light all day; the mildest façade.":
        "ضوء منتشر طوال اليوم؛ ألطف واجهة.",
    "Morning sun; the peak arrives before midday.":
        "شمس الصباح؛ تصل الذروة قبل منتصف النهار.",
    "High midday sun; overhangs work well here.":
        "شمس منتصف النهار العالية؛ تعمل الكوابيل جيدًا هنا.",
    "Afternoon sun; the hottest and latest peak.":
        "شمس العصر؛ الذروة الأشد والأحدث.",
    "Simple, low first cost, and easy to add one unit at a time.":
        "بسيط، تكلفة أولية منخفضة، وسهل التوسع وحدةً تلو الأخرى.",
    "A ducted distribution for open plans, with a fresh-air duct.":
        "توزيع بقنوات للمساحات المفتوحة مع قناة هواء نقي.",
    "Zoned indoor units with strong part-load efficiency through the day.":
        "وحدات داخلية مقسمة بكفاءة عالية عند الأحمال الجزئية طوال اليوم.",
    "A central plant feeding an air-handling unit and ducted distribution.":
        "محطة مركزية تغذي وحدة مناولة هواء وتوزيعًا بقنوات.",

    # -------------------------------------------------------------- answer
    "What the space needs": "ما تحتاجه المساحة",
    "The answer": "الإجابة",
    "One calculation gives both the cooling duty and the most sensible way to deliver it. The recommendation follows size, space type and climate, and keeps a visible safety margin.":
        "حساب واحد يعطي حمل التبريد وأنسب طريقة لتأديته معًا. تتبع التوصية الحجم ونوع المساحة والمناخ، وتُبقي هامش أمان ظاهرًا.",
    "Required cooling": "التبريد المطلوب",
    "{tr:.1f} TR · includes outdoor-air ventilation":
        "{tr:.1f} طن تبريد · يشمل تهوية الهواء الخارجي",
    "Peak coil load at the design condition: room sensible and latent gains plus the fresh-air load.":
        "ذروة حمل الملف عند ظرف التصميم: مكاسب الغرفة المحسوسة والكامنة مضافًا إليها حمل الهواء النقي.",
    "Recommended system": "النظام الموصى به",
    "Rule-based selection from the cooling duty, the space type and the daily operating pattern.":
        "اختيار قائم على قواعد من حمل التبريد ونوع المساحة ونمط التشغيل اليومي.",
    "Installed capacity": "السعة المركبة",
    "{units} × {unit:.1f} kW · {margin:.0f}% above the load":
        "{units} × {unit:.1f} kW · {margin:.0f}% فوق الحمل",
    "Nominal equipment sizes rounded up to the nearest standard unit, including the selection margin.":
        "أحجام المعدات الاسمية مقربة صعودًا إلى أقرب وحدة قياسية، شاملة هامش الاختيار.",
    "Supply airflow": "تدفق هواء الإمداد",
    "Fresh air {oa:,.0f} m³/h · supply ΔT {dt:.0f} K":
        "هواء نقي {oa:,.0f} م³/ساعة · فرق حرارة الإمداد {dt:.0f} K",
    "Airflow from the sensible duty and a practical supply-to-room temperature difference.":
        "التدفق مشتق من الحمل المحسوس وفرق حرارة عملي بين الإمداد والغرفة.",
    "Outdoor air": "الهواء الخارجي",
    "Design day": "يوم التصميم",

    # ------------------------------------------------------------ recommendation
    "{n} outdoor units": "{n} وحدة خارجية",
    "kW installed": "kW مركبة",
    "{margin:.0f}% above the load": "{margin:.0f}% فوق الحمل",
    "Cooling load": "حمل التبريد",
    "Outdoor units": "الوحدات الخارجية",
    "Indoor units": "الوحدات الداخلية",
    "Unit size": "حجم الوحدة",
    "Nominal capacity": "السعة الاسمية",
    "Fresh air": "الهواء النقي",
    "Supply ΔT": "فرق حرارة الإمداد",
    "Rated COP": "COP الاسمي",
    "Selection margin": "هامش الاختيار",
    "Why this system": "لماذا هذا النظام",
    "Before you buy": "قبل الشراء",

    # ------------------------------------------------ live recommendation text
    "The peak coil load is {q:.1f} kW ({tr:.1f} TR), and this selection covers it with a {margin:.0f}% margin for duct gain, fan heat and real-world tolerance.":
        "ذروة حمل الملف {q:.1f} kW ({tr:.1f} TR)، ويغطيها هذا الاختيار بهامش {margin:.0f}% لمكاسب القنوات وحرارة المراوح والتفاوت الواقعي.",
    "A single-zone split is the simplest and lowest-cost answer at this size; shade the outdoor unit and keep the indoor unit clear of the bed and seating.":
        "السبليت لمنطقة واحدة هو الحل الأبسط والأقل تكلفة عند هذا الحجم؛ ظلّل الوحدة الخارجية وأبقِ الوحدة الداخلية بعيدة عن السرير والجلوس.",
    "The space is open-plan, so a ducted system distributes air evenly and can carry a fresh-air duct into the occupied zone.":
        "المساحة مفتوحة، لذا يوزع النظام بالقنوات الهواء بالتساوي ويمكنه إيصال قناة هواء نقي إلى منطقة الإشغال.",
    "Several rooms and a long operating day favour VRF: zoned indoor units track occupancy and part-load efficiency stays high outside the peak.":
        "تعدد الغرف وطول يوم التشغيل يفضلان VRF: تتبع الوحدات الداخلية المقسمة الإشغال وتبقى الكفاءة عند الأحمال الجزئية عالية خارج الذروة.",
    "At this capacity a central chilled-water plant and an AHU are more practical and serviceable than a large bank of DX units.":
        "عند هذه السعة تكون محطة الماء المبرد المركزية ووحدة مناولة الهواء أعملي وأسهل صيانة من مجموعة كبيرة من وحدات التكييف المباشر.",
    "Latent heat is {latent:.0f}% of the load, so choose a coil that genuinely dehumidifies; an oversized dry unit would leave the space cold and clammy.":
        "الحمل الكامن يشكل {latent:.0f}% من الحمل، لذا اختر ملفًا ينزع الرطوبة فعليًا؛ فالوحدة الجافة المفرطة الحجم ستترك المكان باردًا ورطبًا.",
    "The load is mostly sensible at {latent:.0f}% latent, so sensible capacity and airflow set the selection rather than dehumidification.":
        "الحمل محسوس في معظمه بنسبة كامنة {latent:.0f}%، لذا تحدد السعة المحسوسة والتدفق الاختيار أكثر من نزع الرطوبة.",
    "Glazing is {wwr:.0f}% of the exposed wall, so solar gain dominates; low-e glass or external shading buys more comfort than extra capacity.":
        "الزجاج يشكل {wwr:.0f}% من الجدار المعرض، لذا يهيمن الكسب الشمسي؛ والزجاج منخفض الانبعاثية أو التظليل الخارجي يشتري راحة أكبر من سعة إضافية.",
    "A west-facing main window puts the solar peak in the late afternoon, when the outdoor air is already hottest. That is the hour the system must win.":
        "النافذة الرئيسية المواجهة للغرب تضع ذروة الشمس في آخر العصر، حين يكون الهواء الخارجي في أشد حرارته. تلك هي الساعة التي يجب أن يكسبها النظام.",
    "Fresh air is {oa:.0f} m³/h. Confirm the ventilation and exhaust schedule with the people who will use the space.":
        "الهواء النقي {oa:.0f} م³/ساعة. أكّد جدول التهوية والعادم مع من سيستخدمون المساحة.",
    "Keep the outdoor unit shaded and clear of walls; a hot condenser can lose 10% of capacity exactly when you need it.":
        "أبقِ الوحدة الخارجية مظللة وبعيدة عن الجدران؛ فالمكثف الساخن قد يفقد 10% من سعته في اللحظة التي تحتاجها فيها.",
    "This is a design estimate. Final equipment selection must be checked by a qualified engineer against the project brief and local code.":
        "هذا تقدير تصميمي. يجب أن يتحقق مهندس مؤهل من اختيار المعدات النهائي وفق موجز المشروع والكود المحلي.",

    # ------------------------------------------------------------ simulation
    "The hottest day, hour by hour": "أحر يوم، ساعةً بساعة",
    "Design-day simulation": "محاكاة يوم التصميم",
    "The recommended system is put through a full design day: a sine-shaped outdoor temperature, orientation-specific solar gain, the real occupancy schedule and a capacity-limited controller. Scrub the day and watch the room, the load and the meter.":
        "يُختبر النظام الموصى به خلال يوم تصميم كامل: حرارة خارجية بشكل جيبي، وكسب شمسي حسب اتجاه الواجهة، وجدول إشغال حقيقي، ومتحكم محدود السعة. حرّك اليوم وراقب الغرفة والحمل والعداد.",
    "Choose an hour to inspect. The scene, the four readings and the hourly table all follow the same time step.":
        "اختر ساعة للفحص. المشهد والقراءات الأربع والجدول الساعي تتبع الخطوة الزمنية نفسها.",
    "Scrub through the day": "تنقّل خلال اليوم",
    "Every reading below is sampled at the chosen hour of the simulated design day.":
        "تُؤخذ كل قراءة أدناه عند الساعة المختارة من يوم التصميم المحاكى.",
    "Night": "ليل",
    "Dawn": "فجر",
    "Daylight": "نهار",
    "Dusk": "غسق",
    "System off · night setback": "النظام متوقف · خفض ليلي",
    "Comfort held inside the band": "الراحة محققة داخل النطاق",
    "Cooling, but humidity is outside the band": "تبريد، لكن الرطوبة خارج النطاق",
    "Pulling the room back to setpoint": "إعادة الغرفة إلى نقطة الضبط",
    "Outside": "الخارج",
    "Inside": "الداخل",
    "Design day · {city}": "يوم التصميم · {city}",
    "Outdoor dry-bulb temperature at the selected hour, following the design-day swing.":
        "درجة الحرارة الجافة الخارجية عند الساعة المختارة وفق تفاوت يوم التصميم.",
    "Room temperature": "حرارة الغرفة",
    "Setpoint {sp:.1f} °C · RH {rh:.0f}%": "نقطة الضبط {sp:.1f} °C · رطوبة {rh:.0f}%",
    "Zone dry-bulb temperature after the thermal capacitance and the controller response.":
        "درجة حرارة المنطقة الجافة بعد السعة الحرارية واستجابة المتحكم.",
    "Cooling delivered": "التبريد المسلّم",
    "{pct:.0f}% of installed capacity": "{pct:.0f}% من السعة المركبة",
    "Total coil duty at this instant, split between sensible and latent removal.":
        "حمل الملف الكلي في هذه اللحظة، موزعًا بين الإزالة المحسوسة والكامنة.",
    "Electric demand": "الطلب الكهربائي",
    "Compressor and fan": "الضاغط والمروحة",
    "Compressor power after the ambient and part-load corrections, plus the fan share.":
        "قدرة الضاغط بعد تصحيحات المحيط والحمل الجزئي، مضافًا إليها حصة المروحة.",
    "Peak load": "ذروة الحمل",
    "{kw:.1f} kW at {hour:02d}:00": "{kw:.1f} kW عند {hour:02d}:00",
    "Comfort while occupied": "الراحة أثناء الإشغال",
    "Electricity": "الكهرباء",
    "Day COP": "COP اليوم",
    "System on": "تشغيل النظام",
    "Five views of the same day": "خمسة مشاهد لليوم نفسه",
    "Charts": "المخططات",
    "Temperature and control first, then the cooling duty, the gains that create it, the moisture result and the electricity that pays for it.":
        "الحرارة والتحكم أولًا، ثم حمل التبريد، والمكاسب التي تصنعه، ونتيجة الرطوبة، والكهرباء التي تدفع ثمنه.",
    "Hour-by-hour results and export": "النتائج الساعية والتصدير",
    "Download the 24-hour simulation (CSV)": "تنزيل محاكاة 24 ساعة (CSV)",
    "Every hourly sample with temperatures, cooling, capacity, electricity and comfort flags.":
        "كل عينة ساعية مع الحرارات والتبريد والسعة والكهرباء ومؤشرات الراحة.",
    "What the day is telling you": "ما يقوله لك اليوم",
    "The room spends about {hours:.1f} hour(s) more than 0.5 K above setpoint while occupied. That is the honest limit of the installed capacity, not a calculation error. Extra capacity, better glazing or a tighter schedule would close the gap.":
        "تقضي الغرفة نحو {hours:.1f} ساعة أعلى من نقطة الضبط بأكثر من 0.5 K أثناء الإشغال. هذا حد السعة المركبة بصدق، وليس خطأ حسابيًا. سعة إضافية أو زجاج أفضل أو جدول أكثر إحكامًا ستغلق الفجوة.",
    "The selected system holds the room at setpoint through every occupied hour, with {headroom:.0f}% headroom at the peak. The morning ramp and the night setback are visible in the temperature chart: that is the thermal inertia of the room, not a control fault.":
        "يحافظ النظام المختار على الغرفة عند نقطة الضبط خلال كل ساعة إشغال، بهامش {headroom:.0f}% عند الذروة. ويظهر صعود الصباح والخفض الليلي في مخطط الحرارة: ذلك هو القصور الحراري للغرفة وليس عطلًا في التحكم.",
    "How this simulation works": "كيف تعمل هذه المحاكاة",
    "**The load.** Six answers are expanded into the full Chapter-4 input set: geometry from the floor area, occupancy and internal gains from the space type, and envelope values from the build quality. The same engine as Module 1 calculates the peak.":
        "**الحمل.** تُوسَّع الإجابات الست إلى مجموعة مدخلات الفصل 4 الكاملة: الأشكال من مساحة الأرضية، والإشغال والمكاسب الداخلية من نوع المساحة، وقيم الغلاف من جودة البناء. ويحسب المحرك نفسه المستخدم في الوحدة 1 الذروة.",
    "**The day.** Outdoor dry bulb follows a sine that peaks at 15:00, solar gain follows the main window orientation, and the selected system modulates against its installed capacity. The room has thermal and moisture inertia, so morning pull-down, night setback and the afternoon peak all emerge from the model.":
        "**اليوم.** تتبع الحرارة الجافة الخارجية منحنى جيبيًا يبلغ ذروته عند 15:00، ويتبع الكسب الشمسي اتجاه النافذة الرئيسية، ويكيّف النظام المختار قدرته مقابل سعته المركبة. وللغرفة قصور حراري ورطوبي، لذا ينشأ سحب الصباح والخفض الليلي وذروة العصر من النموذج.",
    "**The limits.** This is a single-zone teaching model with a fixed coil sensible heat ratio and a simple ambient COP correction. It is not an hourly energy-compliance simulation. Use it to understand behaviour, then confirm the design with the detailed modules.":
        "**الحدود.** هذا نموذج تعليمي لمنطقة واحدة بنسبة حرارة محسوسة ثابتة للملف وتصحيح مبسط لـ COP حسب المحيط. وهو ليس محاكاة ساعية للامتثال الطاقي. استخدمه لفهم السلوك، ثم أكّد التصميم بالوحدات التفصيلية.",
    "Open the detailed cooling-load module": "افتح وحدة حمل التبريد التفصيلية",
    "Recalculate the same case from every envelope, solar and occupancy input.":
        "أعد حساب الحالة نفسها من كل مدخلات الغلاف والشمس والإشغال.",
    "Open the psychrometric AHU module": "افتح وحدة مناولة الهواء السيكرومترية",
    "See the coil process, apparatus dew point and bypass factor for this air state.":
        "شاهد عملية الملف ونقطة الندى الظاهرية وعامل التجاوز لحالة الهواء هذه.",

    # ----------------------------------------------------------------- charts
    "Total cooling": "إجمالي التبريد",
    "Sensible cooling": "التبريد المحسوس",
    "Installed capacity": "السعة المركبة",
    "Pre-cool pull-down": "سحب التبريد المسبق",
    "Envelope": "الغلاف",
    "Solar through glass": "الشمس عبر الزجاج",
    "People, lighting, equipment": "الأشخاص والإضاءة والمعدات",
    "Outdoor-air ventilation": "تهوية الهواء الخارجي",
    "Room RH": "رطوبة الغرفة",
    "30-70% comfort band": "نطاق الراحة 30–70%",
    "Electric demand": "الطلب الكهربائي",
    "Rated COP": "COP الاسمي",
    "Hour": "الساعة",
    "Cooling (kW)": "التبريد (kW)",
    "Sensible gain (kW)": "الكسب المحسوس (kW)",
    "Electric demand (kW)": "الطلب الكهربائي (kW)",
    "COP (-)": "COP (–)",
    "Outdoor %{y:.1f} degC<extra></extra>": "الخارج %{y:.1f} °C<extra></extra>",
    "Room %{y:.2f} degC<extra></extra>": "الغرفة %{y:.2f} °C<extra></extra>",
    "Setpoint %{y:.1f} degC<extra></extra>": "نقطة الضبط %{y:.1f} °C<extra></extra>",
    "Sensible %{y:.2f} kW<extra></extra>": "محسوس %{y:.2f} kW<extra></extra>",
    "Total %{y:.2f} kW<extra></extra>": "الإجمالي %{y:.2f} kW<extra></extra>",
    "Capacity %{y:.1f} kW<extra></extra>": "السعة %{y:.1f} kW<extra></extra>",
    "Envelope %{y:.2f} kW<extra></extra>": "الغلاف %{y:.2f} kW<extra></extra>",
    "Solar through glass %{y:.2f} kW<extra></extra>":
        "الشمس عبر الزجاج %{y:.2f} kW<extra></extra>",
    "People, lighting, equipment %{y:.2f} kW<extra></extra>":
        "الأشخاص والإضاءة والمعدات %{y:.2f} kW<extra></extra>",
    "Ventilation %{y:.2f} kW<extra></extra>": "التهوية %{y:.2f} kW<extra></extra>",
    "RH %{y:.1f}%<extra></extra>": "الرطوبة %{y:.1f}%<extra></extra>",
    "%{x:.0f}:00 · %{y:.2f} kW<extra></extra>": "%{x:.0f}:00 · %{y:.2f} kW<extra></extra>",
    "Rated COP %{y:.2f}<extra></extra>": "COP الاسمي %{y:.2f}<extra></extra>",
    "kWh/day": "kWh/يوم",

    # ---------------------------------------------------------------- tables
    "Outdoor DB (degC)": "الخارج جافة (°C)",
    "Room DB (degC)": "الغرفة جافة (°C)",
    "Setpoint (degC)": "نقطة الضبط (°C)",
    "RH (%)": "الرطوبة (%)",
    "Capacity (kW)": "السعة (kW)",
    "Occupied": "مشغول",
    "Comfortable": "مريح",
    "Yes": "نعم",
    "No": "لا",
}

OPTION_LABELS: dict[str, str] = {
    "Design & simulation": "التصميم والمحاكاة",
    "Apartment living room": "غرفة معيشة في شقة",
    "Office": "مكتب",
    "Classroom": "صف دراسي",
    "Retail shop": "متجر تجزئة",
    "Restaurant / café": "مطعم / مقهى",
    "Mosque / assembly hall": "مسجد / قاعة اجتماعات",
    "Clinic / laboratory": "عيادة / مختبر",
    "Baghdad": "بغداد",
    "Basra": "البصرة",
    "Mosul": "الموصل",
    "Erbil": "أربيل",
    "Najaf": "النجف",
    "Other / custom": "أخرى / مخصص",
    "North": "شمال",
    "East": "شرق",
    "South": "جنوب",
    "West": "غرب",
    "Basic (older building)": "أساسي (مبنى قديم)",
    "Standard": "معياري",
    "High performance": "عالي الأداء",
    "Auto (recommended)": "تلقائي (موصى به)",
    "High-wall split units": "وحدات سبليت جدارية",
    "Ducted packaged units": "وحدات مجمعة بقنوات",
    "VRF multi-split": "نظام VRF متعدد السبليت",
    "Air-cooled chiller + AHU": "مبرد ماء بالهواء + وحدة مناولة هواء",
    "Single-zone DX": "تكييف مباشر لمنطقة واحدة",
    "Ducted DX": "تكييف مباشر بقنوات",
    "Variable-refrigerant flow": "تدفق مبرد متغير",
    "Central chilled water": "ماء مبرد مركزي",
}

PATTERNS: list[tuple[str, str]] = [
    (r"Peak (\d{2}):00", r"الذروة \1:00"),
    (r"([\d.]+) kWh/day", r"\1 kWh/يوم"),
]
