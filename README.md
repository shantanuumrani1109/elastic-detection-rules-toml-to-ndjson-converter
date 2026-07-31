<div align="center">

# 🛡️ Elastic Detection Rules → Kibana NDJSON Converter

### Three ways to turn Elastic's official `.toml` detection rules into ready-to-import Kibana `.ndjson` — pick the one that fits how you work.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)
![Python](https://img.shields.io/badge/python-3.12%2B-blue?style=flat-square)
![Made for](https://img.shields.io/badge/made%20for-Elastic%20Security-005571?style=flat-square&logo=elastic&logoColor=white)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)

**If this repo saves you time, a ⭐ star and 🍴 fork go a long way — it helps other detection engineers find it too.**

[Quick Start](#-quick-start) •
[What's Inside](#-whats-inside-this-repo) •
[Which One Should I Use?](#-which-notebook-should-i-use) •
[How It Works](#️-how-it-works) •
[FAQ](#-faq) •
[Contributing](#-contributing)

</div>

---

## 🧩 The Problem

Elastic maintains a huge, constantly-updated library of detection rules in the
[`elastic/detection-rules`](https://github.com/elastic/detection-rules) GitHub repository. Every rule lives there
as a `.toml` file — great for version control, unusable for direct Kibana import.

**Kibana's Security app does not accept `.toml`.** Its *Import rules* feature only understands
newline-delimited JSON (`.ndjson`) — the exact format Kibana itself produces when you export rules from the UI.

So if you want Elastic's prebuilt rules inside your own Kibana instance — especially in an **air-gapped**,
**offline**, or **restricted** environment — you need to convert `.toml` ➜ `.ndjson` yourself, at scale.

## ✅ The Solution — Three Tools, One Repo

Different workflows need different outputs, so this repo gives you three ways to do the conversion, all wrapping
the same officially documented Elastic CLI command (`export-rules-from-repo`) under the hood:

| # | Tool | Output |
|---|---|---|
| 1️⃣ | **`Elastic_Detection_Rules_Converter.ipynb`** | One `.ndjson` **per rule**, all zipped together |
| 2️⃣ | **`Elastic_Detection_Rules_Converter_SingleFile.ipynb`** | **One combined `.ndjson`** for the whole category |
| 3️⃣ | **`Elastic_Detection_Rules_Converter_EXE.ipynb`** + `elastic_rules_converter.py` | A **standalone command-line tool** (and optional `.exe`) that does either of the above with flags — no notebook required |

None of these re-implement Elastic's TOML parsing or validation logic — they all orchestrate Elastic's own CLI,
so results always match what Elastic's official tooling produces, even as their rule schema evolves.

---

## 📦 What's Inside This Repo

| File | Description |
|---|---|
| **`Elastic_Detection_Rules_Converter.ipynb`** | Clones the rules repo, installs the CLI, exports every rule in a category as its own `.ndjson`, zips them, downloads the archive. Best for cherry-picking or reviewing individual rules. |
| **`Elastic_Detection_Rules_Converter_SingleFile.ipynb`** | Same setup, but exports an entire category into **one combined `.ndjson`** — a single drag-and-drop import into Kibana. |
| **`Elastic_Detection_Rules_Converter_EXE.ipynb`** | Writes out `elastic_rules_converter.py`, demonstrates it as a parameterized CLI tool, packages it with PyInstaller, and shows how to get a genuine Windows `.exe` via GitHub Actions. |
| **`elastic_rules_converter.py`** | The standalone script itself — usable directly (`python elastic_rules_converter.py --category windows --mode single`) without opening any notebook at all. |
| **`README.md`** | You're reading it. |

---

## 🤔 Which Notebook Should I Use?

<details open>
<summary><strong>👉 Click to expand a quick decision guide</strong></summary>

- **"I want to review or import specific rules one at a time."**
  → `Elastic_Detection_Rules_Converter.ipynb` (per-rule `.ndjson`, zipped)

- **"I just want everything from one category in Kibana, fast, in one upload."**
  → `Elastic_Detection_Rules_Converter_SingleFile.ipynb` (one combined `.ndjson`)

- **"I don't want to touch Jupyter/Colab at all — give me a tool with flags, or better yet an `.exe`."**
  → `Elastic_Detection_Rules_Converter_EXE.ipynb` → `elastic_rules_converter.py` (and the Windows `.exe` via CI, see below)

</details>

---

## 🚀 Quick Start

### Option 1 — Per-rule export (zipped)

1. Open `Elastic_Detection_Rules_Converter.ipynb` in Colab and **Run all**.
2. Choose your category (default: `windows`).
3. Download `Windows_NDJSON.zip` — one `.ndjson` per rule inside.

### Option 2 — Single combined file

1. Open `Elastic_Detection_Rules_Converter_SingleFile.ipynb` in Colab and **Run all**.
2. Set `RULE_CATEGORY` in Step 6 (defaults to `windows`; use `"rules"` for every platform combined).
3. Download the single `windows_rules.ndjson` file.

### Option 3 — Standalone CLI tool

```bash
# One combined file
python elastic_rules_converter.py --category windows --mode single --zip

# One file per rule
python elastic_rules_converter.py --category linux --mode individual --zip

# Every platform, combined
python elastic_rules_converter.py --category rules --mode single --output all_rules.ndjson --zip
```

Requires a local clone of `elastic/detection-rules` with `poetry install` already run inside it — see
`Elastic_Detection_Rules_Converter_EXE.ipynb` for the one-time setup, or build/download the `.exe` (below).

For all three: import the result in Kibana via **Security → Manage → Rules → Detection rules (SIEM) → Import rules**.

---

## 🖇️ How It Works

```text
┌─────────────────────────────┐
│  elastic/detection-rules     │   ← official GitHub repo (source of truth)
│  (cloned fresh every run)    │
└──────────────┬────────────────┘
               │
               ▼
   rules/<category>/*.toml      ← e.g. rules/windows/*.toml
               │
               │  poetry run python -m detection_rules export-rules-from-repo
               │        -f <rule>.toml -o <rule>.ndjson    (per-rule mode)
               │        -d <category>/ -o <combined>.ndjson (single-file mode)
               ▼
   .ndjson output (one file per rule, OR one combined file)
               │
               │  Stack Management → Rules → Import rules
               ▼
   Rules live in your Kibana Security app 🎉
```

All three tools in this repo are just different front-ends onto this same pipeline.

---

## 🖥️ The Standalone Tool & `.exe`, in Detail

`elastic_rules_converter.py` accepts:

| Flag | Description | Default |
|---|---|---|
| `--repo` | Path to the cloned `elastic/detection-rules` repository | `detection-rules` |
| `--category` | Rule category under `rules/` (`windows`, `linux`, `macos`, `network`, `cloud`, …), or `rules` for every platform | `windows` |
| `--mode` | `single` (one combined `.ndjson`) or `individual` (one `.ndjson` per rule) | `individual` |
| `--output` | Output file (single mode) or directory (individual mode) | `<category>_rules.ndjson` / `<category>_NDJSON/` |
| `--zip` | Also zip the result | off |

### Getting a real `.exe`

`Elastic_Detection_Rules_Converter_EXE.ipynb` packages the script with
[PyInstaller](https://pyinstaller.org/) — but PyInstaller builds for whatever OS it runs on, so building it
inside Colab produces a **Linux** binary, not a Windows `.exe`, regardless of the file name.

For a genuine Windows executable, the notebook includes a ready-to-use **GitHub Actions workflow** that builds
it on a real `windows-latest` runner and publishes it to this repo's **Releases** page automatically on every
tagged push. Once that's set up, the whole "lazy researcher" experience becomes: **open Releases → download
`elastic_rules_converter.exe` → run it with flags.** No Python, no Colab, no build step on their end.

> **Honest caveat:** the `.exe` still needs `git` and `poetry` (plus a cloned `detection-rules` repo) present on
> the machine it runs on — it orchestrates Elastic's own CLI rather than reimplementing it, which is what keeps
> its output trustworthy. Fully bundling Elastic's entire `detection_rules` package into one truly
> dependency-free binary is listed as a future enhancement, not something promised today.

---

## ❓ FAQ

<details>
<summary><strong>Why three notebooks instead of one with a toggle?</strong></summary>

Each is meant to be opened, run top-to-bottom, and understood in one sitting — a single mega-notebook with modes
buried in variables is easy to misconfigure. Splitting them keeps each one focused and beginner-friendly, while
`elastic_rules_converter.py` gives power users the single unified tool.
</details>

<details>
<summary><strong>Does this modify or fork Elastic's official rules?</strong></summary>

No. Every tool here clones the repository fresh and runs Elastic's own unmodified CLI against it — none of them
alter rule content.
</details>

<details>
<summary><strong>Will this work in an air-gapped environment?</strong></summary>

Building/running these tools needs internet access to clone the repo and install dependencies. Once you have the
resulting `.ndjson` file(s), importing them into an air-gapped Kibana instance requires no further internet
access.
</details>

<details>
<summary><strong>How often should I re-run this?</strong></summary>

Elastic updates its rule set frequently. Re-run whichever tool you're using (they all clone the latest version
every time) whenever you want fresh rules — or fork this repo and wire the CLI script into a scheduled GitHub
Action for full automation.
</details>

---

## 🛠️ Troubleshooting

Each notebook has its own detailed troubleshooting table — the short version across all three:

| Problem | Fix |
|---|---|
| `poetry: command not found` | Restart the runtime after installing Poetry |
| `poetry install` fails | Check the Python version required in `detection-rules`' `pyproject.toml` |
| Kibana rejects the import | Re-check the exported rule count before importing — make sure the file isn't empty |
| Built `.exe` won't run on Windows | You built it in Colab (Linux) — use the GitHub Actions `windows-latest` workflow instead |

---

## 🤝 Contributing

Ideas for extending this further are very welcome:

- 🔁 A scheduled GitHub Action that re-runs the export nightly and commits fresh `.ndjson` files
- 📦 Support for exporting exception lists and action connectors alongside rules
- 🧳 A fully bundled, zero-dependency executable (vendoring `detection_rules` itself into the binary)
- 🧪 Automated tests validating exported NDJSON against Kibana's import schema

**To contribute:**
1. 🍴 Fork this repo
2. 🌱 Create a feature branch
3. ✅ Make your changes
4. 📬 Open a pull request

Found a bug or have a feature request? [Open an issue](../../issues) — every report helps.

---

## ⭐ Support This Project

If any of these three tools saved you from writing your own TOML-to-NDJSON converter:

- **Star** ⭐ this repo — the easiest way to say thanks, and it helps others discover it
- **Fork** 🍴 it and adapt it to your own environment or rule categories
- **Share** it with your detection engineering / SOC team

<div align="center">

Made with 🛡️ for the detection engineering community.

</div>

---

## ⚖️ License & Disclaimer

This repository is an **independent automation wrapper** and is **not affiliated with, endorsed by, or
maintained by Elastic**. All three tools automate Elastic's own publicly documented CLI command
(`export-rules-from-repo`) from [`elastic/detection-rules`](https://github.com/elastic/detection-rules), which is
separately licensed by Elastic — refer to that repository's `LICENSE.txt` for terms governing the rules and CLI
code themselves.

This repository (the notebooks, script, and documentation) is released under the **MIT License**.
