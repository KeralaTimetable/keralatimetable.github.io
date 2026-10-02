const masterQuestionPool = [
  {
    q: "Who developed the Gemini 4 Argon AI model?",
    o: ["OpenAI", "Anthropic", "Google DeepMind", "Meta"],
    a: "C"
  },
  {
    q: "When was Gemini 4 Argon officially announced?",
    o: ["January 1, 2026", "May 14, 2026", "September 30, 2026", "November 15, 2026"],
    a: "C"
  },
  {
    q: "What is the maximum output token limit for Gemini 4 Argon in a single pass?",
    o: ["64,000 tokens", "128,000 tokens", "500,000 tokens", "1 million tokens"],
    a: "D"
  },
  {
    q: "Which of the following is NOT a primary target use case for Gemini 4 Argon?",
    o: ["Long-horizon software engineering", "Casual consumer chatbot interactions", "Enterprise finance and legal work", "Cybersecurity remediation"],
    a: "B"
  },
  {
    q: "Through which exclusive program was Gemini 4 Argon first rolled out?",
    o: ["The Fairwind Program", "The Gemini Advance Initiative", "Google Cloud Vanguard", "DeepMind Early Access"],
    a: "A"
  },
  {
    q: "Internally at Google, Gemini 4 Argon was used to migrate legacy C and C++ codebases into which programming language?",
    o: ["Go", "Python", "Rust", "Java"],
    a: "C"
  },
  {
    q: "Which specific open-source video decoder did Gemini 4 Argon help port, replacing 32K lines of hand-written SIMD code?",
    o: ["FFmpeg", "libvpx", "libgav1", "x264"],
    a: "C"
  },
  {
    q: "How much faster did the optimized Rust video decoder run after Gemini 4 Argon's profile-guided experiments?",
    o: ["1.5x faster", "2.7x faster", "4.0x faster", "10x faster"],
    a: "B"
  },
  {
    q: "In an internal Google data center deployment, Gemini 4 Argon optimized memory usage. How much memory was freed up initially?",
    o: ["50 TiB", "100 TiB", "Over 300 TiB", "1 PiB"],
    a: "C"
  },
  {
    q: "What specific aspect of quantum computing research did Gemini 4 Argon help optimize internally at Google?",
    o: ["Cryogenic cooling algorithms", "Quantum entanglement distance", "Hardware error correction codes", "Spacetime resources (qubits multiplied by gates)"],
    a: "D"
  },
  {
    q: "Which benchmark measures an AI's ability to understand long videos, where Gemini 4 Argon scored 91.7%?",
    o: ["VidBench", "LVBench", "VideoUnderstanding-1M", "GraphWalks"],
    a: "B"
  },
  {
    q: "On the tool-use benchmark 'AutomationBench,' which tests end-to-end execution across core business functions, what did Gemini 4 Argon score?",
    o: ["31.4%", "51.3%", "71.6%", "91.9%"],
    a: "B"
  },
  {
    q: "Is the underlying code for Gemini 4 Argon available as open-source software?",
    o: ["Yes, fully open-source", "Yes, for non-commercial use only", "No, it is a proprietary model", "Partially open-sourced through Android"],
    a: "C"
  },
  {
    q: "What is the reported API cost per million output tokens for Gemini 4 Argon?",
    o: ["$1", "$5", "$10", "$25"],
    a: "C"
  },
  {
    q: "Which Google operating system kernel was mentioned as part of an Argon codebase migration involving over 800,000 lines of code?",
    o: ["Android Linux Kernel", "Fuchsia OS Zircon kernel", "ChromeOS Core", "KataOS"],
    a: "B"
  },
  {
    q: "What score did Gemini 4 Argon achieve on the DeepSWE v1.1 software engineering benchmark?",
    o: ["55.0%", "68.0%", "77.9%", "91.9%"],
    a: "C"
  },
  {
    q: "On Harvey's Legal Agent Benchmark, what score did Gemini 4 Argon achieve?",
    o: ["5.4%", "19.6%", "42.5%", "65.4%"],
    a: "B"
  },
  {
    q: "What score did Gemini 4 Argon reach on the Vibe Code Bench?",
    o: ["74.2%", "89.6%", "90.3%", "91.9%"],
    a: "D"
  },
  {
    q: "How did Gemini 4 Argon perform on the GraphWalks BFS (256K to 1M context range) benchmark?",
    o: ["65.0%", "71.8%", "84.2%", "99.7%"],
    a: "C"
  },
  {
    q: "What is Gemini 4 Argon's pass rate on the 'Agent's Last Exam' benchmark?",
    o: ["34.2%", "39.5%", "69.2%", "88.8%"],
    a: "B"
  },
  {
    q: "What does the Chartography benchmark measure, where Gemini 4 Argon scored 71.6%?",
    o: ["Visual chart recognition", "Code navigation", "Financial spreadsheeting", "Video rendering"],
    a: "A"
  },
  {
    q: "Which trusted group of professionals was prioritized for the initial phased rollout of Gemini 4 Argon?",
    o: ["Machine learning engineers", "Financial analysts", "Trusted cybersecurity experts", "Legal scholars"],
    a: "C"
  },
  {
    q: "What score did Gemini 4 Argon achieve on the Vals Finance Agent v2 benchmark?",
    o: ["53.5%", "58.6%", "65.4%", "71.6%"],
    a: "C"
  },
  {
    q: "Which cybersecurity benchmark evaluates the model's ability to find and fix security flaws, where Argon scored 68.0%?",
    o: ["CWE-bench v1", "CyberSWE", "DefconBench", "Sec-Agent-1"],
    a: "A"
  },
  {
    q: "Which core Google library, alongside libgav1, was specifically cited as undergoing an automated C/C++ to Rust migration by Argon agents?",
    o: ["TensorFlow", "re2", "V8 Engine", "Skia"],
    a: "B"
  },
  {
    q: "On the LABBench 2 benchmark for science and math, what was Gemini 4 Argon's score?",
    o: ["68.6%", "73.1%", "85.4%", "88.8%"],
    a: "D"
  },
  {
    q: "What score did Gemini 4 Argon achieve on the FrontierSWE v2 benchmark?",
    o: ["55.0%", "65.5%", "77.9%", "91.9%"],
    a: "A"
  },
  {
    q: "Gemini 4 Argon is described as 'multimodal.' Which of the following best describes this capability?",
    o: [
      "It can operate on Windows, Mac, and Linux.",
      "It can process text, images, videos, and documents natively.",
      "It can write code in multiple programming languages simultaneously.",
      "It can integrate with multiple external APIs."
    ],
    a: "B"
  },
  {
    q: "What architectural constraint does Gemini 4 Argon's 1-million output token capability remove for large code refactors?",
    o: [
      "The need for manual human review",
      "The reliance on cloud servers",
      "The 'chunked workflow' that causes stitching and state loss",
      "The requirement for memory-safe languages"
    ],
    a: "C"
  },
  {
    q: "How does Gemini 4 Argon perform on the OSWorld-2.0 offline subset partial reward benchmark?",
    o: ["39.5%", "57.4%", "69.2%", "72.6%"],
    a: "C"
  }
];
