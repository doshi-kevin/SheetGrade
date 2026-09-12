# Glossary

Every technical term used anywhere in this project, one plain sentence each, plus where it shows up. Append as new terms get introduced.

- **IR (intermediate representation)** — our own plain data format that a workbook gets converted into after reading it, so every later step works with the same simple shape instead of dealing with the raw Excel file directly. Lives in `src/sheetgrade/ir/`.
- **Dataclass** — a Python way of defining a simple data container (a `Cell` has a value, a row, a column, etc.) without writing repetitive boilerplate code by hand. Used for every object in `src/sheetgrade/ir/models.py`.
- **Frozen / immutable** — once created, the object can't be changed. We made the IR frozen so that comparing a student's file to the teacher's key can never accidentally corrupt the key by editing it in place.
- **Workbook / Sheet / Cell / Cell address** — our names for an Excel file, one tab within it, one box in a grid, and that box's (row, column) position. The whole IR is built out of these four things.
- **Formula vs. cached value** — a formula cell stores two separate things: the formula text itself (`=SUM(B3:E3)`) and the last number Excel calculated and saved for it. They can disagree if the file was edited without being recalculated.
- **Dependency graph** — a record of which cells a formula reads from. If `F3` contains `=SUM(B3:E3)`, the graph says "F3 depends on B3 through E3." Built in Part 2 (`src/sheetgrade/reader/xlsx_reader.py`), used later for carry-through scoring (Part 19).
- **AST (abstract syntax tree)** — a formula broken down into its actual pieces (function, arguments, operators) instead of left as plain text, so code can tell that `=A1+A2` and `=SUM(A1:A2)` compute the same thing. Not built yet — planned for Part 14, after the parser that creates it is hand-written (Part 14 prep).
- **Recursive descent parser** — the specific kind of code that reads a formula's text left to right and builds the AST from it. One of the five things Kevin writes by hand in this project, not Claude.
- **Regex (regular expression)** — a pattern used to search text for a shape, like "a letter followed by a number." Used in the dependency graph to spot cell references like `B3` inside formula text, without needing a full parser.
- **Fixture** — a small, deliberately-built test file (like `tests/fixtures/keys/sample_key.xlsx`) used to test code against known, controlled content instead of a real unpredictable file.
- **Unit test** — a small, automated check that one specific piece of code does what it's supposed to. Lives under `tests/unit/`.
- **Golden snapshot test** — a test that saves a known-good copy of some output once, then checks that future runs still produce exactly that output — any difference is flagged as a decision to review, not silently allowed. `tests/golden/sample_key.json` is one.
- **Linter** — a tool that checks code for style problems and obvious mistakes without running it. We use one called `ruff`. Purpose only: it catches things like unused imports.
- **Type checker** — a tool that checks whether the *kinds* of data flowing through the code match what the code expects, without running it. We use one called `mypy`. It caught a real bug in Part 2 (see the Part 2 walkthrough).
- **CI (continuous integration)** — an automatic robot that runs our tests, linter, and type checker every time code is pushed to GitHub, so a broken change is caught within seconds instead of days later.
- **Virtual environment** — an isolated folder holding just this project's Python and its libraries, so it can't collide with anything else installed on the machine. Managed here by a tool called `uv`.
- **Dependency lock file** (`uv.lock`) — a file recording the *exact* version of every library actually installed, so the environment can be rebuilt identically later, by anyone.
- **Mutation** — a single, deliberate, labeled change made to a copy of the answer key (insert a column, rename a header, typo a value, etc.), used to manufacture test files where the "correct answer" is already known. `src/sheetgrade/mutate/`.
- **Manifest / mutation record** — the receipt a mutation writes about itself: what it changed, and what effect that change should have on grading (structural only, a real wrong value, etc.).
- **Ground truth by construction** — getting labeled test data for free by damaging something correct yourself and keeping a record of exactly what you did, instead of paying someone to label real mistakes.
- **Seed** — a starting number for a random number generator; the same seed always produces the same sequence of "random" choices, which is what makes a randomly-generated mutation reproducible.
- **Shallow immutability** — a Python gotcha: marking a dataclass `frozen=True` stops you reassigning its fields, but if a field holds a dict or list, the *contents* of that dict or list can still be changed in place. Every mutation in Part 3 builds a fresh copy of any dict it touches specifically to avoid this trap.
- **Model** — a large file of numbers (weights) produced by training, used to answer questions without any further training. `llama3.2:3b` is one such file, holding 3.2 billion of these numbers.
- **Inference** — the act of using a model to answer one question, as opposed to training it. Each inference call is stateless: the model has no memory of a previous call unless that earlier text is explicitly included in the new prompt.
- **Quantization** — storing a model's numbers in fewer bits (e.g. 4 instead of 16) to shrink its memory footprint, at some cost to precision. `llama3.2:3b` is quantized to Q4_K_M, taking ~2.6GB instead of the ~6.4GB it would need unquantized.
- **VRAM** — the GPU's own fast memory, separate from the computer's regular RAM. A model that doesn't fit in VRAM either fails to run on the GPU or runs much slower on regular RAM instead. See `docs/vram_budget.md`.
- **Temperature** — how much randomness a model is allowed when picking its next word. 0.0 always picks the single most likely word (deterministic); higher values allow less-likely words, adding variety at the cost of predictability. `src/sheetgrade/infer/sampling.py`.
- **Call site / routing table** — our name for any place in the pipeline that needs a model call, and the fixed lookup deciding whether that call goes to the local model or a paid hosted one. `src/sheetgrade/infer/router.py`.
- **Determinism test** — a test that runs the same input through a call site twice and asserts the output is identical both times. Requires temperature 0.0 for anything it covers.
