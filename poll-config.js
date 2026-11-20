// ============================================================================
// KTU EXAM REVIEW HUB — POLL CONFIGURATION (poll/poll-config.js)
// Each subject's `id` creates a unique shareable link:
//   https://keralatimetable.in/poll/?s=<subject-id>
// Each exam series creates a series link:
//   https://keralatimetable.in/poll/?exam=<exam-id>
//
// Time Rule: Set `opensAt` to right when the exam ends (e.g. 12:30 or 16:30 IST)
//            and `closesAt` to 24 hours later (auto-locks automatically).
// ============================================================================

window.KTU_POLL_EXAMS = [
    {
        id: "btech-s3-2024",
        title: "B.Tech S3 (R,S) 2024 Scheme Exam Review",
        semester: "S3",
        course: "B.Tech",
        scheme: "2024 Scheme",
        type: "Regular / Supply",
        subjects: [
            // --- EXAM DAY 1 ---
            {
                id: "s3-2024-mat201",
                day: 1,
                code: "GAMAT301",
                subjectName: "Mathematics for Computer & Information Science - 3",
                branch: "CSE / IT",
                tags: ["CSE / IT", "S3", "Day 1"],
                opensAt: "2026-11-18T12:30:00+05:30",
                closesAt: "2026-11-19T12:30:00+05:30"
            },

            // --- EXAM DAY 2 (Multiple branches on the same day!) ---
            {
                id: "s3-2024-cst201",
                day: 2,
                code: "PCCST302",
                subjectName: "Data Structures",
                branch: "CSE",
                tags: ["CSE", "S3", "Day 2"],
                opensAt: "2026-11-20T12:30:00+05:30",
                closesAt: "2026-11-21T12:30:00+05:30"
            },
            {
                id: "s3-2024-ect201",
                day: 2,
                code: "PCECT302",
                subjectName: "Solid State Devices",
                branch: "ECE",
                tags: ["ECE", "S3", "Day 2"],
                opensAt: "2026-11-20T12:30:00+05:30",
                closesAt: "2026-11-21T12:30:00+05:30"
            },
            {
                id: "s3-2024-met201",
                day: 2,
                code: "PCMET302",
                subjectName: "Mechanics of Solids",
                branch: "ME",
                tags: ["ME", "S3", "Day 2"],
                opensAt: "2026-11-20T12:30:00+05:30",
                closesAt: "2026-11-21T12:30:00+05:30"
            },
            {
                id: "s3-2024-cet201",
                day: 2,
                code: "PCCET302",
                subjectName: "Mechanics of Fluids",
                branch: "CE",
                tags: ["CE", "S3", "Day 2"],
                opensAt: "2026-11-20T12:30:00+05:30",
                closesAt: "2026-11-21T12:30:00+05:30"
            },
            {
                id: "s3-2024-eet201",
                day: 2,
                code: "PCEET302",
                subjectName: "Circuits and Networks",
                branch: "EEE",
                tags: ["EEE", "S3", "Day 2"],
                opensAt: "2026-11-20T12:30:00+05:30",
                closesAt: "2026-11-21T12:30:00+05:30"
            },

            // --- EXAM DAY 3 (Upcoming inside active series -> shows "Next Poll" countdown) ---
            {
                id: "s3-2024-cst303",
                day: 3,
                code: "PCCST303",
                subjectName: "Logic System Design",
                branch: "CSE",
                tags: ["CSE", "S3", "Day 3"],
                opensAt: "2026-11-23T12:30:00+05:30",
                closesAt: "2026-11-24T12:30:00+05:30"
            }
        ]
    },
    {
        id: "btech-s5-2019",
        title: "B.Tech S5 (R,S) 2019 Scheme Exam Review",
        semester: "S5",
        course: "B.Tech",
        scheme: "2019 Scheme",
        type: "Regular / Supply",
        subjects: [
            {
                id: "s5-2019-cst301",
                day: 1,
                code: "CST301",
                subjectName: "Formal Languages and Automata Theory",
                branch: "CSE",
                tags: ["CSE", "S5", "Day 1"],
                opensAt: "2026-11-24T12:30:00+05:30",
                closesAt: "2026-11-25T12:30:00+05:30"
            },
            {
                id: "s5-2019-ect301",
                day: 1,
                code: "ECT301",
                subjectName: "Linear Integrated Circuits",
                branch: "ECE",
                tags: ["ECE", "S5", "Day 1"],
                opensAt: "2026-11-24T12:30:00+05:30",
                closesAt: "2026-11-25T12:30:00+05:30"
            }
        ]
    }
];
