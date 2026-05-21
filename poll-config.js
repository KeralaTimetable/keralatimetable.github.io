// poll-config.js
// You can add as many exams here as you want. Just follow this format.

export const pollConfig = [
    {
        id: "UCEST105_2026_Regular", // Unique ID (Don't change this once live)
        subjectName: "UCEST105 - Python for Engineers",
        type: "Regular",
        opensAt: "2026-05-21T12:30:00", // When the poll becomes active
        closesAt: "2026-05-22T12:30:00"  // Auto-locks 24 hours later
    },
    {
        id: "GAMAT101_2026_Regular",
        subjectName: "GAMAT101 - Linear Algebra",
        type: "Regular",
        opensAt: "2026-05-24T12:30:00",
        closesAt: "2026-05-25T12:30:00"
    }
];
