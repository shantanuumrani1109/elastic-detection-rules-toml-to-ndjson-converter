<div align="center">

# 🛡️ Elastic Detection Rules → Kibana NDJSON Converter

### Turn Elastic's official `.toml` detection rules into ready-to-import Kibana `.ndjson` files — in one click.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)
![Python](https://img.shields.io/badge/python-3.12%2B-blue?style=flat-square)
![Made for](https://img.shields.io/badge/made%20for-Elastic%20Security-005571?style=flat-square&logo=elastic&logoColor=white)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)
![Maintained](https://img.shields.io/badge/maintained-yes-success?style=flat-square)

**If this repo saves you time, a ⭐ star and 🍴 fork go a long way — it helps other detection engineers find it too.**

[Quick Start](#-quick-start) •
[What's Inside](#-whats-inside-this-repo) •
[How It Works](#️-how-it-works) •
[Usage Guide](#-usage-guide) •
[FAQ](#-faq) •
[Contributing](#-contributing)

</div>

---

## 🧩 The Problem

Elastic maintains a huge, constantly-updated library of detection rules in the
[`elastic/detection-rules`](https://github.com/elastic/detection-rules) GitHub repository. Every rule lives there
as a `.toml` file — great for version control, terrible for actually loading into Kibana.

**Kibana's Security app does not accept `.toml`.** Its *Import rules* feature only understands
newline-delimited JSON (`.ndjson`) — the exact format Kibana itself produces when you export rules from the UI.

So if you want Elastic's prebuilt rules inside your own Kibana instance — especially in an **air-gapped**,
**offline**, or **restricted** environment without direct access to Elastic's automatic rule-update service — you
need to convert `.toml` ➜ `.ndjson` yourself, at scale, for hundreds of rules at a time.

## ✅ The Solution

This repo contains a single, fully-documented, **copy-paste-and-run** Google Colab notebook that automates the
entire conversion pipeline:

```
elastic/detection-rules (GitHub)  →  clone  →  install official CLI  →  export every rule  →  zip  →  download
```

No manual TOML parsing. No writing your own converter. It's a thin, transparent wrapper around **Elastic's own,
officially documented CLI command** (`export-rules-from-repo`), so it stays correct as Elastic's rule schema
evolves.

---

## 📦 What's Inside This Repo

| File | Description |
|---|---|
| **`ElasticDetectionRulesConverter-[Batch Conversion of Multiple TOML Files to NDJSON Files].ipynb.ipynb`** | The star of the show. A step-by-step Jupyter/Colab notebook — clone the rules repo, install the CLI, export every Windows rule as an individual `.ndjson`, zip it, and download it. Fully commented, with explanations, a troubleshooting table, and a Kibana import walkthrough baked in. |
| **`README.md`** | You're reading it. |

### 🔍 Inside the notebook

The notebook is organized into clearly numbered, self-contained steps so you always know exactly where you are:

| # | Step | What it does |
|---|---|---|
| 📖 | Overview | Explains *what* Elastic Detection Rules are and *why* TOML → NDJSON conversion is necessary |
| ⚙️ | How It Works | A one-glance pipeline diagram of the whole process |
| ✅ | Prerequisites | What you need before running (spoiler: just a browser, if using Colab) |
| 1️⃣ | Install Python Dependencies | Installs `requests` and `toml` helper libraries |
| 2️⃣ | Clone the Repository | Pulls the latest `elastic/detection-rules` from GitHub |
| — | Change Directory | Moves the notebook's working directory into the cloned repo |
| 3️⃣ | Install Poetry | Installs Elastic's dependency manager |
| 4️⃣ | Install Project Dependencies | Installs the exact CLI dependencies via `poetry install` |
| 5️⃣ | Verify the CLI | Confirms the `detection_rules` CLI is working |
| 6️⃣ | Choose the Category | Lists every available rule category (`windows`, `linux`, `macos`, `network`, `cloud`, …) |
| 7️⃣ | Export Every Windows Rule | Loops through every `.toml` file and exports it to its own `.ndjson` |
| 8️⃣ | Verify the Files | Confirms the export worked and previews the output |
| 9️⃣ | Zip the Folder | Bundles every `.ndjson` into one `.zip` |
| 🔟 | Download the ZIP | Downloads the archive straight to your machine |
| 📥 | Importing into Kibana | A guided walkthrough for importing the result into your Kibana instance |
| 📚 | References | Links to Elastic's official docs and CLI reference |

---

## 🚀 Quick Start

1. **Click the badge below** (or open `Elastic_Detection_Rules_Converter.ipynb` in any Jupyter environment):

   [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/)

2. **Run every cell from top to bottom** — `Runtime → Run all` in Colab.
3. In **Step 6**, note which rule categories are available (`windows`, `linux`, `macos`, `network`, `cloud`, …).
4. **Step 7** exports every `.toml` rule under `rules/windows` into its own `.ndjson` file. Want a different
   category? Just change `RULES_DIR` and `OUTPUT_DIR` in that cell — e.g.:
   ```python
   RULES_DIR = "rules/linux"
   OUTPUT_DIR = "Linux_NDJSON"
   ```
5. **Step 10** downloads a `.zip` containing every converted rule.
6. In Kibana: **Security → Manage → Rules → Detection rules (SIEM) → Import rules**, then drop in your `.ndjson`
   file(s).

That's it — no local Python setup, no cloning anything by hand.

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
               │  poetry run python -m detection_rules
               │        export-rules-from-repo -f <rule>.toml -o <rule>.ndjson
               ▼
   <Category>_NDJSON/*.ndjson   ← one Kibana-importable file per rule
               │
               │  shutil.make_archive
               ▼
      <Category>_NDJSON.zip     ← downloadable bundle
               │
               │  Stack Management → Rules → Import rules
               ▼
   Rules live in your Kibana Security app 🎉
```

The conversion itself is performed entirely by **Elastic's own CLI** — this notebook just orchestrates it, so you
always get results that match what Elastic officially supports.

---

## 📘 Usage Guide

### Running in Google Colab (recommended)

- Zero setup. Everything — Python, Poetry, git — is installed inside the Colab cell execution.
- Free GPU/CPU runtime is more than enough; this is a lightweight I/O and subprocess task.

### Running locally (Jupyter / VS Code / JupyterLab)

- Requires `git`, Python 3.12+ (match whatever `elastic/detection-rules`'s `pyproject.toml` specifies), and
  internet access.
- The `google.colab` download cell (Step 10) is Colab-specific — locally, just grab the `.zip` straight from your
  working directory instead.

### Targeting a different rule category

By default, the notebook exports the **Windows** rule set. To export another category (or all of them), edit the
variables at the top of **Step 7**:

```python
RULES_DIR = "rules/linux"      # or rules/macos, rules/network, rules/cloud, etc.
OUTPUT_DIR = "Linux_NDJSON"
```

Re-run Steps 7–10 for each category you want.

### Importing into Kibana

1. Open **Kibana → Security → Manage → Rules → Detection rules (SIEM)**.
2. Click **Import rules**.
3. Drag in the `.ndjson` file(s) from your unzipped folder.
4. Optionally enable **overwrite on conflicting `rule_id`** if you're re-importing an update.
5. Click **Import** and verify the rule count.

---

## ❓ FAQ

<details>
<summary><strong>Why not just export the whole rules/ directory into one giant NDJSON?</strong></summary>

You can! Point `RULES_DIR` at `rules/` instead of `rules/windows` if you want everything. This notebook exports
**one file per rule** by default because it makes it easy to cherry-pick individual rules for import, review, or
version control.
</details>

<details>
<summary><strong>Does this modify or fork Elastic's official rules?</strong></summary>

No. It clones the repository fresh, runs Elastic's own unmodified CLI against it, and does not alter any rule
content.
</details>

<details>
<summary><strong>Will this work in an air-gapped environment?</strong></summary>

The notebook itself needs internet access to clone the repo and install dependencies. Once you have the resulting
`.ndjson` files, though, importing them into an air-gapped Kibana instance requires no further internet access.
</details>

<details>
<summary><strong>How often should I re-run this?</strong></summary>

Elastic updates its rule set frequently. Re-run the notebook (it always clones the latest version) whenever you
want the newest rules — or fork this repo and wire it into a scheduled GitHub Action for full automation.
</details>

---

## 🛠️ Troubleshooting

Full troubleshooting table lives inside the notebook — but the short version:

| Problem | Fix |
|---|---|
| `poetry: command not found` | Restart the runtime after installing Poetry |
| `poetry install` fails | Check the Python version required in `detection-rules`' `pyproject.toml` |
| Kibana rejects the import | Re-check the `Exported`/`Failed` counts from the export step — make sure the file isn't empty |

---

## 🤝 Contributing

Ideas for making this even more useful are very welcome:

- 🔁 A scheduled GitHub Action that re-runs the export nightly and commits fresh `.ndjson` files
- 📦 Support for exporting exception lists and action connectors alongside rules
- 🧪 Automated tests validating exported NDJSON against Kibana's import schema

**To contribute:**
1. 🍴 Fork this repo
2. 🌱 Create a feature branch
3. ✅ Make your changes
4. 📬 Open a pull request

Found a bug or have a feature request? [Open an issue](../../issues) — every report helps.

---

## ⭐ Support This Project

If this notebook saved you from writing your own TOML-to-NDJSON converter:

- **Star** ⭐ this repo — it's the easiest way to say thanks and helps others discover it
- **Fork** 🍴 it and adapt it to your own environment or rule categories
- **Share** it with your detection engineering / SOC team

<div align="center">

### ⭐ Star History

If you found this useful, consider starring — every star helps this reach more security teams!

</div>

---

## ⚖️ License & Disclaimer

This repository is an **independent automation wrapper** and is **not affiliated with, endorsed by, or
maintained by Elastic**. It automates Elastic's own publicly documented CLI command
(`export-rules-from-repo`) from [`elastic/detection-rules`](https://github.com/elastic/detection-rules), which is
separately licensed by Elastic — refer to that repository's `LICENSE.txt` for terms governing the rules and CLI
code themselves.

This repository (the notebook and documentation) is released under the **MIT License**.

<div align="center">

Made with 🛡️ for the detection engineering community.

</div>
