# 🧠 Neural Vault Brain v2.0

**A neural binary query engine for Obsidian vaults with Local AI (RAG) capabilities.**

Every `.md` note is a **neuron**. Every `[[WikiLink]]` is a **synapse**. Every query fires a **signal** that propagates through the network. Each neuron receives a binary classification: **`1` (relevant)** or **`0` (irrelevant)**.

Works with **any AI coding assistant**: Antigravity, Claude Code, OpenClaw, ChatGPT, Cursor, Copilot, Codex, Aider, Windsurf, and more.

---

## 🏗️ Architecture (v2.0)

```
                    ┌─────────────────────────────────┐
                    │       🔌 INPUT LAYER             │
                    │   User Query → Tokenization      │
                    │   + Inhibitory Token Filter (-)  │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │      👁️ SENSORY LAYER            │
                    │  Instant Load via Cache (LTM)    │
                    │  Parse tags, titles, content,    │
                    │  and wikilinks from .md notes    │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │       🧠 HIDDEN LAYER            │
                    │  4-Dimensional Weighted Scoring  │
                    │                                  │
                    │  ┌──────────┐ ┌──────────┐       │
                    │  │ Tags 25% │ │Title 30% │       │
                    │  └──────────┘ └──────────┘       │
                    │  ┌──────────┐ ┌──────────┐       │
                    │  │TF-IDF 25%│ │Links 20% │       │
                    │  └──────────┘ └──────────┘       │
                    │                                  │
                    │   Σ Weighted Score → Threshold θ │
                    │   score ≥ 0.40 → 1 (activated)   │
                    │   score < 0.40 → 0 (inactive)    │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │    ⚡ SYNAPTIC PROPAGATION       │
                    │  Bidirectional (Forward/Backward)│
                    │  Weighted by Synaptic Thickness  │
                    │  Up to 3 levels deep             │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │       📊 OUTPUT LAYER            │
                    │  Report: activated (1) neurons   │
                    │  Mode --ask: Local AI RAG Query  │
                    └─────────────────────────────────┘
```

## ✨ New in v2.0

- **Local AI RAG (`--ask`)**: The neural engine now seamlessly connects to local AIs (like Ollama or LM Studio) to chat with your vault using Neural Retrieval-Augmented Generation.
- **Long-Term Memory Cache**: Vaults now load instantaneously. The engine detects file modifications and only parses updated notes.
- **TF-IDF Mathematical Scoring**: Query tokens are weighed by their rarity in your vault. Common words carry little weight, while specific technical terms carry massive weight.
- **Bidirectional Propagation**: Neural signals now flow forward (through outgoing links) and backward (through incoming links).
- **Inhibitory Tokens**: Prefix any search word with `-` (e.g., `-wpf`) to completely inhibit and shut down any neuron containing that word.
- **Synaptic Thickness**: Links in titles or with aliases are treated as stronger synapses, propagating larger neural bonuses.

---

## ⚡ Quick Start

```bash
# Clone
git clone https://github.com/aandreve/neural-vault-brain.git
cd neural-vault-brain

# Edit neural_config.json — set your vault path
# "vault_path": "/path/to/your/obsidian/vault"

# Run interactive mode
python scripts/neural_vault_brain.py

# Chat with your vault via Local AI (requires Ollama/LM Studio running)
python scripts/neural_vault_brain.py --ask "Resume my recent architecture notes"

# Direct search query with inhibitory tokens
python scripts/neural_vault_brain.py "machine learning -python"

# JSON output (for programmatic use)
python scripts/neural_vault_brain.py --json "database optimization"
```

**No dependencies required.** Pure Python 3.7+ stdlib only.

---

## 🤖 AI Assistant Integration

Neural Vault Brain can inject relevant vault context into **any** AI coding assistant. Because this is the Open Source generic version, you can adapt it to any tool.

