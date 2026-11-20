// ============================================================================
// TEMPORARY HAPTICS & EMOJI BURST TEST CONFIG (polls/poll-config.js)
// Safe test IDs (`test-haptic-*`) — delete or replace with real config after testing.
// ============================================================================

window.KTU_POLL_EXAMS = [
    {
        id: "haptic-test-live",
        title: "Haptics & Emoji Burst Test Poll (Live Now)",
        semester: "S3",
        course: "B.Tech",
        scheme: "2024 Scheme",
        type: "Test Live",
        subjects: [
            {
                id: "test-haptic-cse-1",
                day: 1,
                slot: "A",
                code: "PCCST302",
                subjectName: "Test 1 — Tap 😊 Easy (Light Double-Pop)",
                branch: "CSE",
                tags: ["CSE", "S3", "Day 1"],
                opensAt: "2026-11-20T16:00:00+05:30",
                closesAt: "2026-11-21T23:59:00+05:30"
            },
            {
                id: "test-haptic-ce-2",
                day: 1,
                slot: "A",
                code: "PCCET302",
                subjectName: "Test 2 — Tap 😐 Average (Crisp Tap)",
                branch: "CE",
                tags: ["CE", "S3", "Day 1"],
                opensAt: "2026-11-20T16:00:00+05:30",
                closesAt: "2026-11-21T23:59:00+05:30"
            },
            {
                id: "test-haptic-ece-3",
                day: 1,
                slot: "A",
                code: "PCECT302",
                subjectName: "Test 3 — Tap 😓 Hard (Firm Pulse)",
                branch: "ECE",
                tags: ["ECE", "S3", "Day 1"],
                opensAt: "2026-11-20T16:00:00+05:30",
                closesAt: "2026-11-21T23:59:00+05:30"
            },
            {
                id: "test-haptic-me-4",
                day: 1,
                slot: "A",
                code: "PCMET302",
                subjectName: "Test 4 — Tap 💀 Supply Confirm (Triple Thud)",
                branch: "ME",
                tags: ["ME", "S3", "Day 1"],
                opensAt: "2026-11-20T16:00:00+05:30",
                closesAt: "2026-11-21T23:59:00+05:30"
            }
        ]
    },
    {
        id: "btech-s3-2024",
        title: "B.Tech S3 (R, S) November 2026 — 2024 Scheme Exam Review",
        semester: "S3",
        course: "B.Tech",
        scheme: "2024 Scheme",
        type: "Regular / Supply",
        subjects: [
            {
                id: "s3-2024-gamat301",
                day: 1,
                slot: "A",
                code: "GAMAT301",
                subjectName: "Mathematics for Information Science - 3",
                branch: "Group A",
                tags: ["Group A", "S3", "Slot A • Day 1"],
                opensAt: "2026-11-24T16:00:00+05:30",
                closesAt: "2026-11-25T16:00:00+05:30"
            },
            {
                id: "s3-2024-pccst302",
                day: 2,
                slot: "B",
                code: "PCCST302",
                subjectName: "Theory of Computation",
                branch: "CSE",
                tags: ["CSE", "S3", "Slot B • Day 2"],
                opensAt: "2026-11-26T16:00:00+05:30",
                closesAt: "2026-11-27T16:00:00+05:30"
            }
        ]
    }
];
