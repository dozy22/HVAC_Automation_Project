# -*- coding: utf-8 -*-
"""Arabic copy for Module 3 — the vapour-compression refrigeration cycle."""

TRANSLATIONS: dict[str, str] = {
    "Vapour-compression": "دورة الانضغاط البخاري",
    "refrigeration": "للتبريد",
    "Vapour-compression refrigeration": "دورة الانضغاط البخاري للتبريد",
    "Chapter 8 · Refrigeration cycles": "الفصل 8 · دورات التبريد",
    "Fluids": "الموائع",
    "Library": "المكتبة",
    "CoolProp real-fluid states": "حالات الموائع الحقيقية بـ CoolProp",
    "Outputs": "المخرجات",
    "Evaluate a real-fluid cycle from evaporator to condenser: capacity in kW and tons, compressor power, COP, refrigerant mass flow, pressure ratio, superheat and subcooling. Every state is solved with CoolProp equations of state.":
        "قيّم دورة بمائع حقيقي من المبخر إلى المكثف: السعة بالكيلوواط والأطنان، وقدرة الضاغط، وCOP، والتدفق الكتلي للمبرد، ونسبة الضغط، والتسخين والتبريد الفائقين. تُحل كل حالة بمعادلات حالة CoolProp.",
    "Cycle specification": "مواصفات الدورة",
    "Design point": "نقطة التصميم",
    "Refrigerant": "المبرد",
    "R134a is the classroom baseline; R410A and R32 are common in modern packaged equipment.":
        "R134a هو الأساس الصفي، وR410A وR32 شائعان في المعدات المجمعة الحديثة.",
    "Evaporating temperature (°C)": "حرارة التبخر (°C)",
    "Condensing temperature (°C)": "حرارة التكثيف (°C)",
    "Suction superheat (K)": "التسخين الفائق للشفط (K)",
    "Liquid subcooling (K)": "التبريد الفائق للسائل (K)",
    "Isentropic efficiency (–)": "الكفاءة الأيزونتروبية (–)",
    "Size cycle from connected system load": "حدد الدورة من حمل المنظومة المتصلة",
    "Cooling capacity (kW)": "سعة التبريد (kW)",
    "Saturation temperature in the evaporator. Lower values increase the temperature lift.":
        "حرارة التشبع في المبخر. القيم الأقل تزيد فرق الحرارة.",
    "Saturation temperature in the condenser. Must stay above the evaporating temperature.":
        "حرارة التشبع في المكثف. يجب أن تبقى أعلى من حرارة التبخر.",
    "Temperature rise above the evaporating saturation temperature at compressor suction.":
        "ارتفاع الحرارة فوق حرارة تشبع التبخر عند شفط الضاغط.",
    "Liquid temperature drop below condensing saturation before the expansion valve.":
        "انخفاض حرارة السائل تحت تشبع التكثيف قبل صمام التمدد.",
    "Ratio of isentropic compression work to actual compressor work.":
        "نسبة شغل الانضغاط الأيزونتروبي إلى شغل الضاغط الفعلي.",
    "Imports the current coil load from Module 2, or the Module 1 design load if no AHU result exists.":
        "يستورد حمل الملف الحالي من الوحدة 2، أو حمل تصميم الوحدة 1 إن لم توجد نتيجة لوحدة مناولة الهواء.",
    "Independent refrigeration capacity for cycle studies.":
        "سعة تبريد مستقلة لدراسات الدورة.",
    "Source:": "المصدر:",
    "Cooling delivered at the evaporator. One ton of refrigeration equals 3.5169 kW.":
        "التبريد المسلّم عند المبخر. طن التبريد الواحد يساوي 3.5169 kW.",
    "COP = refrigeration effect ÷ compressor work for the real cycle with isentropic efficiency.":
        "COP = تأثير التبريد ÷ شغل الضاغط للدورة الحقيقية بالكفاءة الأيزونتروبية.",
    "Actual electrical-equivalent shaft power implied by the isentropic efficiency.":
        "قدرة عمود مكافئة كهربائيًا كما توحي الكفاءة الأيزونتروبية.",
    "Mass flow needed to deliver the stated capacity with the computed enthalpy difference.":
        "التدفق الكتلي اللازم لتسليم السعة المحددة بفرق الإنثالبي المحسوب.",
    "Fluid": "المائع",
    "Evaporator": "المبخر",
    "Condenser": "المكثف",
    "Superheat": "التسخين الفائق",
    "Subcooling": "التبريد الفائق",
    "η isentropic": "η الأيزونتروبية",
    "Keep the condensing temperature at least 3 K above evaporating, stay below the refrigerant critical temperature, and use a valid capacity.":
        "أبقِ حرارة التكثيف أعلى من التبخر بـ 3 K على الأقل، وابقَ تحت الحرارة الحرجة للمبرد، واستخدم سعة صالحة.",
    "Condenser rejection": "طرد المكثف",
    "Discharge temperature": "حرارة الطرد",
    "Second-law efficiency": "كفاءة القانون الثاني",
    "Volumetric capacity": "السعة الحجمية",
    "Cooling load + compressor work": "حمل التبريد + شغل الضاغط",
    "Heat rejected at the condenser, equal to evaporator duty plus compressor power in steady state.":
        "الحرارة المطرودة عند المكثف، وتساوي حمل المبخر مضافًا إليه قدرة الضاغط في الحالة المستقرة.",
    "Real compressor discharge temperature after applying the isentropic efficiency.":
        "حرارة طرد الضاغط الفعلية بعد تطبيق الكفاءة الأيزونتروبية.",
    "Real COP ÷ Carnot COP at the same temperatures":
        "COP الفعلي ÷ COP كارنو عند الحرارتين نفسيهما",
    "How closely the real cycle approaches the reversible Carnot limit between the saturation temperatures.":
        "مدى اقتراب الدورة الحقيقية من حد كارنو العكوس بين حرارتي التشبع.",
    "Refrigeration effect per cubic metre of suction vapour; it links capacity to compressor displacement.":
        "تأثير التبريد لكل متر مكعب من بخار الشفط؛ يربط السعة بإزاحة الضاغط.",
    "Pressure–enthalpy cycle": "دورة الضغط–الإنثالبي",
    "Real-fluid diagram": "مخطط المائع الحقيقي",
    "The subcritical saturation dome is drawn from CoolProp saturation data. State 2 is the actual discharge; 2s is the ideal isentropic endpoint.":
        "تُرسم قبة التشبع دون الحرجة من بيانات تشبع CoolProp. الحالة 2 هي الطرد الفعلي، و2s هي النهاية الأيزونتروبية المثالية.",
    "Cycle state points": "نقاط حالة الدورة",
    "Performance summary": "ملخص الأداء",
    "At design capacity": "عند سعة التصميم",
    "Download cycle states (CSV)": "تنزيل حالات الدورة (CSV)",
    "Download cycle performance (CSV)": "تنزيل أداء الدورة (CSV)",
    "Measured model superheat is": "التسخين الفائق المقاس في النموذج هو",
    "K and subcooling is": "K والتبريد الفائق هو",
    "Subcooling buys refrigeration effect after the condenser; suction superheat protects the compressor but lowers suction density and raises discharge temperature.":
        "يزيد التبريد الفائق تأثير التبريد بعد المكثف؛ ويحمي التسخين الفائق للشفط الضاغط لكنه يخفض كثافة الشفط ويرفع حرارة الطرد.",
    "The compressor rejects": "يطرد الضاغط",
    "kW at the condenser and requires": "kW عند المكثف ويحتاج إلى",
    "of": "من",
    "At design capacity": "عند سعة التصميم",
    "Superheat and subcooling sensitivity": "حساسية التسخين والتبريد الفائقين",
    "Cycle diagnostics": "تشخيص الدورة",
    "Hold the evaporating and condensing temperatures fixed and sweep one degree-of-superheat variable. The amber marker is the current design point.":
        "ثبّت حرارتي التبخر والتكثيف وغيّر متغيرًا واحدًا للتسخين أو التبريد الفائق. العلامة الكهرمانية هي نقطة التصميم الحالية.",
    "Sweep variable": "متغير الدراسة",
    "Subcooling acts on the liquid line; superheat acts on the suction vapour.":
        "يؤثر التبريد الفائق في خط السائل؛ ويؤثر التسخين الفائق في بخار الشفط.",
    "Subcooling (K)": "التبريد الفائق (K)",
    "Superheat (K)": "التسخين الفائق (K)",
    "0–25 K": "0–25 K",
    "Compressor kW": "الضاغط kW",
    "Mass flow kg/s": "التدفق الكتلي kg/s",
    "Discharge temperature C": "حرارة الطرد C",
    "Discharge °C": "الطرد °C",
    "Raising subcooling from": "رفع التبريد الفائق من",
    "changes COP by": "يغيّر COP بمقدار",
    "and refrigerant mass flow by": "والتدفق الكتلي للمبرد بمقدار",
    "Subcooling lowers the expansion-inlet enthalpy, so the evaporator produces more refrigeration per kilogram without changing the compressor pressure ratio.":
        "يخفض التبريد الفائق إنثالبي دخول صمام التمدد، فينتج المبخر تبريدًا أكثر لكل كيلوغرام دون تغيير نسبة ضغط الضاغط.",
    "Raising superheat from": "رفع التسخين الفائق من",
    "and discharge temperature from": "وحرارة الطرد من",
    "Useful superheat protects the compressor from liquid slugs, but excessive suction superheat lowers suction density and increases discharge temperature.":
        "يحمي التسخين الفائق المفيد الضاغط من كتل السائل، لكن التسخين الفائق الزائد للشفط يخفض كثافة الشفط ويرفع حرارة الطرد.",
    "Screen all refrigerants at this operating point": "افحص كل المبردات عند نقطة التشغيل هذه",
    "Same saturation temperatures, superheat, subcooling and isentropic efficiency. This screening compares thermodynamics only; flammability, GWP, lubricant and safety classification must be assessed separately.":
        "الحرارتان نفساهما للتشبع والتسخين والتبريد الفائقان والكفاءة الأيزونتروبية. تقارن هذه الفرزية الترموديناميك فقط؛ ويجب تقييم الاشتعالية وقيمة GWP والزيت وتصنيف السلامة بصورة منفصلة.",
    "Run the six-fluid comparison": "شغّل مقارنة الموائع الستة",
    "Computes each supported refrigerant at the current evaporating and condensing temperatures.":
        "يحسب كل مبرد مدعوم عند حرارتي التبخر والتكثيف الحاليتين.",
    "Download refrigerant screening (CSV)": "تنزيل فرز المبردات (CSV)",
    "Cycle equations and modelling assumptions": "معادلات الدورة وافتراضات النمذجة",
    "State 1 is superheated suction vapour, 2 is actual discharge, 3 is subcooled liquid at condenser pressure, and 4 is the isenthalpic expansion outlet.":
        "الحالة 1 بخار شفط مسخّن فائقًا، والحالة 2 الطرد الفعلي، والحالة 3 سائل مبرّد فائقًا عند ضغط المكثف، والحالة 4 مخرج التمدد متساوي الإنثالبي.",
    "Temperatures in the Carnot expression are absolute. Compressor, piping and motor losses beyond the entered isentropic efficiency are not modelled. Heat rejection assumes steady state with no ambient losses.":
        "الحرارات في تعبير كارنو مطلقة. لا تُنمذج خسائر الضاغط والأنابيب والمحرك خارج الكفاءة الأيزونتروبية المدخلة. ويفترض طرد الحرارة حالة مستقرة دون فقد إلى المحيط.",
    "Specific refrigeration effect": "تأثير التبريد النوعي",
    "Refrigerant mass flow": "التدفق الكتلي للمبرد",
    "Volumetric refrigeration effect": "تأثير التبريد الحجمي",
    "Coefficient of performance": "معامل الأداء",
    "Carnot COP": "COP كارنو",
    "Pressure ratio": "نسبة الضغط",
    "Compressor discharge temperature": "حرارة طرد الضاغط",
    "Try a less extreme liquid or suction condition.":
        "جرّب حالة سائل أو شفط أقل تطرفًا.",
    "Compressor power": "قدرة الضاغط",
    "Cooling capacity": "سعة التبريد",
    "Mass flow (kg/s)": "التدفق الكتلي (kg/s)",
    "Compressor (kW)": "الضاغط (kW)",
    "Discharge (°C)": "الطرد (°C)",
    "tons of refrigeration": "طن تبريد",
    "Carnot limit": "حد كارنو",
    "Specific effect": "التأثير النوعي",
    "Download cycle states (CSV)": "تنزيل حالات الدورة (CSV)",
}