```bash
# Generic context block
python scripts/neural_vault_brain.py "my query"
```

### Integration Examples

**Claude Code** — Use in a slash command or CLAUDE.md:
```bash
CONTEXT=$(python scripts/neural_vault_brain.py "my question")
# Inject $CONTEXT into your prompt
```

**Cursor IDE** — Pipe into .cursorrules:
```bash
python scripts/neural_vault_brain.py "my topic" >> .cursorrules
```

---

## ⚙️ Configuration

Edit `neural_config.json` to customize the brain:

```json
{
  "vault_path": "C:\\ruta\\a\\tu\\vault",
  "weights": {
    "tags": 0.25,
    "title": 0.30,
    "content": 0.25,
    "inbound_links": 0.20
  },
  "threshold": 0.40,
  "synapse_bonus": 0.15,
  "backward_synapse_bonus": 0.05,
  "max_propagation_depth": 3,
  "exclude_patterns": [".obsidian", ".smart-env", "scripts", ".base"],
  "local_ai": {
    "provider": "ollama",
    "endpoint": "http://localhost:11434/api/generate",
    "model": "llama3",
    "system_prompt": "Eres un asistente experto llamado Neural Brain...",
    "context_max_chars": 12000
  }
}
```

### Tuning Tips

| Goal | Action |
|:---|:---|
| More search results | Lower `threshold` (e.g., 0.30) |
| Fewer, precise results | Raise `threshold` (e.g., 0.50) |
| Wider propagation | Increase `max_propagation_depth` |
| Increase RAG context | Increase `local_ai.context_max_chars` |

---

## 🎓 How to "Train" Your Vault (For Future Customizable AI)

Because this is a structural network rather than a pre-trained LLM, **your Obsidian vault is the neural network**. "Training" it means improving your notes and the connections between them so that in the future, your Personal AI can reason perfectly over your second brain.

Every time you write in Obsidian, you are wiring the brain. Here are the 4 ways to train it:

### 1. Strengthen Synapses (Improve Propagation)
The system propagates activation through `[[WikiLinks]]`. 
* **How to train:** Whenever you create a new note, link it to existing relevant notes. If Note A links to Note B, any query that activates Note A will send an electrical "bonus" to Note B.
* *Bonus (Synaptic Thickness):* Links inside Header blocks (`# `) carry double the weight. Use headers for your most important links!

### 2. Sharpen Receptors (Use Tags)
Tags are heavily weighted (25%) because they act as direct conceptual receptors.
* **How to train:** Add precise `#tags` at the beginning or end of your notes.
* *Example:* Tagging a note with `#sql #auth #backend` ensures that those specific tokens will instantly fire the neuron when queried.

### 3. Create "Hub" Neurons (MOCs & Indices)
Dimension 4 measures inbound links (Popularity, 20% weight). A note that many other notes point to becomes a **hyper-sensitive neuron** that fires easily.
* **How to train:** Keep your Index notes or Maps of Content (MOCs) updated. The more notes that point to your `[[000-INDEX]]` or `[[Python-Snippets]]` note, the stronger that region of the brain becomes.

### 4. Provide Clean Context for Local AI
When using the `--ask` command, the AI relies entirely on the content of the activated neurons.
* **How to train:** Write your notes in clear, declarative sentences. Avoid ambiguous pronouns. A note that explicitly states "The server uses Nginx for reverse proxying" is infinitely better for AI ingestion than "We use it for proxying".

---

## 📁 Project Structure

```
neural-vault-brain/
├── scripts/
│   ├── neural_vault_brain.py   # Core engine + CLI + RAG (zero dependencies)
│   └── neural_config.json      # Editable configuration
├── README.md                   # This file
└── LICENSE                     # MIT License
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE).

---

## 🙏 Credits

Created by **Amir Andreve**.
Inspired by neural network architectures applied to knowledge management. Built for the Obsidian community and the AI-assisted development ecosystem.
