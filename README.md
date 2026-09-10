# 🧠 Neural Vault Brain

**A neural binary query engine for Obsidian vaults.**

Every `.md` note is a **neuron**. Every `[[WikiLink]]` is a **synapse**. Every query fires a **signal** that propagates through the network. Each neuron receives a binary classification: **`1` (relevant)** or **`0` (irrelevant)**.

Works with **any AI coding assistant**: Antigravity, Claude Code, OpenClaw, ChatGPT, Cursor, Copilot, Codex, Aider, Windsurf, and more.

---

## 🏗️ Architecture

```
                    ┌─────────────────────────────────┐
                    │       🔌 INPUT LAYER             │
                    │    User Query → Tokenization     │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │      👁️ SENSORY LAYER            │
                    │   Load all .md → Parse tags,     │
                    │   titles, content, wikilinks     │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │       🧠 HIDDEN LAYER            │
                    │  4-Dimensional Weighted Scoring   │
                    │                                  │
                    │  ┌──────────┐ ┌──────────┐       │
                    │  │ Tags 25% │ │Title 30% │       │
                    │  └──────────┘ └──────────┘       │
                    │  ┌──────────┐ ┌──────────┐       │
                    │  │Content25%│ │Links 20% │       │
                    │  └──────────┘ └──────────┘       │
                    │                                  │
                    │   Σ Weighted Score → Threshold θ  │
                    │   score ≥ 0.40 → 1 (activated)   │
                    │   score < 0.40 → 0 (inactive)    │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │    ⚡ SYNAPTIC PROPAGATION       │
                    │  Activated neurons propagate     │
                    │  via [[WikiLinks]] with decay    │
                    │  Up to 3 levels deep             │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │       📊 OUTPUT LAYER            │
                    │  Report: activated (1) neurons   │
                    │  Report: inactive (0) neurons    │
                    │  Synaptic propagation map        │
                    └─────────────────────────────────┘
```

## ⚡ Quick Start

```bash
# Clone
git clone https://github.com/aandreve/neural-vault-brain.git
cd neural-vault-brain

# Edit config.json — set your vault path
# "vault_path": "/path/to/your/obsidian/vault"

# Run interactive mode
python neural_vault_brain.py

# Direct query
python neural_vault_brain.py "machine learning transformers"

# Markdown output
python neural_vault_brain.py --md "project architecture"

# JSON output (for programmatic use)
python neural_vault_brain.py --json "database optimization"
```

**No dependencies required.** Pure Python 3.7+ stdlib only.

---

## 🤖 AI Assistant Integration

Neural Vault Brain can inject relevant vault context into **any** AI coding assistant:

```bash
# Generic context block
python neural_vault_brain.py --context "my query"

# Formatted for a specific assistant
python neural_vault_brain.py --assistant antigravity "classify WPF articles"
python neural_vault_brain.py --assistant claude-code "auth middleware"
python neural_vault_brain.py --assistant chatgpt "database schema"
python neural_vault_brain.py --assistant cursor "React components"
python neural_vault_brain.py --assistant openclaw "deployment pipeline"
```

### Supported Assistants

| Assistant | Integration Method | Flag |
|:---|:---|:---|
| **Antigravity** | `run_command` in IDE | `--assistant antigravity` |
| **Claude Code** | CLAUDE.md / slash command | `--assistant claude-code` |
| **OpenClaw** | Agent CLI context | `--assistant openclaw` |
| **ChatGPT** | System prompt injection | `--assistant chatgpt` |
| **Cursor** | .cursorrules context | `--assistant cursor` |
| **GitHub Copilot** | Context files | `--assistant copilot` |
| **Codex CLI** | Pipe input | `--assistant codex` |
| **Aider** | `--read` flag | `--assistant aider` |
| **Windsurf** | Context files | `--assistant windsurf` |
| **Custom** | Configurable template | `--assistant custom` |

### Integration Examples

**Antigravity IDE** — Add to your global rules:
```
Before answering questions about the vault, run:
python neural_vault_brain.py --assistant antigravity "USER_QUERY"
```

