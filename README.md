# Py2CppAI

**High-level Pitch (the "Why")**

**Problem:** Teams prototype fast in Python but hit a wall when they need native-speed C++ for embedded boards, robotics, or high-frequency data loops.

**Solution:** Py2CppAI is a one-command transpiler that turns a safe subset of Python into modern, readable C++17—then sprinkles AI-suggested types and performance hints so you get 20-60× speed-ups without hand-rewriting code.

**Outcome:** Non-expert devs keep writing Python; experts get audit-ready C++ binaries for production.

## Roadmap at a Glance

| # | Milestone | Non-technical framing | Technical deliverables & stack |
|---|-----------|----------------------|--------------------------------|
| 0 | Kick-off & Design Doc | Agree on "what we're building" and success metric (≥ 20× speed-up). | • Ten-page spec (scoped Python subset, stretch goals)<br>• Repo, MIT licence, GitHub Actions skeleton |
| 1 | Parser Online | "We can now read any supported Python file." | • ast-based walker → JSON dump<br>• 95% test coverage (pytest, coverage) |
| 2 | Type Assurance | "Every variable now has a clear type; AI fills blanks." | • mypy integration<br>• Local Code-Llama call for unknowns<br>• Confidence score + fallback UI |
| 3 | Intermediate Representation (IR) | "Python logic is converted into a neutral, optimisable format." | • SSA-style 3-address IR classes<br>• Constant-fold & dead-code passes |
| 4 | C++17 Code-gen MVP | "Hello-world examples compile & run as C++." | • Jinja2 templates (std::vector, smart-ptrs)<br>• GCC/Clang build script, Sanitizer flags |
| 5 | CLI & Docker Image | "Anyone can run pytocpp my.py on any machine." | • Click-based CLI (--ai, -O2 flags)<br>• 200 MB Docker image with toolchain |
| 6 | AI Loop Optimiser | "Tool auto-unrolls hot loops when it helps." | • IR → prompt → #pragma unroll N injection<br>• Speed gain ≥ 1.5× on histogram demo |
| 7 | Benchmark Suite | "We prove the 20-60× claim." | • Dot-product, FIR filter, histogram scripts<br>• CSV + Matplotlib chart generator |
| 8 | Docs, Demo GIF, v1 Release | "Five-minute Quick-Start, share-able GIF, blog post." | • README, architecture diagram<br>• Medium-length launch blog<br>• GitHub Release v1.0 tag |

**Total calendar:** 8 two-week sprints.

## Tech Stack Summary

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Parser | Python 3.12 ast | Built-in, no grammar maintenance |
| Type checker | mypy API + Code-Llama 7B (Ollama) | Static first, AI only when needed |
| IR & passes | Custom SSA in Python | Simple to iterate; serialises to JSON |
| Code-gen | Jinja2 templates → C++17 | Human-readable output; easy to tweak |
| Native build | GCC / Clang via subprocess | Leverages proven optimiser |
| Perf tests | pytest-benchmark, timeit | Reproducible timing |
| Tooling | Docker, GitHub Actions, pre-commit | Smooth onboarding / CI |

## How the Pieces Join

1. User runs CLI → Python parsed
2. Types resolved → any missing ones predicted by LLM
3. AST lowered to IR → optimised
4. IR rendered as C++ → compiled with GCC
5. Binary executed & timed → result + speed-up printed

Every milestone delivers one of those arrows; when the last arrives, the whole pipeline clicks.

## Quick Start

```bash
# Coming soon - currently in development
pytocpp my_script.py --ai --optimize
```

## Development Status

🚧 **Currently working on:** Milestone 0 - Project setup and design documentation

## License

MIT License - see [LICENSE](LICENSE) file for details. 