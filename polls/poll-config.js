// ============================================================================
// KTU EXAM REVIEW HUB — OFFICIAL POLL CONFIG (polls/poll-config.js)
// Sources:
//   - KTU/SOEX-IV/2122/2024 (07.11.2026) — B.Tech S3 (R, S) Exam Nov 2026 (2024 Scheme)
//   - KTU/EX-II#1/1833/2025 (07.11.2026) — B.Tech S5 (R) Exam Nov 2026 (2024 Scheme)
//
// Auto-Timing Rule:
//   - Mon–Thu & Sat exams run 1:30 PM – 4:00 PM IST -> polls open 16:00:00+05:30.
//   - Friday exams (S5 Slot B) run 2:00 PM – 4:30 PM IST -> polls open 16:30:00+05:30.
//   - All polls auto-lock 24h after opening.
//
// Shareable Links:
//   - S3 Series   : https://keralatimetable.in/polls/?exam=btech-s3-2024
//   - S3 Poll     : https://keralatimetable.in/polls/?s=s3-2024-<lowercase-code>
//   - S5 Series   : https://keralatimetable.in/polls/?exam=btech-s5-2024
//   - S5 Poll     : https://keralatimetable.in/polls/?s=s5-2024-<lowercase-code>
//     (e.g. https://keralatimetable.in/polls/?s=s5-2024-pccst501)
// ============================================================================

