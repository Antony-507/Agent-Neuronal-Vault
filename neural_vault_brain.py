#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     🧠 NEURAL VAULT BRAIN v1.0                             ║
║            Neural Binary Query Engine for Obsidian Vaults                  ║
║                                                                            ║
║  Universal Edition — Works with ANY AI coding assistant                    ║
║  Antigravity • Claude Code • OpenClaw • ChatGPT • Cursor • Copilot        ║
║                                                                            ║
║  Every .md note is a NEURON.                                               ║
║  Every [[WikiLink]] is a SYNAPSE.                                          ║
║  Every query fires a SIGNAL that propagates through the network.           ║
║  Result: 1 (activated) or 0 (inactive) per neuron.                        ║
║                                                                            ║
║  License: MIT                                                              ║
║  Repository: github.com/aandreve/neural-vault-brain                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import re
import sys
import json
import math
import unicodedata
from collections import defaultdict
from datetime import datetime

__version__ = "1.0.0"
__author__ = "Amir Andreve"

# Fix Windows console encoding for Unicode box-drawing characters
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
elif sys.platform == 'win32':
    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")

DEFAULT_CONFIG = {
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
    "exclude_patterns": [".obsidian", ".smart-env", "scripts", ".base", "node_modules", ".git"],
    "assistant_integration": {
        "mode": "standalone",
        "output_format": "text",
        "inject_context_header": True,
        "max_context_tokens": 8000,
        "context_template": (
            "The following notes from the user's Obsidian vault are relevant "
            "to the current query:\n\n{activated_notes}\n\n"
            "Use this context to inform your response."
        )
    }
}


def load_config(config_path=None):
    """Load configuration from config.json or use defaults."""
    path = config_path or CONFIG_PATH
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                config = json.load(f)
            # Deep merge with defaults
            def merge(base, override):
                result = base.copy()
                for key, value in override.items():
                    if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                        result[key] = merge(result[key], value)
                    else:
                        result[key] = value
                return result
            return merge(DEFAULT_CONFIG, config)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"  ⚠️  Config parse error: {e}. Using defaults.", file=sys.stderr)
    return DEFAULT_CONFIG.copy()


# ═══════════════════════════════════════════════════════════════════════════════
# NEURON — Representation of a single .md note
# ═══════════════════════════════════════════════════════════════════════════════

