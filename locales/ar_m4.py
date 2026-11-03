# -*- coding: utf-8 -*-
"""Arabic copy for Module 4 — comfort and closed-loop control."""

TRANSLATIONS: dict[str, str] = {
    "Automatic control & smart comfort": "التحكم الآلي والراحة الذكية",
    "Chapters 3 & 11 · Comfort & control": "الفصلان 3 و11 · الراحة والتحكم",
    "Comfort under": "الراحة تحت",
    "automatic control": "التحكم الآلي",
    "Comfort under automatic control": "الراحة تحت التحكم الآلي",
    "Controllers": "المتحكمات",
    "PID & threshold hysteresis": "PID وعتبة مع تباطؤ",
    "Actuators": "المشغلات",
    "Chilled-water valve · SA temperature": "صمام الماء المبرد · حرارة هواء الإمداد",
    "Comfort test": "فحص الراحة",
    "ET* proxy + 30–70% RH": "بديل ET* + رطوبة 30–70%",
    "Close the loop on a reduced-order zone. A PID or threshold controller commands either a chilled-water valve or a supply-air temperature to hold effective temperature and relative humidity inside the acceptance band.":
        "أغلق الحلقة على منطقة مبسطة الرتبة. يأمر متحكم PID أو العتبة إما صمام ماء مبرد أو حرارة هواء إمداد للحفاظ على درجة الحرارة الفعالة والرطوبة النسبية داخل نطاق القبول.",
    "Zone": "المنطقة",
    "96 m² classroom · 307 m³": "صف بمساحة 96 m² · 307 m³",
    "Plant": "المنظومة",
    "10 kW rated sensible demo coil": "ملف عرض محسوس مقنن 10 kW",
    "COP source": "مصدر COP",
    "Module 3 ·": "الوحدة 3 ·",
    "default 3.20": "افتراضي 3.20",
    "Model": "النموذج",
    "Reduced-order energy & moisture balance": "موازنة طاقة ورطوبة مبسطة الرتبة",
    "The loop is a teaching model, not an equipment selection. Rated capacity is sensible; the wet-coil model removes latent heat separately, so the instantaneous total cooling demand can exceed the rated sensible value.":
        "الحلقة نموذج تعليمي وليست اختيار معدات. السعة المقننة محسوسة؛ ويزيل نموذج الملف المبلل الحرارة الكامنة منفصلة، لذا قد يتجاوز طلب التبريد الكلي اللحظي القيمة المحسوسة المقننة.",
    "Control specification": "مواصفات التحكم",
    "Closed loop": "حلقة مغلقة",
    "Controller": "المتحكم",
    "Actuator": "المشغل",
    "Weather scenario": "سيناريو الطقس",
    "Simulation duration (h)": "مدة المحاكاة (h)",
    "Cooling setpoint (°C)": "ضبط التبريد (°C)",
    "Rated sensible cooling capacity (kW)": "سعة التبريد المحسوسة المقننة (kW)",
    "Use COP from Module 3": "استخدم COP من الوحدة 3",
    "Plant COP (–)": "COP المنظومة (–)",
    "PID gains & switching band": "مكاسب PID ونطاق التبديل",
    "Comfort acceptance band": "نطاق قبول الراحة",
    "Zone and weather model": "نموذج المنطقة والطقس",
    "Imported from the refrigeration cycle in Module 3.":
        "مستورد من دورة التبريد في الوحدة 3.",
    "Total cooling divided by electrical input. A seasonal system COP is normally lower than a design-point cycle COP.":
        "إجمالي التبريد مقسومًا على المدخل الكهربائي. عادةً يكون COP الموسمي للمنظومة أقل من COP الدورة عند نقطة التصميم.",
    "PID modulates the actuator continuously. Threshold control switches between fully on and off with hysteresis.":
        "يعدّل PID المشغل باستمرار. أما تحكم العتبة فيبدّل بين التشغيل الكامل والإيقاف الكامل مع تباطؤ.",
    "The valve modulates coil capacity. The supply-air option adjusts the air temperature delivered to the zone.":
        "يعدّل الصمام سعة الملف. ويضبط خيار هواء الإمداد حرارة الهواء المسلّمة إلى المنطقة.",
    "Illustrative outdoor dry-bulb swing and humidity for the demonstration day.":
        "تغير توضيحي للحرارة الجافة الخارجية والرطوبة في يوم العرض.",
    "Sensible coil capacity at the design supply-to-room temperature difference. Latent removal is modelled separately.":
        "سعة الملف المحسوسة عند فرق حرارة التصميم بين الإمداد والغرفة. وتُنمذج إزالة الرطوبة منفصلة.",
    "Borrow the real-fluid cycle COP to convert delivered cooling into estimated electricity.":
        "استعِر COP دورة المائع الحقيقي لتحويل التبريد المسلّم إلى كهرباء مقدّرة.",
    "PID: error is room temperature minus setpoint. The output is bounded to 0–100% with conditional-integration anti-windup.":
        "PID: الخطأ هو حرارة الغرفة ناقص نقطة الضبط. ويُحصر الخرج بين 0–100% مع منع تراكم التكامل الشرطي.",
    "Threshold: the plant switches at setpoint ± half the deadband. Hysteresis prevents rapid short-cycling.":
        "العتبة: تتبدل المنظومة عند نقطة الضبط ± نصف النطاق الميت. يمنع التباطؤ التقصير السريع للدورة.",
    "Proportional gain Kp (%/K)": "المكسب التناسبي Kp (%/K)",
    "Integral gain Ki (%/K·s)": "المكسب التكاملي Ki (%/K·s)",
    "Derivative gain Kd (%·min/K)": "المكسب التفاضلي Kd (%·min/K)",
    "Switching deadband (K)": "النطاق الميت للتبديل (K)",
    "ET* minimum (°C)": "الحد الأدنى لـ ET* (°C)",
    "ET* maximum (°C)": "الحد الأعلى لـ ET* (°C)",
    "RH minimum (%)": "الحد الأدنى للرطوبة (%)",
    "RH maximum (%)": "الحد الأعلى للرطوبة (%)",
    "Outdoor mean DB (°C)": "متوسط الحرارة الجافة الخارجية (°C)",
    "Outdoor swing (±K)": "تأرجح الحرارة الخارجية (±K)",
    "Outdoor RH (%)": "الرطوبة النسبية الخارجية (%)",
    "Initial room DB (°C)": "حرارة الغرفة الابتدائية الجافة (°C)",
    "Initial room RH (%)": "الرطوبة النسبية الابتدائية للغرفة (%)",
    "Zone UA (kW/K)": "UA للمنطقة (kW/K)",
    "Zone capacitance (kJ/K)": "سعة المنطقة الحرارية (kJ/K)",
    "Zone volume (m³)": "حجم المنطقة (m³)",
    "Infiltration (ACH)": "التسرب (ACH)",
    "Internal sensible (kW)": "المحسوس الداخلي (kW)",
    "Internal latent (kW)": "الكامن الداخلي (kW)",
    "Length of the demonstration day. The comfort KPI uses the final half.":
        "طول يوم العرض. ويستخدم مؤشر الراحة النصف الأخير.",
    "Dry-bulb setpoint used by both controllers.": "حرارة الضبط الجافة التي يستخدمها المتحكمان.",
    "Immediate valve or supply-temperature response to temperature error.":
        "استجابة فورية للصمام أو حرارة الإمداد تجاه خطأ الحرارة.",
    "Removes steady-state offset. Too much integral action causes overshoot.":
        "يزيل الإزاحة المستقرة. الإجراء التكاملي الزائد يسبب تجاوزًا.",
    "Damps fast temperature change. The implementation differentiates the measurement.":
        "يخمد تغير الحرارة السريع. ويشتق التطبيق القياس.",
    "Total deadband around the setpoint. A wider band means fewer switch changes but larger temperature swings.":
        "النطاق الميت الكلي حول نقطة الضبط. النطاق الأوسع يعني تبديلات أقل وتأرجح حرارة أكبر.",
    "Lower effective-temperature acceptance limit.": "الحد الأدنى لقبول الحرارة الفعالة.",
    "Upper effective-temperature acceptance limit.": "الحد الأعلى لقبول الحرارة الفعالة.",
    "Project comfort criterion used as an acceptance gate.":
        "معيار راحة المشروع المستخدم كبوابة قبول.",
    "Mean outdoor dry bulb over the simulated day.": "متوسط الحرارة الجافة الخارجية خلال اليوم المحاكى.",
    "Half-amplitude of the sinusoidal outdoor dry-bulb profile, peaking around 15:00.":
        "نصف سعة الملف الجيبي للحرارة الجافة الخارجية، بذروة حول الساعة 15:00.",
    "Constant outdoor relative humidity used to compute ventilation moisture.":
        "الرطوبة النسبية الخارجية الثابتة المستخدمة لحساب رطوبة التهوية.",
    "Starting zone temperature at the beginning of pull-down.":
        "حرارة المنطقة الابتدائية عند بدء السحب.",
    "Starting zone relative humidity.": "الرطوبة النسبية الابتدائية للمنطقة.",
    "Overall envelope conductance to outdoor air.": "موصلية الغلاف الكلية تجاه الهواء الخارجي.",
    "Lumped thermal capacitance of the zone and its furnishings.":
        "السعة الحرارية المجمعة للمنطقة وأثاثها.",
    "Used for infiltration airflow and moisture capacitance.":
        "تُستخدم لتدفق هواء التسرب وسعة الرطوبة.",
    "Envelope leakage expressed as air changes per hour.":
        "تسرب الغلاف معبرًا عنه بعدد تغيرات الهواء في الساعة.",
    "People, lighting and equipment sensible gain retained in the reduced-order model.":
        "الكسب المحسوس للأشخاص والإضاءة والمعدات المحتفظ به في النموذج المبسط.",
    "People and equipment moisture gain.": "كسب الرطوبة من الأشخاص والمعدات.",
    "Comfort maintained": "الراحة المحققة",
    "Final half of the simulated day": "النصف الأخير من اليوم المحاكى",
    "Percentage of sampled control periods in the last half of the run that satisfy both ET* and RH criteria.":
        "نسبة فترات التحكم المأخوذة عيناتها في النصف الأخير من التشغيل التي تحقق معياري ET* والرطوبة معًا.",
    "Final room temperature": "حرارة الغرفة النهائية",
    "Zone dry-bulb temperature at the end of the simulated day.":
        "حرارة المنطقة الجافة عند نهاية اليوم المحاكى.",
    "Final relative humidity": "الرطوبة النسبية النهائية",
    "Delivered cooling": "التبريد المسلّم",
    "Integrated total coil cooling over the run. Electricity uses the selected plant COP.":
        "إجمالي تبريد الملف المكامل خلال التشغيل. وتُحسب الكهرباء بمعامل COP المختار للمنظومة.",
    "Overall comfort": "الراحة الإجمالية",
    "Thermal in band": "الحرارة ضمن النطاق",
    "RH in band": "الرطوبة ضمن النطاق",
    "Peak total coil": "ذروة الحمل الكلي للملف",
    "Estimated electricity": "الكهرباء المقدّرة",
    "Setpoint held within 0.25 K and comfort maintained.":
        "نقطة الضبط محفوظة ضمن 0.25 K والراحة محققة.",
    "Review the trajectory and acceptance band.":
        "راجع المسار ونطاق القبول.",
    "Peak total coil includes latent removal during pull-down and may exceed the rated sensible capacity. This is intentional in the reduced-order plant.":
        "تشمل ذروة الحمل الكلي للملف إزالة الحرارة الكامنة أثناء السحب وقد تتجاوز السعة المحسوسة المقننة. وهذا مقصود في المنظومة المبسطة.",
    "Check that the setpoint exceeds the minimum supply temperature, comfort limits are ordered correctly, and zone properties are positive.":
        "تحقق من أن نقطة الضبط تتجاوز أدنى حرارة إمداد، وأن حدود الراحة مرتبة صحيحًا، وأن خصائص المنطقة موجبة.",
    "Comfort last half (%)": "الراحة في النصف الأخير (%)",
    "Humidity in band (%)": "الرطوبة ضمن النطاق (%)",
    "Delivered cooling (kWh)": "التبريد المسلّم (kWh)",
    "Estimated electricity (kWh)": "الكهرباء المقدّرة (kWh)",
    "Switch changes": "مرات تبديل المشغل",
    "Comfort (%)": "الراحة (%)",
    "RH in band (%)": "الرطوبة ضمن النطاق (%)",
    "Cooling (kWh)": "التبريد (kWh)",
    "Electricity (kWh)": "الكهرباء (kWh)",
    "Switches": "مرات التبديل",
    "Comfort definition, control logic and model limits": "تعريف الراحة ومنطق التحكم وحدود النموذج",
    "Comfort policy is explicitly educational. For a real design, document the chosen standard, activity, clothing and local code requirements.":
        "سياسة الراحة تعليمية صراحةً. للتصميم الحقيقي، وثّق المعيار المختار والنشاط والملبس ومتطلبات الكود المحلي.",
    "The demonstration plant is deliberately smaller than the 19 kW peak design case. It exposes controller behaviour and pull-down dynamics without implying that a 10 kW coil is the selected equipment.":
        "المنظومة التوضيحية أصغر عمدًا من حالة التصميم ذات الذروة 19 kW. وهي تُظهر سلوك المتحكم وديناميكية السحب دون الإيحاء بأن ملف 10 kW هو المعدة المختارة.",
    "A day under closed-loop control": "يوم تحت التحكم بحلقة مغلقة",
    "Control timeline": "الخط الزمني للتحكم",
    "Temperature, humidity and effective temperature share the same clock. Green bands are the acceptance criteria; the dashed line is the temperature setpoint.":
        "تشارك الحرارة والرطوبة والحرارة الفعالة الساعة نفسها. النطاقات الخضراء معايير القبول؛ والخط المتقطع هو نقطة ضبط الحرارة.",
    "Actuator command": "أمر المشغل",
    "Comfort trajectory": "مسار الراحة",
    "ET* vs RH": "ET* مقابل الرطوبة",
    "PID versus threshold": "PID مقابل العتبة",
    "Controller comparison": "مقارنة المتحكمات",
    "Both controllers run on the same weather, zone and actuator. The useful comparison is stability and actuator wear, not a guaranteed energy saving in this simplified plant.":
        "يعمل المتحكمان على الطقس والمنطقة والمشغل نفسها. المقارنة المفيدة هي الاستقرار وبلى المشغل، لا توفير طاقة مضمون في هذه المنظومة المبسطة.",
    "Download control time series (CSV)": "تنزيل السلسلة الزمنية للتحكم (CSV)",
    "Download controller comparison (CSV)": "تنزيل مقارنة المتحكمات (CSV)",
    "Comfort check: the ET* minimum must be below the ET* maximum.":
        "فحص الراحة: يجب أن يكون الحد الأدنى لـ ET* أقل من الحد الأعلى.",
    "Comfort check: the RH minimum must be below the RH maximum.":
        "فحص الراحة: يجب أن يكون الحد الأدنى للرطوبة أقل من الحد الأعلى.",
}