(function () {
    function buildSlotSubjects(semPrefix, semLabel, slot, day, openDate, closeDate, rows, openTime = "16:00:00") {
        const opensAt = `${openDate}T${openTime}+05:30`;
        const closesAt = `${closeDate}T${openTime}+05:30`;
        return rows.map(([code, subjectName, branch]) => ({
            id: `${semPrefix}-${code.toLowerCase()}`,
            day,
            slot,
            code,
            subjectName,
            branch,
            tags: [branch, semLabel, `Slot ${slot} • Day ${day}`],
            opensAt,
            closesAt
        }));
    }

    // ========================================================================
    // B.TECH S3 (R, S) NOVEMBER 2026 — 2024 SCHEME
    // ========================================================================
    const s3Nov2026Subjects = [
        // ====================================================================
        // SLOT A — EXAM DAY 1 — 24.11.2026 (Tuesday, 1:30 PM – 4:00 PM)
        // ====================================================================
        ...buildSlotSubjects("s3-2024", "S3", "A", 1, "2026-11-24", "2026-11-25", [
            ["GAMAT301", "Mathematics for Information Science - 3", "Group A"],
            ["GDMAT301", "Mathematics for Life Science - 3", "Group D"],
            ["GYMAT301", "Mathematics for Physical Science - 3 / Electrical Science - 3", "Group B & C"]
        ]),

        // ====================================================================
        // SLOT B — EXAM DAY 2 — 26.11.2026 (Thursday, 1:30 PM – 4:00 PM)
        // ====================================================================
        ...buildSlotSubjects("s3-2024", "S3", "B", 2, "2026-11-26", "2026-11-27", [
            ["PCCST302", "Theory of Computation", "CSE"],
            ["PCECT302", "Solid State Devices", "ECE"],
            ["PCEET302", "Circuits and Networks", "EEE"],
            ["PCMET302", "Mechanics of Solids", "ME"],
            ["PCCET302", "Fluid Mechanics", "CE"],
            ["PCITT302", "Computer Organisation and Architecture", "IT"],
            ["PCAET302", "Electronic Devices and Circuits", "AEI"],
            ["PCAGT302", "Strength of Materials & Theory of Structures", "AG"],
            ["PCAIT302", "Foundations of Artificial Intelligence", "AI"],
            ["PCAMT302", "Machine Learning - I", "AI & ML"],
            ["PCAOT302", "Engineering Thermodynamics", "AO"],
            ["PCAUT302", "Fluid Mechanics and Hydraulic Machines", "AU"],
            ["PCBBT302", "Biochemistry", "BT"],
            ["PCBMT302", "Analog Electronics", "BM"],
            ["PCBRT302", "Introduction to Robotics", "BR"],
            ["PCCBT302", "Fundamentals of Management", "CSBS"],
            ["PCCGT302", "Computer Networks and Protocols", "CG"],
            ["PCCHT302", "Particle Technology", "CH"],
            ["PCCPT302", "Microcontrollers and Embedded Systems", "EL / CP"],
            ["PCEBT302", "Electronic Devices & Circuits", "EB"],
            ["PCERT302", "Data Structures", "ER"],
            ["PCFTT302", "Food Thermodynamics and Process Calculations", "FT"],
            ["PCICT302", "Electronics Circuits and Network", "IC"],
            ["PCIET302", "Fluid Mechanics and Hydraulic Machines", "IE"],
            ["PCMRT302", "Electrical Machines & Drives", "MR"],
            ["PCMUT302", "Automotive Systems", "MU"],
            ["PCNST302", "Fluid Mechanics for Naval Architects", "NS"],
            ["PCPET302", "Solid Mechanics and Design", "PE"],
            ["PCPOT302", "Polymer Science", "PO"],
            ["PCRAT302", "Microcontrollers and Embedded Systems", "RA"],
            ["PCRUT302", "Solid Mechanics", "RU"],
            ["PCSFT302", "Fire Engineering Fundamentals", "SF"]
        ]),

        // ====================================================================
        // SLOT C — EXAM DAY 3 — 30.11.2026 (Monday, 1:30 PM – 4:00 PM)
        // ====================================================================
        ...buildSlotSubjects("s3-2024", "S3", "C", 3, "2026-11-30", "2026-12-01", [
            ["PCCST303", "Data Structures and Algorithms", "CSE"],
            ["PCECT303", "Analog Circuits", "ECE"],
            ["PCEET303", "DC Machines and Transformers", "EEE"],
            ["PCMET303", "Fluid Mechanics and Machinery", "ME"],
            ["PCCET303", "Structural Analysis - I", "CE"],
            ["PCITT303", "Data Structures", "IT"],
            ["PCAET303", "Transducers and Measurements", "AEI"],
            ["PCAGT303", "Fluid Mechanics & Open Channel Hydraulics", "AG"],
            ["PCAOT303", "Mechanics of Aircraft Materials", "AO"],
            ["PCAUT303", "Automotive Chassis", "AU"],
            ["PCBBT303", "Microbiology", "BT"],
            ["PCBMT303", "Medical Physics", "BM"],
            ["PCBRT303", "Sensors and Actuators", "BR"],
            ["PCCHT303", "Chemical Engineering Thermodynamics", "CH"],
            ["PCCPT303", "Fundamentals of Cyber Physical Systems", "EL / CP"],
            ["PCCVT303", "Analysis of Structures", "CV"],
            ["PCEBT303", "Logic Circuits & Design", "EB"],
            ["PCEIT303", "Network Theory", "EIE"],
            ["PCEOT303", "Data Structures and Algorithms", "EO"],
            ["PCERT303", "Digital System Design Using Verilog", "ER"],
            ["PCFTT303", "Food Microbiology", "FT"],
            ["PCICT303", "Transducers and Measurements", "IC"],
            ["PCIET303", "Thermal Engineering", "IE"],
            ["PCMRT303", "Mechanics of Solids", "MR"],
            ["PCNST303", "Solid Mechanics for Naval Architects", "NS"],
            ["PCPET303", "Fluid and Thermal Sciences", "PE"],
            ["PCPOT303", "Latex Technology", "PO"],
            ["PCRAT303", "Robotic Manipulators and Workcell Design", "RA"],
            ["PCRUT303", "Materials and Manufacturing Processes", "RU"],
            ["PCSFT303", "Fluid Mechanics and Hydraulic Machines", "SF"]
        ]),

        // ====================================================================
        // SLOT D — EXAM DAY 4 — 02.12.2026 (Wednesday, 1:30 PM – 4:00 PM)
        // ====================================================================
        ...buildSlotSubjects("s3-2024", "S3", "D", 4, "2026-12-02", "2026-12-03", [
            ["PBCST304", "Object Oriented Programming", "CSE"],
            ["PBECT304", "Logic Circuit Design", "ECE"],
            ["PBEET304", "Analog Electronics", "EEE"],
            ["PBMET304", "Manufacturing Processes", "ME"],
            ["PBCET304", "Surveying & Geomatics", "CE"],
            ["PBITT304", "Database Management System", "IT"],
            ["PBADT304", "Introduction to Data Science", "AI & DS"],
            ["PBAGT304", "Surface & Groundwater Hydrology", "AG"],
            ["PBAIT304", "Human Computer Interaction", "AI"],
            ["PBAOT304", "Fluid Mechanics", "AO"],
            ["PBAUT304", "Material Science and Metallurgy", "AU"],
            ["PBBBT304", "PBL1: Industrial Bioprocess Technology", "BT"],
            ["PBBMT304", "Digital Electronics", "BM"],
            ["PBBRT304", "Electronics Circuits & Logic Design", "BR"],
            ["PBCCT304", "Basic Concepts in Computer Networks", "CC"],
            ["PBCHT304", "Fluid and Particle Mechanics", "CH"],
            ["PBCMT304", "Concepts in Machine Learning", "AI & ML"],
            ["PBCPT304", "Analog and Digital Electronics", "EL / CP"],
            ["PBEBT304", "Biosensors & Transducers", "EB"],
            ["PBEIT304", "Sensors & Measurements", "EIE"],
            ["PBEOT304", "Digital Electronics and Logic System Design", "EO"],
            ["PBERT304", "Electronic Devices and Circuits", "ER"],
            ["PBFTT304", "Food Process Engineering", "FT"],
            ["PBICT304", "Design of Logic Circuits", "IC"],
            ["PBIET304", "Operations Management", "IE"],
            ["PBMRT304", "Analog Electronics", "MR"],
            ["PBNST304", "Ship Stability", "NS"],
            ["PBPET304", "Material Science and Engineering", "PE"],
            ["PBPOT304", "Biomedical & Biopolymers", "PO"],
            ["PBRAT304", "Analog and Digital Electronics", "RA"],
            ["PBRUT304", "Electronic Circuits and Logic Design", "RU"],
            ["PBSFT304", "Chemical Process Principles", "SF"]
        ]),

        // ====================================================================
        // SLOT F — EXAM DAY 5 — 05.12.2026 (Saturday, 1:30 PM – 4:00 PM)
        // ====================================================================
        ...buildSlotSubjects("s3-2024", "S3", "F", 5, "2026-12-05", "2026-12-06", [
            ["GAEST305", "Digital Electronics & Logic Design", "Group A"],
            ["GNEST305", "Introduction to Artificial Intelligence and Data Science", "Common"]
        ]),

        // ====================================================================
        // SLOT G — EXAM DAY 6 — 08.12.2026 (Tuesday, 1:30 PM – 4:00 PM)
        // ====================================================================
        ...buildSlotSubjects("s3-2024", "S3", "G", 6, "2026-12-08", "2026-12-09", [
            ["UCHUT346", "Economics for Engineers", "Common"],
            ["UCHUT347", "Engineering Ethics and Sustainable Development", "Common"]
        ])
    ];

    // ========================================================================
    // B.TECH S5 (R) NOVEMBER 2026 — 2024 SCHEME
    // ========================================================================
    const s5Nov2026Subjects = [
        // ====================================================================
        // SLOT A — EXAM DAY 1 — 23.11.2026 (Monday, 1:30 PM – 4:00 PM)
        // ====================================================================
        ...buildSlotSubjects("s5-2024", "S5", "A", 1, "2026-11-23", "2026-11-24", [
            ["PCCST501", "Computer Networks", "CSE"],
            ["PCECT501", "Electromagnetics", "ECE"],
            ["PCEET501", "Power Generation, Transmission and Protection", "EEE"],
            ["PCMET501", "Dynamics of Machinery", "ME"],
            ["PCCET501", "Hydrology & Water Resources Engineering", "CE"],
            ["PCITT501", "Machine Learning", "IT"],
            ["PCAET501", "Control System Theory", "AEI"],
            ["PCAGT501", "Design of Farm Structures & Cost Estimation", "AG"],
            ["PCAMT501", "Introduction to Internet of Things", "AI & ML"],
            ["PCAOT501", "High Speed Aerodynamics", "AO"],
            ["PCAUT501", "Automobile Electrical and Electronics", "AU"],
            ["PCBBT501", "Heat Transfer Operation", "BT"],
            ["PCBMT501", "Biomedical Signal Processing", "BM"],
            ["PCBRT501", "Medical Robotics", "BR"],
            ["PCCCT501", "Applied Cryptography", "CC"],
            ["PCCGT501", "Foundations of Cryptography", "CG"],
            ["PCCHT501", "Mass Transfer Operation - II", "CH"],
            ["PCCPT501", "Control Systems", "EL / CP"],
            ["PCEBT501", "Hospital Engineering", "EB"],
            ["PCEOT501", "Microcontroller and Embedded Systems", "EO"],
            ["PCERT501", "Digital Signal Processing", "ER"],
            ["PCEVT501", "Digital CMOS Design", "EV"],
            ["PCFTT501", "Processing of Fruits and Vegetables", "FT"],
            ["PCICT501", "Classical Control Engineering", "IC"],
            ["PCIET501", "Data Analytics", "IE"],
            ["PCMRT501", "Linear Control Systems", "MR"],
            ["PCMUT501", "Automotive Electrical and Electronics Systems", "MU"],
            ["PCNST501", "Ship Dynamics", "NS"],
            ["PCPET501", "Industrial Engineering", "PE"],
            ["PCPOT501", "Rubbers – Science & Technology", "PO"],
            ["PCRAT501", "Control Systems", "RA"],
            ["PCRUT501", "Industrial Automation", "RU"],
            ["PCSFT501", "Structural Fire Safety and Design of Fire Protection Systems", "SF"]
        ]),

        // ====================================================================
        // SLOT B — EXAM DAY 2 — 27.11.2026 (Friday, 2:00 PM – 4:30 PM)
        // ====================================================================
        ...buildSlotSubjects("s5-2024", "S5", "B", 2, "2026-11-27", "2026-11-28", [
            ["PCCST502", "Design and Analysis of Algorithms", "CSE"],
            ["PCECT502", "Analog and Digital Communication", "ECE"],
            ["PCEET502", "Electromagnetic Theory", "EEE"],
            ["PCMET502", "Advanced Manufacturing Engineering", "ME"],
            ["PCCET502", "Transportation Engineering", "CE"],
            ["PCITT502", "Algorithm Analysis and Design", "IT"],
            ["PCADT502", "Robotics and Intelligent Systems", "AI & DS"],
            ["PCAET502", "Process Dynamics and Control", "AEI"],
            ["PCAGT502", "Thermodynamics & Heat Engines", "AG"],
            ["PCAIT502", "Recommendation System", "AI"],
            ["PCAOT502", "Aircraft Structures - II", "AO"],
            ["PCAUT502", "Theory of Machines", "AU"],
            ["PCBBT502", "Bioprocess Engineering", "BT"],
            ["PCBMT502", "Therapeutic Equipment", "BM"],
            ["PCBRT502", "Electrical Drives & Control Systems", "BR"],
            ["PCCAT502", "Introduction to Artificial Intelligence", "CA"],
            ["PCCCT502", "Network and System Security", "CC"],
            ["PCCHT502", "Chemical Reaction Engineering", "CH"],
            ["PCCPT502", "Introduction to Wireless Communication", "EL / CP"],
            ["PCEBT502", "Medical Imaging Techniques", "EB"],
            ["PCEOT502", "Power Electronics", "EO"],
            ["PCERT502", "Theory of Computation", "ER"],
            ["PCEVT502", "FPGA Based System Design", "EV"],
            ["PCFTT502", "Processing of Milk & Milk Products", "FT"],
            ["PCICT502", "Process Control Instrumentation", "IC"],
            ["PCIET502", "Supply Chain and Logistics Management", "IE"],
            ["PCMRT502", "Thermodynamics", "MR"],
            ["PCMUT502", "Heat and Mass Transfer", "MU"],
            ["PCNST502", "Ship Structures I", "NS"],
            ["PCPET502", "Sensors and Mechatronic Systems", "PE"],
            ["PCPOT502", "Polymer Processing", "PO"],
            ["PCRAT502", "Advanced Topics in Artificial Intelligence & Machine Learning", "RA"],
            ["PCRUT502", "Kinematics and Design of Machine Elements", "RU"],
            ["PCSFT502", "Qualitative and Quantitative Approach in Safety", "SF"]
        ], "16:30:00"),

        // ====================================================================
        // SLOT C — EXAM DAY 3 — 01.12.2026 (Tuesday, 1:30 PM – 4:00 PM)
        // ====================================================================
        ...buildSlotSubjects("s5-2024", "S5", "C", 3, "2026-12-01", "2026-12-02", [
            ["PCCST503", "Machine Learning", "CSE"],
            ["PCECT503", "Control Systems", "ECE"],
            ["PCEET503", "Signals & Systems", "EEE"],
            ["PCMET503", "Heat and Mass Transfer", "ME"],
            ["PCCET503", "Environmental Engineering", "CE"],
            ["PCITT503", "Software Engineering", "IT"],
            ["PCAET503", "Power Electronics", "AEI"],
            ["PCAGT503", "Heat & Mass Transfer", "AG"],
            ["PCAIT503", "Web and Mobile Application for AI", "AI"],
            ["PCAOT503", "Air Breathing Propulsion", "AO"],
            ["PCAUT503", "Automotive Transmission", "AU"],
            ["PCBBT503", "Mass Transfer Operations", "BT"],
            ["PCBMT503", "Medical Imaging Techniques", "BM"],
            ["PCBRT503", "Power Electronics & Applications", "BR"],
            ["PCCBT503", "Computational Statistics", "CSBS"],
            ["PCCDT503", "Data Analytics", "CD"],
            ["PCCGT503", "Microprocessors and Microcontrollers for IoT", "CG"],
            ["PCCHT503", "Chemical Technology", "CH"],
            ["PCCMT503", "Deep Learning Concepts", "AI & ML"],
            ["PCCNT503", "Web Programming", "CN"],
            ["PCCPT503", "Electric Drives & Control", "EL / CP"],
            ["PCCVT503", "Foundation Engineering", "CV"],
            ["PCEBT503", "Therapeutic Equipments", "EB"],
            ["PCEOT503", "Power Systems", "EO"],
            ["PCERT503", "Microcontrollers and Interfacing", "ER"],
            ["PCEVT503", "VLSI Technology", "EV"],
            ["PCFTT503", "Food Safety & Quality Regulations", "FT"],
            ["PCICT503", "Industrial Instrumentation - II", "IC"],
            ["PCIET503", "Quality Engineering", "IE"],
            ["PCMRT503", "Industrial Hydraulics & Pneumatics", "MR"],
            ["PCMUT503", "Electric Vehicles - Drives and Control", "MU"],
            ["PCNST503", "Marine Engineering", "NS"],
            ["PCPET503", "Mechanical Measurements and Quality Control", "PE"],
            ["PCPOT503", "Polymer Machinery & Product Manufacturing", "PO"],
            ["PCRAT503", "Electric Drives & Control", "RA"],
            ["PCRUT503", "Electric Drives and Control", "RU"],
            ["PCSFT503", "Occupational Health, Hygiene and First Aid", "SF"]
        ]),

        // ====================================================================
        // SLOT D — EXAM DAY 4 — 03.12.2026 (Thursday, 1:30 PM – 4:00 PM)
        // ====================================================================
        ...buildSlotSubjects("s5-2024", "S5", "D", 4, "2026-12-03", "2026-12-04", [
            ["PBCST504", "Microcontrollers", "CSE"],
            ["PBECT504", "Digital Signal Processing", "ECE"],
            ["PBEET504", "Microprocessor and Embedded Systems", "EEE"],
            ["PBMET504", "Management for Engineers", "ME"],
            ["PBCET504", "Foundation Engineering", "CE"],
            ["PBITT504", "Web Application Development", "IT"],
            ["PBADT504", "Big Data Analytics", "AI & DS"],
            ["PBAGT504", "Irrigation & Drainage Engineering", "AG"],
            ["PBAIT504", "Real Time Systems", "AI"],
            ["PBAOT504", "Heat Transfer", "AO"],
            ["PBAUT504", "Computer Aided Design and Manufacturing", "AU"],
            ["PBBBT504", "Enzyme Kinetics and Technology", "BT"],
            ["PBBMT504", "Analytical and Diagnostic Equipment", "BM"],
            ["PBBRT504", "Biomedical Signal Processing", "BR"],
            ["PBCAT504", "Advanced Graph Algorithms", "CA"],
            ["PBCBT504", "Operations Research", "CSBS"],
            ["PBCDT504", "Big Data Processing", "CD"],
            ["PBCGT504", "Software Engineering and Design Concepts", "CG"],
            ["PBCHT504", "Chemical Engineering Design - I", "CH"],
            ["PBCMT504", "Introduction to Computer Vision", "AI & ML"],
            ["PBCNT504", "Virtual Reality", "CN"],
            ["PBCPT504", "Fundamentals of Real Time Digital Signal Processing", "EL / CP"],
            ["PBCVT504", "Environmental Engineering II", "CV"],
            ["PBEBT504", "Introduction to Biomedical Signal Processing", "EB"],
            ["PBEOT504", "Database Management System", "EO"],
            ["PBERT504", "Database Management Systems", "ER"],
            ["PBEVT504", "Embedded System Design", "EV"],
            ["PBFTT504", "Food Additives and Flavorings", "FT"],
            ["PBICT504", "Microcontroller", "IC"],
            ["PBIET504", "Optimisation Techniques", "IE"],
            ["PBMRT504", "Signal Processing & Communication", "MR"],
            ["PBMUT504", "Mechanics of Machinery", "MU"],
            ["PBNST504", "Ship Design I", "NS"],
            ["PBPET504", "CAD/CAM/CAE", "PE"],
            ["PBPOT504", "Tyre Technology", "PO"],
            ["PBRAT504", "Robot Operating System", "RA"],
            ["PBRUT504", "Mobile Robotics", "RU"],
            ["PBSFT504", "Heat and Mass Transfer Operations", "SF"]
        ]),

        // ====================================================================
        // SLOT E — EXAM DAY 5 — 07.12.2026 (Monday, 1:30 PM – 4:00 PM)
        // ====================================================================
        ...buildSlotSubjects("s5-2024", "S5", "E", 5, "2026-12-07", "2026-12-08", [
            ["PECST521", "Software Project Management", "CSE"],
            ["PECST522", "Artificial Intelligence", "CSE"],
            ["PECST523", "Data Analytics", "CSE"],
            ["PECST524", "Data Compression", "CSE"],
            ["PECST525", "Data Mining", "CSE"],
            ["PECST527", "Computer Graphics & Multimedia", "CSE"],
            ["PECST595", "Advanced Graph Algorithms", "CSE"],
            ["PEECT521", "Biomedical Engineering", "ECE"],
            ["PEECT522", "Data Structures", "ECE"],
            ["PEECT523", "Sensors and Actuators", "ECE"],
            ["PEECT524", "ARM Architecture & Programming", "ECE"],
            ["PEECT525", "ARM Architecture Programming & Interfacing", "ECE"],
            ["PEECT526", "High Speed Digital Design", "ECE"],
            ["PEEET521", "Energy Storage Systems", "EEE"],
            ["PEEET522", "Electric Vehicles", "EEE"],
            ["PEEET523", "Digital System Design", "EEE"],
            ["PEEET526", "Data Structures", "EEE"],
            ["PEEET527", "Introduction to Machine Learning", "EEE"],
            ["PEEET528", "Computer Network Systems", "EEE"],
            ["PEMET521", "Computational Fluid Dynamics", "ME"],
            ["PEMET522", "Design for Manufacture and Assembly", "ME"],
            ["PEMET523", "Computer Aided Design and Analysis", "ME"],
            ["PEMET524", "Additive Manufacturing", "ME"],
            ["PEMET525", "Instrumentation and Control Systems", "ME"],
            ["PEMET526", "Energy Economics and Policy", "ME"],
            ["PEMET527", "Human Resources Management", "ME"],
            ["PEMET528", "Operations Research", "ME"],
            ["PECET521", "Advanced Structural Analysis", "CE"],
            ["PECET522", "Modern Construction Technology", "CE"],
            ["PECET523", "Open Channel Hydraulics", "CE"],
            ["PECET524", "Disaster Management", "CE"],
            ["PECET525", "Design of Prestressed Concrete", "CE"],
            ["PECET527", "Town Planning", "CE"],
            ["PEITT521", "Soft Computing", "IT"],
            ["PEITT522", "Internetworking Using TCP/IP", "IT"],
            ["PEITT523", "Cloud Computing", "IT"],
            ["PEITT524", "Data Mining and Warehousing", "IT"],
            ["PEITT525", "Formal Languages and Automata Theory", "IT"],
            ["PEADT522", "Business Analytics", "AI & DS"],
            ["PEADT523", "Information Systems", "AI & DS"],
            ["PEADT525", "Fundamentals of Digital Image Processing", "AI & DS"],
            ["PEAET521", "Data Communication", "AEI"],
            ["PEAET522", "Modern Processor Architecture", "AEI"],
            ["PEAET525", "VLSI System Design", "AEI"],
            ["PEAET526", "Biomedical Instrumentation", "AEI"],
            ["PEAET595", "Robotics and Automation", "AEI"],
            ["PEAGT521", "Remote Sensing & GIS", "AG"],
            ["PEAGT522", "Pump Engineering and Hydraulic Control", "AG"],
            ["PEAIT521", "Knowledge Engineering", "AI"],
            ["PEAIT522", "Healthcare Analytics", "AI"],
            ["PEAIT527", "Responsible Artificial Intelligence", "AI"],
            ["PEAMT595", "Operating System Concepts", "AI & ML"],
            ["PEAOT525", "Civil Aviation Regulations", "AO"],
            ["PEAOT527", "Airframe Maintenance and Repair", "AO"],
            ["PEAUT522", "Automotive Pollution and Testing", "AU"],
            ["PEAUT525", "Electric Drives and Controls for Automation", "AU"],
            ["PEBBT521", "Cancer Biology", "BT"],
            ["PEBBT522", "Bioethics and Safety", "BT"],
            ["PEBBT524", "Genetic Engineering", "BT"],
            ["PEBBT525", "Bio Separation Technology", "BT"],
            ["PEBMT523", "Radiological Equipments", "BM"],
            ["PEBMT524", "Implants & Prosthetic Engineering", "BM"],
            ["PEBMT525", "Artificial Neural Networks", "BM"],
            ["PEBMT526", "Fundamentals of BioMEMS and Microfluidics", "BM"],
            ["PEBRT525", "Artificial Intelligence for Robotics", "BR"],
            ["PECAT522", "Artificial Neural Networks Techniques", "CA"],
            ["PECBT525", "Managerial Economics", "CSBS"],
            ["PECCT521", "Network Fundamentals for Cloud", "CC"],
            ["PECCT522", "Block Chain and Crypto Currency", "CC"],
            ["PECCT523", "AI in Cyber Security", "CC"],
            ["PECCT524", "Advanced Industrial Cyber Security", "CC"],
            ["PECDT523", "Data Privacy and Security", "CD"],
            ["PECHT522", "Oil and Natural Gas Engineering", "CH"],
            ["PECHT523", "Polymer Technology", "CH"],
            ["PECHT524", "Project Engineering", "CH"],
            ["PECHT525", "Mathematical Methods in Process Engineering", "CH"],
            ["PECHT527", "Corrosion Engineering", "CH"],
            ["PECMT522", "Expert Systems", "AI & ML"],
            ["PECMT535", "Object Oriented Programming Concepts", "AI & ML"],
            ["PECNT529", "Visual Design and Communication", "CN"],
            ["PECPT521", "Sensor and Actuator Integration", "EL / CP"],
            ["PECPT525", "Cloud Computing", "EL / CP"],
            ["PEEBT524", "Biomedical Optics & Bio Photonics", "EB"],
            ["PEEBT525", "Artificial Neural Networks", "EB"],
            ["PEEBT526", "VLSI Design", "EB"],
            ["PEEOT521", "Modern Operating Systems", "EO"],
            ["PEERT521", "Wireless Sensor Networks", "ER"],
            ["PEERT522", "CMOS VLSI Design", "ER"],
            ["PEERT524", "Cloud Computing", "ER"],
            ["PEEVT521", "Analog and Digital Communication", "EV"],
            ["PEEVT523", "Graph Theory", "EV"],
            ["PEEVT527", "Real Time Operating Systems", "EV"],
            ["PEFTT522", "Nanotechnology in Food", "FT"],
            ["PEFTT524", "Sensory Evaluation of Food Products", "FT"],
            ["PEFTT528", "Food Fermentation Technology", "FT"],
            ["PEICT521", "Analytical Instrumentation", "IC"],
            ["PEICT522", "Biomedical Instrumentation", "IC"],
            ["PEIET521", "Advanced Manufacturing Processes", "IE"],
            ["PEIET525", "Additive Manufacturing and 3D Printing", "IE"],
            ["PEMRT521", "Power Electronics", "MR"],
            ["PEMRT522", "Design of Manufacture", "MR"],
            ["PEMRT525", "IoT & Applications", "MR"],
            ["PEMUT522", "Automotive Pollution and Control", "MU"],
            ["PEMUT523", "Tractors, Farm Equipments and Special Types of Vehicles", "MU"],
            ["PENST521", "Electrical Technology & Instrumentation", "NS"],
            ["PEPET524", "Logistics & Supply Chain Engineering", "PE"],
            ["PEPET525", "Design of Experiments and Statistical Analysis", "PE"],
            ["PEPOT525", "Polymer Electrolytes & Gels", "PO"],
            ["PERAT524", "Additive Manufacturing and 3D Printing", "RA"],
            ["PERUT521", "Artificial Intelligence for Robotics", "RU"],
            ["PERUT525", "Robot Operating System ROS", "RU"],
            ["PERUT526", "Industrial Engineering", "RU"],
            ["PESFT521", "Non-Destructive Testing Methods", "SF"],
            ["PESFT522", "Safety in Material Handling", "SF"],
            ["PESFT526", "Safety in Construction", "SF"]
        ])
    ];

    window.KTU_POLL_EXAMS = [
        {
            id: "btech-s3-2024",
            title: "B.Tech S3 (R, S) November 2026 — 2024 Scheme Exam Review",
            semester: "S3",
            course: "B.Tech",
            scheme: "2024 Scheme",
            type: "Regular / Supply",
            subjects: s3Nov2026Subjects
        },
        {
            id: "btech-s5-2024",
            title: "B.Tech S5 (R) November 2026 — 2024 Scheme Exam Review",
            semester: "S5",
            course: "B.Tech",
            scheme: "2024 Scheme",
            type: "Regular",
            subjects: s5Nov2026Subjects
        }
    ];
})();