class Neuron:
    """
    A neuron represents a single .md note in the vault.

    Attributes:
        filename      — File name (without path)
        filepath      — Absolute file path
        tags          — List of #tag annotations extracted from content
        title         — Primary title (first H1 heading or filename)
        content       — Full text content of the file
        wikilinks     — List of outgoing [[WikiLink]] targets (synaptic connections)
        signal        — Binary signal: 1 (activated/relevant) or 0 (inactive/irrelevant)
        raw_score     — Weighted score before thresholding (0.0 to 1.0)
        activated_by  — Key of the note that propagated activation (None if direct)
        depth         — Propagation depth at which this neuron was activated (0 = direct)
    """
    __slots__ = [
        'filename', 'filepath', 'tags', 'title', 'content',
        'wikilinks', 'signal', 'raw_score', 'activated_by', 'depth'
    ]

    def __init__(self, filename, filepath, content):
        self.filename = filename
        self.filepath = filepath
        self.content = content
        self.tags = self._extract_tags()
        self.title = self._extract_title()
        self.wikilinks = self._extract_wikilinks()
        self.signal = 0
        self.raw_score = 0.0
        self.activated_by = None
        self.depth = -1

    def _extract_tags(self):
        """Extract #tag annotations from content (excluding markdown headings)."""
        tags = set()
        for match in re.finditer(r'(?:^|\s)#([a-zA-Z0-9_\-\u00C0-\u024F]+)', self.content):
            tag = match.group(1).lower()
            tags.add(tag)
        return list(tags)

    def _extract_title(self):
        """Extract primary title: first H1 heading or filename as fallback."""
        match = re.search(r'^#\s+(.+)$', self.content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return os.path.splitext(self.filename)[0].replace('-', ' ').replace('_', ' ')

    def _extract_wikilinks(self):
        """Extract all [[WikiLink]] targets from content."""
        links = set()
        for match in re.finditer(r'\[\[([^\]|]+?)(?:\|[^\]]+?)?\]\]', self.content):
            links.add(match.group(1).strip())
        return list(links)

    def __repr__(self):
        return f"Neuron({self.filename}, signal={self.signal}, score={self.raw_score:.3f})"


# ═══════════════════════════════════════════════════════════════════════════════
# NEURAL VAULT BRAIN — Core Engine
# ═══════════════════════════════════════════════════════════════════════════════

class NeuralVaultBrain:
    """
    Neural binary query engine for Obsidian vaults.

    Architecture:
        Input Layer        → Query tokenization
        Sensory Layer      → Load and parse all .md notes
        Hidden Layer       → Weighted scoring across 4 dimensions
        Threshold θ        → Binarization: score ≥ θ → 1, score < θ → 0
        Propagation        → Synaptic activation via [[WikiLinks]]
        Output Layer       → Report of activated/inactive neurons

    Usage:
        brain = NeuralVaultBrain()
        brain.load_vault()
        result = brain.query("my search terms")
        print(brain.generate_report(result))
    """

    def __init__(self, config=None):
        self.config = config or load_config()
        self.vault_path = self.config["vault_path"]
        self.weights = self.config["weights"]
        self.threshold = self.config["threshold"]
        self.synapse_bonus = self.config["synapse_bonus"]
        self.max_depth = self.config["max_propagation_depth"]
        self.exclude_patterns = self.config["exclude_patterns"]
        self.assistant_config = self.config.get("assistant_integration", {})

        self.neurons = {}
        self.inbound_links = defaultdict(set)
        self.total_notes = 0
        self.max_inbound = 1

    # ─── Sensory Layer: Vault Loading ───────────────────────────────────────

    def load_vault(self, vault_path=None):
        """Recursively scan the vault directory and create a Neuron per .md file."""
        if vault_path:
            self.vault_path = vault_path
        self.neurons.clear()
        self.inbound_links.clear()

        vault = os.path.abspath(self.vault_path)
        if not os.path.isdir(vault):
            raise FileNotFoundError(f"Vault directory not found: {vault}")

        for root, dirs, files in os.walk(vault):
            dirs[:] = [d for d in dirs if not any(
                pat in os.path.join(root, d) for pat in self.exclude_patterns
            )]
            for file in files:
                if not file.endswith(".md"):
                    continue
                if any(pat in file for pat in self.exclude_patterns):
                    continue
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                except (IOError, OSError):
                    continue
                key = os.path.splitext(file)[0]
                self.neurons[key] = Neuron(file, filepath, content)

        for key, neuron in self.neurons.items():
            for link in neuron.wikilinks:
                self.inbound_links[link].add(key)

        self.total_notes = len(self.neurons)
        self.max_inbound = max((len(v) for v in self.inbound_links.values()), default=1)
        return self.total_notes

    # ─── Input Layer: Tokenization ──────────────────────────────────────────

    @staticmethod
    def normalize_text(text):
        """Normalize text: remove accents, lowercase, strip special characters."""
        text = text.lower().strip()
        nfkd = unicodedata.normalize('NFKD', text)
        text = ''.join(c for c in nfkd if not unicodedata.combining(c))
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        return text

    def tokenize_query(self, query):
        """Tokenize and normalize the user's query."""
        normalized = self.normalize_text(query)
        return [t for t in normalized.split() if len(t) >= 2]

    # ─── Hidden Layer: Weighted Scoring ─────────────────────────────────────

    def _score_tags(self, neuron, tokens):
        """Dimension 1: Token match against #tag annotations."""
        if not neuron.tags:
            return 0.0
        normalized_tags = [self.normalize_text(tag) for tag in neuron.tags]
        hits = sum(1 for t in tokens if any(t in tag or tag in t for tag in normalized_tags))
        return min(hits / max(len(tokens), 1), 1.0)

    def _score_title(self, neuron, tokens):
        """Dimension 2: Token match against note title and filename."""
        combined = (
            self.normalize_text(neuron.title) + " " +
            self.normalize_text(os.path.splitext(neuron.filename)[0])
        )
        hits = sum(1 for t in tokens if t in combined)
        return min(hits / max(len(tokens), 1), 1.0)

    def _score_content(self, neuron, tokens):
        """Dimension 3: Log-normalized frequency of tokens in body text."""
        norm = self.normalize_text(neuron.content)
        word_count = len(norm.split()) or 1
        total = 0.0
        for token in tokens:
            count = norm.count(token)
            if count > 0:
                total += math.log(1 + count) / math.log(1 + word_count)
        cap = len(tokens) * (math.log(2) / math.log(1 + word_count)) if tokens else 1
        return min(total / max(cap, 0.001), 1.0)

    def _score_inbound_links(self, neuron, tokens):
        """Dimension 4: Popularity — inbound [[WikiLink]] count, normalized."""
        key = os.path.splitext(neuron.filename)[0]
        count = len(self.inbound_links.get(key, set()))
        return min(count / max(self.max_inbound, 1), 1.0)

    def score_neuron(self, neuron, tokens):
        """
        Compute weighted score for a neuron.

        Score = Σ (weight_i × dimension_i) for i in {tags, title, content, inbound_links}
        Each dimension is normalized to [0, 1]. Weights should sum to 1.0.
        """
        return (
            self.weights["tags"] * self._score_tags(neuron, tokens) +
            self.weights["title"] * self._score_title(neuron, tokens) +
            self.weights["content"] * self._score_content(neuron, tokens) +
            self.weights["inbound_links"] * self._score_inbound_links(neuron, tokens)
        )

    # ─── Threshold θ: Binarization ─────────────────────────────────────────

    def apply_threshold(self, score):
        """Apply threshold θ: returns 1 if score ≥ θ, else 0."""
        return 1 if score >= self.threshold else 0

    # ─── Synaptic Propagation ───────────────────────────────────────────────

    def propagate_activation(self, activated_keys, tokens, current_depth=0):
        """
        Propagate activation through [[WikiLinks]] (synapses).

        For each activated neuron (signal=1), traverse its outgoing WikiLinks
        and apply a decaying synaptic bonus to the linked notes' scores.
        If the new score exceeds θ, the linked note is activated.

        Recurses up to max_propagation_depth levels.
        """
        if current_depth >= self.max_depth:
            return []

        newly_activated = []
        for source_key in activated_keys:
            source = self.neurons.get(source_key)
            if not source:
                continue
            for target_key in source.wikilinks:
                target = self.neurons.get(target_key)
                if not target or target.signal == 1:
                    continue
                decay = 1.0 / (1.0 + current_depth * 0.5)
                new_score = target.raw_score + self.synapse_bonus * decay
                if self.apply_threshold(new_score):
                    target.signal = 1
                    target.raw_score = new_score
                    target.activated_by = source_key
                    target.depth = current_depth + 1
                    newly_activated.append(target_key)

        if newly_activated:
            deeper = self.propagate_activation(newly_activated, tokens, current_depth + 1)
            newly_activated.extend(deeper)
        return newly_activated

    # ─── Full Query Pipeline ────────────────────────────────────────────────

    def query(self, text):
        """
        Execute the full neural query pipeline.

        1. Tokenize query
        2. Score each neuron (weighted 4-dimensional scoring)
        3. Apply threshold θ → binary 1/0
        4. Propagate activation via synapses ([[WikiLinks]])
        5. Compile report

        Returns:
            dict with keys: 'activated', 'inactive', 'propagated', 'stats'
        """
        tokens = self.tokenize_query(text)
        if not tokens:
            return {"activated": [], "inactive": [], "propagated": [], "stats": {}}

        for n in self.neurons.values():
            n.signal = 0
            n.raw_score = 0.0
            n.activated_by = None
            n.depth = -1

        directly_activated = []
        for key, neuron in self.neurons.items():
            score = self.score_neuron(neuron, tokens)
            neuron.raw_score = score
            neuron.signal = self.apply_threshold(score)
            if neuron.signal == 1:
                neuron.depth = 0
                directly_activated.append(key)

        propagated = self.propagate_activation(directly_activated, tokens)

        activated, inactive = [], []
        for key, neuron in self.neurons.items():
            entry = {
                "filename": neuron.filename,
                "key": key,
                "signal": neuron.signal,
                "score": round(neuron.raw_score, 4),
                "title": neuron.title[:80],
                "tags": neuron.tags[:5],
                "activated_by": neuron.activated_by,
                "depth": neuron.depth,
                "wikilinks_out": len(neuron.wikilinks),
                "inbound_count": len(self.inbound_links.get(key, set()))
            }
            (activated if neuron.signal == 1 else inactive).append(entry)

        activated.sort(key=lambda x: x["score"], reverse=True)
        inactive.sort(key=lambda x: x["score"], reverse=True)

        stats = {
            "query": text,
            "tokens": tokens,
            "total_neurons": self.total_notes,
            "activated_count": len(activated),
            "inactive_count": len(inactive),
            "directly_activated": len(directly_activated),
            "propagated_count": len(propagated),
            "activation_rate": f"{len(activated)/max(self.total_notes,1)*100:.1f}%",
            "threshold": self.threshold,
            "timestamp": datetime.now().isoformat()
        }

        return {
            "activated": activated,
            "inactive": inactive,
            "propagated": propagated,
            "stats": stats
        }

    # ─── Context Injection for AI Assistants ────────────────────────────────

    def generate_context(self, result, max_tokens=None):
        """
        Generate injectable context for an AI assistant.

        Produces a formatted block of text containing the content of the
        most relevant activated neurons, suitable for injection into the
        assistant's system prompt or conversation context.

        Args:
            result: Output from query()
            max_tokens: Approximate token limit (chars * 0.25). Defaults to config.

        Returns:
            str: Formatted context block ready for injection.
        """
        max_tk = max_tokens or self.assistant_config.get("max_context_tokens", 8000)
        max_chars = max_tk * 4  # Rough chars-to-tokens ratio
        template = self.assistant_config.get(
            "context_template",
            "Relevant vault notes:\n\n{activated_notes}"
        )

        notes_text = []
        char_count = 0
        for entry in result["activated"]:
            neuron = self.neurons.get(entry["key"])
            if not neuron:
                continue
            header = f"### [{entry['signal']}] {neuron.filename} (score={entry['score']:.3f})\n"
            snippet = neuron.content[:2000]
            block = header + snippet + "\n\n---\n\n"
            if char_count + len(block) > max_chars:
                break
            notes_text.append(block)
            char_count += len(block)

        activated_notes = "".join(notes_text) if notes_text else "(No relevant notes found.)"
        return template.format(activated_notes=activated_notes)

    # ─── Report Generators ──────────────────────────────────────────────────

    def generate_report(self, result, format="text"):
        """Generate a human-readable text report."""
        stats = result["stats"]
        activated = result["activated"]
        inactive = result["inactive"]

        lines = [
            "",
            "=" * 78,
            "  🧠 NEURAL VAULT BRAIN — Activation Report",
            "=" * 78,
            "",
            f"  📝 Query:             \"{stats['query']}\"",
            f"  🔑 Tokens:            {stats['tokens']}",
            f"  🧪 Threshold θ:       {stats['threshold']}",
            f"  📊 Total neurons:     {stats['total_neurons']}",
            f"  ✅ Activated (1):     {stats['activated_count']} ({stats['activation_rate']})",
            f"     ├─ Direct:         {stats['directly_activated']}",
            f"     └─ Propagated:     {stats['propagated_count']}",
            f"  ❌ Inactive (0):      {stats['inactive_count']}",
            "",
            "─" * 78,
            "  ✅ ACTIVATED NEURONS (signal = 1)",
            "─" * 78,
        ]

        if activated:
            lines.append(f"  {'#':<4} {'SIG':<5} {'SCORE':<8} {'DEPTH':<7} {'NOTE'}")
            lines.append(f"  {'─'*3}  {'─'*3}  {'─'*6}  {'─'*5}  {'─'*50}")
            for i, n in enumerate(activated[:30], 1):
                d = f"D{n['depth']}" if n['depth'] >= 0 else "?"
                via = f" ← {n['activated_by']}" if n['activated_by'] else " (direct)"
                lines.append(f"  {i:<4} [ 1 ] {n['score']:<8.4f} {d:<7} {n['filename'][:45]}{via}")
        else:
            lines.append("  (no neurons reached threshold θ)")

        lines.append("")
        lines.append("─" * 78)
        lines.append("  ⚡ NEAR-MISS (highest-scoring inactive)")
        lines.append("─" * 78)

        near = [n for n in inactive if n["score"] > 0][:10]
        if near:
            lines.append(f"  {'#':<4} {'SIG':<5} {'SCORE':<8} {'NOTE'}")
            lines.append(f"  {'─'*3}  {'─'*3}  {'─'*6}  {'─'*50}")
            for i, n in enumerate(near, 1):
                lines.append(f"  {i:<4} [ 0 ] {n['score']:<8.4f} {n['filename'][:55]}")
        else:
            lines.append("  (all scoring notes were activated)")

        lines.append("")

        prop = [n for n in activated if n["activated_by"]]
        if prop:
            lines.append("─" * 78)
            lines.append("  🔗 SYNAPTIC PROPAGATION MAP")
            lines.append("─" * 78)
            for n in prop:
                lines.append(f"    {n['activated_by']}  ──→  {n['filename']}  (D{n['depth']}, score={n['score']:.4f})")
            lines.append("")

        lines += [
            "=" * 78,
            f"  ⏱️  {stats['timestamp']}",
            "=" * 78,
            ""
        ]
        return "\n".join(lines)

    def generate_markdown_report(self, result):
        """Generate a Markdown-formatted report."""
        stats = result["stats"]
        activated = result["activated"]
        inactive = result["inactive"]

        lines = [
            f"# 🧠 Neural Vault Brain — Query Report",
            f"",
            f"**Query:** `{stats['query']}`  ",
            f"**Tokens:** `{stats['tokens']}`  ",
            f"**Threshold θ:** `{stats['threshold']}`  ",
            f"**Timestamp:** `{stats['timestamp']}`  ",
            f"",
            f"## 📊 Statistics",
            f"| Metric | Value |",
            f"|:---|:---|",
            f"| Total neurons | {stats['total_neurons']} |",
            f"| Activated (1) | {stats['activated_count']} ({stats['activation_rate']}) |",
            f"| Direct | {stats['directly_activated']} |",
            f"| Propagated | {stats['propagated_count']} |",
            f"| Inactive (0) | {stats['inactive_count']} |",
            f"",
            f"## ✅ Activated Neurons (signal = 1)",
            f"| # | Signal | Score | Depth | Note | Activated by |",
            f"|:--|:--|:--|:--|:--|:--|",
        ]
        for i, n in enumerate(activated[:30], 1):
            via = n['activated_by'] or "direct"
            lines.append(f"| {i} | **1** | {n['score']:.4f} | D{n['depth']} | `{n['filename']}` | {via} |")

        near = [n for n in inactive if n["score"] > 0][:10]
        if near:
            lines += [
                f"",
                f"## ⚡ Near-Miss (top inactive)",
                f"| # | Signal | Score | Note |",
                f"|:--|:--|:--|:--|",
            ]
            for i, n in enumerate(near, 1):
                lines.append(f"| {i} | 0 | {n['score']:.4f} | `{n['filename']}` |")

        return "\n".join(lines)

    def generate_json_report(self, result):
        """Generate a JSON report (for programmatic consumption)."""
        return json.dumps(result, ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════════
# ASSISTANT INTEGRATION ADAPTERS
# ═══════════════════════════════════════════════════════════════════════════════

class AssistantAdapter:
    """
    Adapters for integrating Neural Vault Brain with different AI assistants.

    Each adapter knows how to format the query result in a way that is
    optimal for injection into that assistant's context window or prompt.

    Supported assistants:
        - antigravity  : Google Antigravity IDE (run_command integration)
        - claude-code  : Anthropic Claude Code (slash command / SKILL.md)
        - openclaw     : OpenClaw CLI agents
        - chatgpt      : OpenAI ChatGPT (system prompt injection)
        - cursor       : Cursor IDE (.cursorrules integration)
        - copilot      : GitHub Copilot (context files)
        - codex        : OpenAI Codex CLI
        - aider        : Aider CLI (--read integration)
        - custom       : Generic adapter with configurable template
    """

    @staticmethod
    def format_for_antigravity(brain, result):
        """Format for Antigravity CLI — concise text report for run_command."""
        return brain.generate_report(result)

    @staticmethod
    def format_for_claude_code(brain, result):
        """Format for Claude Code — context block for CLAUDE.md injection."""
        ctx = brain.generate_context(result)
        header = "<!-- Neural Vault Brain Context (auto-injected) -->\n"
        return header + ctx

    @staticmethod
    def format_for_openclaw(brain, result):
        """Format for OpenClaw — structured context for agent consumption."""
        return brain.generate_context(result)

    @staticmethod
    def format_for_chatgpt(brain, result):
        """Format for ChatGPT — system message context block."""
        ctx = brain.generate_context(result)
        return f"[VAULT CONTEXT START]\n{ctx}\n[VAULT CONTEXT END]"

    @staticmethod
    def format_for_cursor(brain, result):
        """Format for Cursor IDE — .cursorrules compatible block."""
        ctx = brain.generate_context(result)
        return f"# Vault Context (Neural Vault Brain)\n\n{ctx}"

    @staticmethod
    def format_for_generic(brain, result):
        """Generic format — works with any assistant."""
        return brain.generate_context(result)

    @classmethod
    def get_adapter(cls, assistant_name):
        """Get the appropriate formatting function for an assistant."""
        adapters = {
            "antigravity": cls.format_for_antigravity,
            "claude-code": cls.format_for_claude_code,
            "openclaw": cls.format_for_openclaw,
            "chatgpt": cls.format_for_chatgpt,
            "cursor": cls.format_for_cursor,
            "copilot": cls.format_for_generic,
            "codex": cls.format_for_generic,
            "aider": cls.format_for_generic,
            "windsurf": cls.format_for_generic,
            "custom": cls.format_for_generic,
        }
        return adapters.get(assistant_name.lower(), cls.format_for_generic)


# ═══════════════════════════════════════════════════════════════════════════════
# CLI — Interactive Mode & Direct Command Mode
# ═══════════════════════════════════════════════════════════════════════════════

USAGE = """
Usage:
  python neural_vault_brain.py                          Interactive REPL mode
  python neural_vault_brain.py "query"                  Direct query (text output)
  python neural_vault_brain.py --md "query"             Direct query (markdown)
  python neural_vault_brain.py --json "query"           Direct query (JSON)
  python neural_vault_brain.py --context "query"        Context block for AI injection
  python neural_vault_brain.py --assistant NAME "query" Formatted for specific assistant
  python neural_vault_brain.py --vault PATH "query"     Use a custom vault path
  python neural_vault_brain.py --config PATH "query"    Use a custom config file
  python neural_vault_brain.py --help                   Show this help message
  python neural_vault_brain.py --version                Show version

Supported assistants: antigravity, claude-code, openclaw, chatgpt, cursor,
                      copilot, codex, aider, windsurf, custom
"""


def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     🧠 NEURAL VAULT BRAIN v1.0                             ║
║            Neural Binary Query Engine for Obsidian Vaults                  ║
║                                                                            ║
║  Every .md = NEURON  |  Every [[WikiLink]] = SYNAPSE                       ║
║  signal = 1 (relevant)   |  signal = 0 (irrelevant)                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)


def main():
    args = list(sys.argv[1:])

    if "--help" in args or "-h" in args:
        print(USAGE)
        return
    if "--version" in args:
        print(f"Neural Vault Brain v{__version__}")
        return

    # Parse flags
    config_path = None
    vault_path = None
    output_format = "text"
    assistant_name = None

    if "--config" in args:
        idx = args.index("--config")
        config_path = args.pop(idx + 1)
        args.pop(idx)

    if "--vault" in args:
        idx = args.index("--vault")
        vault_path = args.pop(idx + 1)
        args.pop(idx)

    if "--md" in args:
        output_format = "markdown"
        args.remove("--md")
    elif "--json" in args:
        output_format = "json"
        args.remove("--json")
    elif "--context" in args:
        output_format = "context"
        args.remove("--context")

    if "--assistant" in args:
        idx = args.index("--assistant")
        assistant_name = args.pop(idx + 1)
        args.pop(idx)
        output_format = "assistant"

    config = load_config(config_path)
    if vault_path:
        config["vault_path"] = vault_path

    brain = NeuralVaultBrain(config)
    print_banner()
    print(f"  📂 Vault: {os.path.abspath(brain.vault_path)}")
    print(f"  ⏳ Loading neurons...")
    total = brain.load_vault()
    print(f"  ✅ {total} neurons loaded.\n")

    # Direct command mode
    query_text = " ".join(args) if args else None
    if query_text:
        result = brain.query(query_text)
        if output_format == "json":
            print(brain.generate_json_report(result))
        elif output_format == "markdown":
            print(brain.generate_markdown_report(result))
        elif output_format == "context":
            print(brain.generate_context(result))
        elif output_format == "assistant":
            adapter = AssistantAdapter.get_adapter(assistant_name or "custom")
            print(adapter(brain, result))
        else:
            print(brain.generate_report(result))
        return

    # Interactive REPL mode
    print("  Type your query and press Enter.")
    print("  Commands: 'quit', 'stats', 'config', 'help'\n")

    while True:
        try:
            query = input("  🧠 Query > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  👋 Goodbye!")
            break

        if not query:
            continue
        if query.lower() in ("quit", "exit", "q", "salir"):
            print("  👋 Goodbye!")
            break
        if query.lower() == "stats":
            print(f"\n  📊 Neurons loaded: {brain.total_notes}")
            print(f"  🔗 Max inbound: {brain.max_inbound}")
            print(f"  ⚙️  Threshold θ: {brain.threshold}")
            print(f"  ⚡ Synapse bonus: {brain.synapse_bonus}")
            print(f"  🔄 Max depth: {brain.max_depth}\n")
            continue
        if query.lower() == "config":
            print(f"\n  {json.dumps(config, ensure_ascii=False, indent=2)}\n")
            continue
        if query.lower() == "help":
            print("\n  Commands:")
            print("    <query>     — Search vault with neural activation")
            print("    stats       — Show brain statistics")
            print("    config      — Show current configuration")
            print("    quit        — Exit\n")
            continue

        result = brain.query(query)
        print(brain.generate_report(result))


if __name__ == "__main__":
    main()
