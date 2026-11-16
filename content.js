/*
  ==========================================================================
  SITE CONTENT: this is the only file you need to edit to change the text.
  ==========================================================================

  How to edit:
    * Change only the text between the quote marks "like this".
    * Keep the quote marks, and keep the comma at the end of each line.
    * To make a word bold, put two stars around it: **Boise**
    * If you need a quote mark inside the text, write it as \"  (backslash first)
    * Save the file, then refresh the website.

  The three language sections (en, ru, ro) have the same fields in the same
  order. If you add a service or town in one language, add it in all three.
*/

window.SITE = {

  // ---- Phone number (used everywhere on the site) ------------------------
  phone: {
    display: "(208) 810-1910",   // what visitors see
    tel: "+12088101910"          // what the phone dials: + country code + number, no spaces
  },

  // ---- Languages (order here = order of the buttons in the header) -------
  languages: [
    { code: "en", label: "EN", name: "English" },
    { code: "ru", label: "RU", name: "Русский" },
    { code: "ro", label: "RO", name: "Română" }
  ],

  text: {

    // ======================================================================
    en: {
      metaTitle: "ProTech Assistance | Mobile Truck Repair in Boise, ID",
      metaDescription: "Mobile truck repair technician serving Boise, Idaho. We come to you: trailer repair, brakes, electrical, air systems and roadside breakdown repair.",

      navServices: "Services",
      navArea: "Service Area",
      navContact: "Contact",
      callNow: "Call Now",
      tapToCall: "Tap to Call",

      eyebrow: "Mobile Truck & Trailer Repair · Boise, ID",
      headline1: "Broke down?",
      headline2: "We come to you.",
      lead: "Professional on-site repair for semis, trailers and work trucks. Skip the tow and get back on the road faster.",
      callButton: "Call {phone}",
      seeServices: "See Services",
      badges: ["On-site service", "Fast response", "Honest pricing"],

      servicesEyebrow: "What we do",
      servicesTitle: "Services",
      servicesIntro: "Full-service truck repair, done in your yard, on the shoulder, or wherever you're parked.",
      services: [
        { title: "Roadside Breakdown Repair", text: "Stranded? We diagnose and fix the problem on the spot whenever possible." },
        { title: "Trailer Repair", text: "Brakes, lights, axles, bearings, landing gear, doors and suspension repaired on-site for dry vans, reefers and flatbeds." },
        { title: "Brakes & Air Systems", text: "Brake adjustments and replacement, air leaks, compressors, dryers and slack adjusters." },
        { title: "Electrical", text: "Batteries, starters, alternators, wiring faults and lighting repairs." },
        { title: "Engine & Drivetrain", text: "Fuel system, cooling, belts, hoses, clutches and general mechanical repairs." },
        { title: "Preventive Maintenance", text: "Oil and filter service, fluid checks and inspections to keep your fleet out of the shop." }
      ],

      areaEyebrow: "Where we work",
      areaTitle: "Service Area",
      areaText1: "We provide mobile truck repair throughout the greater **Boise, Idaho** area. If your truck is stuck anywhere in our service area, call and we'll send a technician to you.",
      areaText2: "Not sure if you're in range? Give us a call, we're happy to help.",
      areaCenter: "Greater Boise Area",

      ctaTitle: "Need a technician now?",
      ctaText: "Call for fast, on-site truck repair in Boise.",

      footer: "© {year} ProTech Assistance · Mobile Truck Repair · Boise, ID"
    },

    // ======================================================================
    ru: {
      metaTitle: "ProTech Assistance | Выездной ремонт грузовиков в Бойсе, Айдахо",
      metaDescription: "Выездной ремонт грузовиков в Бойсе, штат Айдахо. Мы приезжаем к вам: ремонт прицепов, тормоза, электрика, пневмосистемы и ремонт при поломке на дороге.",

      navServices: "Услуги",
      navArea: "Зона обслуживания",
      navContact: "Контакты",
      callNow: "Позвонить",
      tapToCall: "Позвонить",

      eyebrow: "Выездной ремонт грузовиков и прицепов · Бойсе, Айдахо",
      headline1: "Сломались?",
      headline2: "Мы приедем к вам.",
      lead: "Профессиональный ремонт на месте для седельных тягачей, прицепов и рабочих грузовиков. Обойдитесь без эвакуатора и быстрее вернитесь на дорогу.",
      callButton: "Позвонить {phone}",
      seeServices: "Наши услуги",
      badges: ["Ремонт на месте", "Быстрый выезд", "Честные цены"],

      servicesEyebrow: "Что мы делаем",
      servicesTitle: "Услуги",
      servicesIntro: "Полный спектр ремонта грузовиков: на вашей стоянке, на обочине или там, где вы остановились.",
      services: [
        { title: "Ремонт при поломке на дороге", text: "Застряли? Мы найдём и устраним неисправность на месте, когда это возможно." },
        { title: "Ремонт прицепов", text: "Тормоза, освещение, оси, подшипники, опорные стойки, двери и подвеска: ремонтируем на месте фургоны, рефрижераторы и платформы." },
        { title: "Тормоза и пневмосистемы", text: "Регулировка и замена тормозов, утечки воздуха, компрессоры, осушители и рычаги-регулировщики." },
        { title: "Электрика", text: "Аккумуляторы, стартеры, генераторы, неисправности проводки и ремонт освещения." },
        { title: "Двигатель и трансмиссия", text: "Топливная система, охлаждение, ремни, шланги, сцепление и общий механический ремонт." },
        { title: "Профилактическое обслуживание", text: "Замена масла и фильтров, проверка жидкостей и осмотры, чтобы ваш транспорт реже попадал в сервис." }
      ],

      areaEyebrow: "Где мы работаем",
      areaTitle: "Зона обслуживания",
      areaText1: "Мы выполняем выездной ремонт грузовиков в **Бойсе, штат Айдахо**, и его окрестностях. Если ваш грузовик застрял в зоне нашего обслуживания, позвоните, и мы направим к вам техника.",
      areaText2: "Не уверены, что вы в зоне выезда? Позвоните нам, мы с радостью поможем.",
      areaCenter: "Бойсе и окрестности",

      ctaTitle: "Нужен техник прямо сейчас?",
      ctaText: "Звоните: быстрый ремонт грузовиков на месте в Бойсе.",

      footer: "© {year} ProTech Assistance · Выездной ремонт грузовиков · Бойсе, Айдахо"
    },

    // ======================================================================
    ro: {
      metaTitle: "ProTech Assistance | Reparații mobile de camioane în Boise, ID",
      metaDescription: "Reparații mobile de camioane în Boise, Idaho. Venim la tine: reparații remorci, frâne, electrică, sisteme pneumatice și reparații la pană pe drum.",

      navServices: "Servicii",
      navArea: "Zona deservită",
      navContact: "Contact",
      callNow: "Sună acum",
      tapToCall: "Apasă pentru apel",

      eyebrow: "Reparații mobile de camioane și remorci · Boise, ID",
      headline1: "Ai rămas în pană?",
      headline2: "Venim la tine.",
      lead: "Reparații profesionale la fața locului pentru capete tractor, remorci și camioane de lucru. Renunță la tractare și revino mai repede pe drum.",
      callButton: "Sună {phone}",
      seeServices: "Vezi serviciile",
      badges: ["Service la fața locului", "Intervenție rapidă", "Prețuri corecte"],

      servicesEyebrow: "Ce facem",
      servicesTitle: "Servicii",
      servicesIntro: "Reparații complete de camioane, făcute în curtea ta, pe marginea drumului sau oriunde ești parcat.",
      services: [
        { title: "Reparații la pană pe drum", text: "Ai rămas pe drum? Diagnosticăm și reparăm problema pe loc, ori de câte ori este posibil." },
        { title: "Reparații remorci", text: "Frâne, iluminat, osii, rulmenți, picioare de sprijin, uși și suspensii, reparate la fața locului pentru remorci cu prelată, frigorifice și platforme." },
        { title: "Frâne și sisteme pneumatice", text: "Reglarea și înlocuirea frânelor, scurgeri de aer, compresoare, uscătoare și regulatoare de joc." },
        { title: "Electrică", text: "Baterii, electromotoare, alternatoare, defecțiuni de cablaj și reparații la iluminat." },
        { title: "Motor și transmisie", text: "Sistem de alimentare, răcire, curele, furtunuri, ambreiaje și reparații mecanice generale." },
        { title: "Mentenanță preventivă", text: "Schimb de ulei și filtre, verificarea fluidelor și inspecții, ca flota ta să stea cât mai puțin în service." }
      ],

      areaEyebrow: "Unde lucrăm",
      areaTitle: "Zona deservită",
      areaText1: "Oferim reparații mobile de camioane în zona metropolitană **Boise, Idaho**. Dacă ai camionul blocat oriunde în zona noastră de deservire, sună și trimitem un tehnician la tine.",
      areaText2: "Nu ești sigur că ești în raza noastră? Sună-ne, te ajutăm cu plăcere.",
      areaCenter: "Zona metropolitană Boise",

      ctaTitle: "Ai nevoie de un tehnician acum?",
      ctaText: "Sună pentru reparații rapide de camioane la fața locului în Boise.",

      footer: "© {year} ProTech Assistance · Reparații mobile de camioane · Boise, ID"
    }
  }
};