**Claude Code** — Use in a slash command or CLAUDE.md:
```bash
CONTEXT=$(python neural_vault_brain.py --context "my question")
# Inject $CONTEXT into your prompt
```

**Cursor IDE** — Pipe into .cursorrules:
```bash
python neural_vault_brain.py --assistant cursor "my topic" >> .cursorrules
```

---

## ⚙️ Configuration

Edit `config.json` to customize the brain:

```json
{
  "vault_path": "./vault",
  "weights": {
    "tags": 0.25,
    "title": 0.30,
    "content": 0.25,
    "inbound_links": 0.20
  },
  "threshold": 0.40,
  "synapse_bonus": 0.15,
  "max_propagation_depth": 3,
  "exclude_patterns": [".obsidian", ".git", "node_modules"]
}
```

### Scoring Dimensions

| Dimension | Weight | Description |
|:---|:---|:---|
| **Tags** | 0.25 | Match query tokens against `#hashtag` annotations |
| **Title** | 0.30 | Match against H1 heading and filename |
| **Content** | 0.25 | Log-normalized token frequency in body text |
| **Inbound Links** | 0.20 | Popularity: how many notes link to this note |

### Tuning Tips

| Goal | Action |
|:---|:---|
| More results | Lower `threshold` (e.g., 0.30) |
| Fewer, more precise results | Raise `threshold` (e.g., 0.50) |
| Wider propagation | Increase `max_propagation_depth` |
| Narrower propagation | Decrease `synapse_bonus` |
| Prioritize file names | Increase `weights.title` |
| Prioritize popular notes | Increase `weights.inbound_links` |

---

## 📊 Sample Output

```
==============================================================================
  🧠 NEURAL VAULT BRAIN — Activation Report
==============================================================================

  📝 Query:             "WPF classifier articles"
  🔑 Tokens:            ['wpf', 'classifier', 'articles']
  🧪 Threshold θ:       0.4
  📊 Total neurons:     427
  ✅ Activated (1):     12 (2.8%)
     ├─ Direct:         5
     └─ Propagated:     7
  ❌ Inactive (0):      415

──────────────────────────────────────────────────────────────────────────────
  ✅ ACTIVATED NEURONS (signal = 1)
──────────────────────────────────────────────────────────────────────────────
  #    SIG   SCORE    DEPTH   NOTE
  ───  ───   ──────   ─────   ──────────────────────────────────────────────
  1    [ 1 ] 0.8234   D0      SUBRAMA-WPF-CLASIFICADOR.md (direct)
  2    [ 1 ] 0.7156   D0      algoritmo-clasificacion-jerarquica.md (direct)
  3    [ 1 ] 0.5521   D1      auditoria-logica-sistema-clasificacion.md ← SUBRAMA-WPF-CLASIFICADOR
  ...
```

---

## 🧬 How It Works

1. **Tokenization**: Your query is normalized (lowercased, accent-stripped) and split into tokens.
2. **Scoring**: Each note is scored across 4 weighted dimensions. Scores are normalized to `[0, 1]`.
3. **Thresholding**: If `Σ(weight × dimension) ≥ θ`, the neuron fires: `signal = 1`.
4. **Propagation**: Activated neurons propagate a decaying bonus through their `[[WikiLinks]]`. If a linked note's new score exceeds θ, it also fires — up to `max_propagation_depth` levels deep.
5. **Reporting**: Results are sorted by score and formatted as text, markdown, JSON, or injectable context.

---

## 📁 Project Structure

```
neural-vault-brain/
├── neural_vault_brain.py   # Core engine + CLI (zero dependencies)
├── config.json             # Editable configuration
├── README.md               # This file
└── LICENSE                 # MIT License
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE).

---

## 🙏 Credits

Created by **Amir Andreve** — powered by Antigravity IDE.

Inspired by neural network architectures applied to knowledge management. Built for the Obsidian community and the AI-assisted development ecosystem.
