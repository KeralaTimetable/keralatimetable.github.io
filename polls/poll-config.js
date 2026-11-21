// ============================================================================
// KTU EXAM REVIEW HUB — OFFICIAL POLL CONFIG (polls/poll-config.js)
// Source: KTU/SOEX-IV/2122/2024 (07.11.2026)
//         B.Tech S3 (R, S) Examinations, November 2026 (2024 Scheme)
//
// Auto-Timing Rule:
//   - All S3 exams run 1:30 PM – 4:00 PM IST.
//   - Polls auto-open at 16:00:00+05:30 on exam day & auto-lock 24h later.
//
// Shareable Links:
//   - Exam Series : https://keralatimetable.in/polls/?exam=btech-s3-2024
//   - Single Poll : https://keralatimetable.in/polls/?s=s3-2024-<lowercase-code>
//     (e.g. https://keralatimetable.in/polls/?s=s3-2024-pccst303)
// ============================================================================

(function () {
    function buildSlotSubjects(semPrefix, semLabel, slot, day, openDate, closeDate, rows) {
        const opensAt = `${openDate}T16:00:00+05:30`;
        const closesAt = `${closeDate}T16:00:00+05:30`;
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

    window.KTU_POLL_EXAMS = [
        {
            id: "btech-s3-2024",
            title: "B.Tech S3 (R, S) November 2026 — 2024 Scheme Exam Review",
            semester: "S3",
            course: "B.Tech",
            scheme: "2024 Scheme",
            type: "Regular / Supply",
            subjects: s3Nov2026Subjects
        }
    ];
})();
