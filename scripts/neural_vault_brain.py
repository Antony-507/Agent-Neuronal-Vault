#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     🧠 NEURAL VAULT BRAIN v2.0                             ║
║            Motor de Consulta Neuronal Binario para Obsidian                ║
║                                                                            ║
║  Versión: Open Source Version (Customizable)                               ║
║  Compatible con: OpenClaw, Claude Code, ChatGPT, Antigravity, etc.         ║
║                                                                            ║
║  Características v2.0:                                                     ║
║  - Caché de Memoria a Largo Plazo (Instantáneo)                            ║
║  - Propagación Bidireccional (Forward/Backward)                            ║
║  - Inhibición Neuronal (Filtros negativos ej. -palabra)                    ║
║  - Grosor Sináptico (Links en títulos pesan más)                           ║
║  - Matemáticas TF-IDF para rareza de tokens                                ║
║  - Modo RAG `--ask` para IAs Locales (Ollama, LM Studio, etc.)             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import re
import sys
import json
import math
import unicodedata
import urllib.request
import urllib.error
from collections import defaultdict
from datetime import datetime

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
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "neural_config.json")
CACHE_PATH = os.path.join(SCRIPT_DIR, "brain_cache.json")

DEFAULT_CONFIG = {
    "vault_path": r"C:\ruta\a\tu\vault",
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
        "system_prompt": "Eres un asistente experto llamado Neural Brain. Usa el contexto provisto (extraído de la bóveda personal del usuario) para responder la pregunta de forma precisa y concisa. Si la respuesta no está en el contexto, usa tu conocimiento general, pero dale prioridad absoluta al contexto.",
        "context_max_chars": 12000
    }
}


def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
                elif isinstance(value, dict):
                    for subkey, subval in value.items():
                        if subkey not in config[key]:
                            config[key][subkey] = subval
            return config
        except (json.JSONDecodeError, KeyError):
            pass
    return DEFAULT_CONFIG.copy()


def normalize_text(text):
    text = text.lower().strip()
    nfkd = unicodedata.normalize('NFKD', text)
    text = ''.join(c for c in nfkd if not unicodedata.combining(c))
    text = re.sub(r'[^a-z0-9\s-]', ' ', text)
    return text

# ═══════════════════════════════════════════════════════════════════════════════
# NEURONA — Representación de una nota .md
# ═══════════════════════════════════════════════════════════════════════════════

class Neuron:
    __slots__ = [
        'filename', 'filepath', 'tags', 'title', 'content',
        'wikilinks', 'signal', 'raw_score', 'activated_by', 'depth', 'content_tokens_set'
    ]

    def __init__(self, filename, filepath, content):
        self.filename = filename
        self.filepath = filepath
        self.content = content
        self.tags = self._extract_tags()
        self.title = self._extract_title()
        self.wikilinks = self._extract_wikilinks()
        self.content_tokens_set = set(normalize_text(content).split())
        
        self.signal = 0
        self.raw_score = 0.0
        self.activated_by = None
        self.depth = -1

    def _extract_tags(self):
        tags = set()
        for match in re.finditer(r'(?:^|\s)#([a-zA-Z0-9_\-áéíóúñü]+)', self.content):
            tag = match.group(1).lower()
            if not tag.startswith('#'):
                tags.add(tag)
        return list(tags)

    def _extract_title(self):
        match = re.search(r'^#\s+(.+)$', self.content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return os.path.splitext(self.filename)[0].replace('-', ' ').replace('_', ' ')

    def _extract_wikilinks(self):
        """Devuelve un diccionario {target: weight (Grosor Sináptico)}"""
        links = {}
        lines = self.content.split('\n')
        for line in lines:
            # Detectar si la línea es un heading
            is_heading = bool(re.match(r'^#+\s', line.strip()))
            
            for match in re.finditer(r'\[\[([^\]|]+?)(?:\|[^\]]+?)?\]\]', line):
                target = match.group(1).strip()
                has_alias = '|' in match.group(0)
                
                # Grosor Sináptico
                weight = 1.0
                if is_heading: weight += 1.0
                if has_alias: weight += 0.5
                
                # Guardar el mayor peso si ya existe
                if target not in links or weight > links[target]:
                    links[target] = weight
        return links

    def to_dict(self):
        return {
            "tags": self.tags,
            "title": self.title,
            "wikilinks": self.wikilinks,
            "content_tokens_set": list(self.content_tokens_set)
        }

    def from_dict(self, data):
        self.tags = data.get("tags", [])
        self.title = data.get("title", "")
        self.wikilinks = data.get("wikilinks", {})
        self.content_tokens_set = set(data.get("content_tokens_set", []))


# ═══════════════════════════════════════════════════════════════════════════════
# NEURAL VAULT BRAIN — Motor principal
# ═══════════════════════════════════════════════════════════════════════════════

class NeuralVaultBrain:
    def __init__(self, config=None):
        self.config = config or load_config()
        self.vault_path = self.config["vault_path"]
        self.weights = self.config["weights"]
        self.threshold = self.config["threshold"]
        self.synapse_bonus = self.config["synapse_bonus"]
        self.backward_synapse_bonus = self.config["backward_synapse_bonus"]
        self.max_depth = self.config["max_propagation_depth"]
        self.exclude_patterns = self.config["exclude_patterns"]

        self.neurons = {}           # filename_sin_ext -> Neuron
        self.inbound_links = defaultdict(dict)  # target -> {source: weight}
        self.total_notes = 0
        self.max_inbound = 1
        self.global_df = defaultdict(int) # Document Frequency para TF-IDF

    # ─── Capa Sensorial: Carga del Vault + Caché ────────────────────────────

    def load_vault(self):
        cache = {}
        if os.path.exists(CACHE_PATH):
            try:
                with open(CACHE_PATH, "r", encoding="utf-8") as f:
                    cache = json.load(f)
            except Exception:
                pass

        self.neurons.clear()
        self.inbound_links.clear()
        self.global_df.clear()

        new_cache = {}
        parsed_count = 0
        cached_count = 0

        for root, dirs, files in os.walk(self.vault_path):
            dirs[:] = [d for d in dirs if not any(pat in os.path.join(root, d) for pat in self.exclude_patterns)]

            for file in files:
                if not file.endswith(".md"): continue
                if any(pat in file for pat in self.exclude_patterns): continue

                filepath = os.path.join(root, file)
                key = os.path.splitext(file)[0]
                
                try:
                    mtime = os.path.getmtime(filepath)
                except OSError:
                    continue

                cache_key = filepath
                
                # Check cache
                if cache_key in cache and cache[cache_key]["mtime"] == mtime:
                    try:
                        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                        neuron = Neuron(file, filepath, content)
                        neuron.from_dict(cache[cache_key]["data"])
                        self.neurons[key] = neuron
                        new_cache[cache_key] = cache[cache_key]
                        cached_count += 1
                    except Exception:
                        pass # Fallback a parsear
                
                if key not in self.neurons:
                    # Parsear desde cero
                    try:
                        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                        neuron = Neuron(file, filepath, content)
                        self.neurons[key] = neuron
                        new_cache[cache_key] = {"mtime": mtime, "data": neuron.to_dict()}
                        parsed_count += 1
                    except Exception:
                        pass

        # Construir enlaces entrantes y calcular Document Frequency
        for key, neuron in self.neurons.items():
            for link, weight in neuron.wikilinks.items():
                self.inbound_links[link][key] = weight
            for token in neuron.content_tokens_set:
                self.global_df[token] += 1

        self.total_notes = len(self.neurons)
        if self.inbound_links:
            self.max_inbound = max(len(v) for v in self.inbound_links.values())
        else:
            self.max_inbound = 1

        # Guardar caché
        try:
            with open(CACHE_PATH, "w", encoding="utf-8") as f:
                json.dump(new_cache, f, ensure_ascii=False)
        except Exception:
            pass

        return self.total_notes, parsed_count, cached_count

    # ─── Capa de Entrada: Tokenización con Inhibición ───────────────────────

    def tokenize_query(self, query):
        tokens = []
        inhibitory_tokens = []
        
        words = query.lower().split()
        for word in words:
            if word.startswith('-') and len(word) > 1:
                inhibitory_tokens.append(normalize_text(word[1:]))
            else:
                norm = normalize_text(word)
                if len(norm) >= 2:
                    tokens.append(norm)
                    
        return tokens, inhibitory_tokens

    # ─── Capa Oculta: Scoring Ponderado (TF-IDF) ────────────────────────────

    def _score_tags(self, neuron, tokens):
        if not neuron.tags: return 0.0
        normalized_tags = [normalize_text(tag) for tag in neuron.tags]
        hits = sum(1 for t in tokens for tag in normalized_tags if t in tag or tag in t)
        return min(hits / max(len(tokens), 1), 1.0)

    def _score_title(self, neuron, tokens):
        combined = normalize_text(neuron.title) + " " + normalize_text(os.path.splitext(neuron.filename)[0])
        hits = sum(1 for t in tokens if t in combined)
        return min(hits / max(len(tokens), 1), 1.0)

    def _score_content_tfidf(self, neuron, tokens):
        normalized_content = normalize_text(neuron.content)
        content_len = len(normalized_content.split()) or 1
        total_tfidf = 0
        
        for token in tokens:
            tf = normalized_content.count(token)
            if tf > 0:
                tf_log = math.log(1 + tf) / math.log(1 + content_len)
                df = self.global_df.get(token, 1)
                idf = math.log(max(self.total_notes / df, 1.0))
                total_tfidf += tf_log * idf
                
        # Normalización gruesa
        max_possible = len(tokens) * (math.log(2) / math.log(1 + content_len)) * math.log(self.total_notes) if tokens else 1
        return min(total_tfidf / max(max_possible, 0.001), 1.0)

    def _score_inbound_links(self, neuron, tokens):
        key = os.path.splitext(neuron.filename)[0]
        inbound_count = len(self.inbound_links.get(key, {}))
        return min(inbound_count / max(self.max_inbound, 1), 1.0)

    def score_neuron(self, neuron, tokens, inhibitory_tokens):
        # 1. Chequear Inhibición Neuronal
        normalized_content = normalize_text(neuron.content)
        normalized_title = normalize_text(neuron.title)
        
        for itoken in inhibitory_tokens:
            if itoken in normalized_content or itoken in normalized_title or any(itoken in t for t in neuron.tags):
                return 0.0 # Inhibición total

        # 2. Scoring Normal
        s_tags = self._score_tags(neuron, tokens)
        s_title = self._score_title(neuron, tokens)
        s_content = self._score_content_tfidf(neuron, tokens)
        s_inbound = self._score_inbound_links(neuron, tokens)

        score = (
            self.weights["tags"] * s_tags +
            self.weights["title"] * s_title +
            self.weights["content"] * s_content +
            self.weights["inbound_links"] * s_inbound
        )
        return score

    # ─── Propagación Bidireccional ──────────────────────────────────────────

    def propagate_activation(self, activated_keys, tokens, current_depth=0):
        if current_depth >= self.max_depth: return []
        newly_activated = []

        for source_key in activated_keys:
            source_neuron = self.neurons.get(source_key)
            if not source_neuron: continue

            # A) Hacia adelante (Forward Synapses)
            for link_target, thickness in source_neuron.wikilinks.items():
                target_neuron = self.neurons.get(link_target)
                if not target_neuron or target_neuron.signal == 1: continue

                depth_decay = 1.0 / (1.0 + current_depth * 0.5)
                bonus = self.synapse_bonus * thickness * depth_decay
                new_score = target_neuron.raw_score + bonus

                if new_score >= self.threshold:
                    target_neuron.signal = 1
                    target_neuron.raw_score = new_score
                    target_neuron.activated_by = source_key
                    target_neuron.depth = current_depth + 1
                    newly_activated.append(link_target)

            # B) Hacia atrás (Backward Synapses)
            for backlink_source, thickness in self.inbound_links.get(source_key, {}).items():
                target_neuron = self.neurons.get(backlink_source)
                if not target_neuron or target_neuron.signal == 1: continue

                depth_decay = 1.0 / (1.0 + current_depth * 0.5)
                bonus = self.backward_synapse_bonus * thickness * depth_decay
                new_score = target_neuron.raw_score + bonus

                if new_score >= self.threshold:
                    target_neuron.signal = 1
                    target_neuron.raw_score = new_score
                    target_neuron.activated_by = f"← {source_key}" # Retro-activación
                    target_neuron.depth = current_depth + 1
                    newly_activated.append(backlink_source)

        if newly_activated:
            deeper = self.propagate_activation(newly_activated, tokens, current_depth + 1)
            newly_activated.extend(deeper)

        return newly_activated

    # ─── Pipeline Completo de Consulta ──────────────────────────────────────

    def query(self, text):
        tokens, inhibitory = self.tokenize_query(text)
        if not tokens:
            return {"activated": [], "inactive": [], "propagated": [], "stats": {}}

        for neuron in self.neurons.values():
            neuron.signal = 0
            neuron.raw_score = 0.0
            neuron.activated_by = None
            neuron.depth = -1

        directly_activated = []
        for key, neuron in self.neurons.items():
            score = self.score_neuron(neuron, tokens, inhibitory)
            neuron.raw_score = score
            if score >= self.threshold:
                neuron.signal = 1
                neuron.depth = 0
                directly_activated.append(key)

        propagated = self.propagate_activation(directly_activated, tokens)

        activated = []
        inactive = []
        for key, neuron in self.neurons.items():
            entry = {
                "filename": neuron.filename,
                "filepath": neuron.filepath,
                "signal": neuron.signal,
                "score": round(neuron.raw_score, 4),
                "title": neuron.title[:80],
                "tags": neuron.tags[:5],
                "activated_by": neuron.activated_by,
                "depth": neuron.depth,
                "wikilinks_count": len(neuron.wikilinks),
                "inbound_count": len(self.inbound_links.get(key, {}))
            }
            if neuron.signal == 1: activated.append(entry)
            else: inactive.append(entry)

        activated.sort(key=lambda x: x["score"], reverse=True)
        inactive.sort(key=lambda x: x["score"], reverse=True)

        stats = {
            "query": text,
            "tokens": tokens,
            "inhibitory_tokens": inhibitory,
            "total_neurons": self.total_notes,
            "activated_count": len(activated),
            "inactive_count": len(inactive),
            "directly_activated": len(directly_activated),
            "propagated_count": len(propagated),
            "activation_rate": f"{len(activated)/max(self.total_notes,1)*100:.1f}%",
            "threshold": self.threshold,
            "timestamp": datetime.now().isoformat()
        }

        return {"activated": activated, "inactive": inactive, "propagated": propagated, "stats": stats}

    # ─── Generación de Reportes ─────────────────────────────────────────────

    def generate_report(self, result, format="text"):
        stats = result["stats"]
        activated = result["activated"]
        inactive = result["inactive"]

        lines = []
        lines.append("")
        lines.append("=" * 78)
        lines.append("  🧠 NEURAL VAULT BRAIN v2.0 — Reporte de Activación Neuronal")
        lines.append("=" * 78)
        lines.append("")
        lines.append(f"  📝 Consulta:          \"{stats['query']}\"")
        lines.append(f"  🔑 Tokens:            {stats['tokens']}")
        if stats.get('inhibitory_tokens'):
            lines.append(f"  ⛔ Inhibidores:       {stats['inhibitory_tokens']}")
        lines.append(f"  🧪 Umbral θ:          {stats['threshold']}")
        lines.append(f"  📊 Total neuronas:    {stats['total_neurons']}")
        lines.append(f"  ✅ Activadas (1):     {stats['activated_count']} ({stats['activation_rate']})")
        lines.append(f"     ├─ Directas:       {stats['directly_activated']}")
        lines.append(f"     └─ Propagadas:     {stats['propagated_count']}")
        lines.append("")

        lines.append("─" * 78)
        lines.append("  ✅ NEURONAS ACTIVADAS (signal = 1)")
        lines.append("─" * 78)

        if activated:
            lines.append(f"  {'#':<4} {'SCORE':<7} {'DEPTH':<7} {'NOTA'}")
            lines.append(f"  {'─'*4} {'─'*7} {'─'*7} {'─'*50}")
            for i, n in enumerate(activated[:30], 1):
                depth_str = f"D{n['depth']}" if n['depth'] >= 0 else "?"
                via = f" ← {n['activated_by']}" if n['activated_by'] else " (directa)"
                lines.append(f"  {i:<4} {n['score']:<7.4f} {depth_str:<7} {n['filename'][:45]}{via}")
        else:
            lines.append("  (ninguna neurona alcanzó el umbral θ)")

        lines.append("")
        lines.append("=" * 78)
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# LOCAL AI RAG MODULE
# ═══════════════════════════════════════════════════════════════════════════════

def ask_local_ai(brain, query):
    """
    Realiza una búsqueda neuronal, ensambla un prompt gigante con el contexto,
    y consulta a una IA local (ej. Ollama o OpenAI-compatible).
    """
    print(f"\n  🧠 Iniciando Retrieval Neuronal para: '{query}'...")
    result = brain.query(query)
    activated = result["activated"]
    
    if not activated:
        print("  ⚠️ La red neuronal no encontró contexto relevante en el Vault.")
        context = "No hay contexto disponible en la bóveda."
    else:
        print(f"  ✅ {len(activated)} neuronas activadas. Ensamblando contexto...")
        context_parts = []
        current_chars = 0
        max_chars = brain.config["local_ai"].get("context_max_chars", 12000)
        
        # Tomamos las top notas
        for n in activated[:15]:
            neuron = brain.neurons[os.path.splitext(n['filename'])[0]]
            part = f"--- ARCHIVO: {neuron.filename} ---\n{neuron.content}\n\n"
            if current_chars + len(part) > max_chars:
                break
            context_parts.append(part)
            current_chars += len(part)
            
        context = "".join(context_parts)
    
    system_prompt = brain.config["local_ai"].get("system_prompt", "Eres un asistente experto.")
    model = brain.config["local_ai"].get("model", "llama3")
    endpoint = brain.config["local_ai"].get("endpoint", "http://localhost:11434/api/generate")
    provider = brain.config["local_ai"].get("provider", "ollama")
    
    prompt = f"Contexto de la bóveda del usuario:\n{context}\n\nPregunta del usuario: {query}"
    
    print(f"  🤖 Contactando IA Local ({provider} - {model}) vía {endpoint}...\n")
    print("  " + "─"*76)
    
    data = {}
    if provider == "ollama":
        data = {
            "model": model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": True
        }
    else: # openai_compatible
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "stream": True
        }
    
    req = urllib.request.Request(endpoint, data=json.dumps(data).encode('utf-8'))
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req) as response:
            sys.stdout.write("  ")
            for line in response:
                if line:
                    decoded = line.decode('utf-8')
                    try:
                        chunk = json.loads(decoded)
                        if provider == "ollama":
                            if "response" in chunk:
                                sys.stdout.write(chunk["response"])
                                sys.stdout.flush()
                        else:
                            if "choices" in chunk and len(chunk["choices"]) > 0:
                                delta = chunk["choices"][0].get("delta", {})
                                if "content" in delta:
                                    sys.stdout.write(delta["content"])
                                    sys.stdout.flush()
                    except json.JSONDecodeError:
                        if decoded.startswith("data: "):
                            try:
                                chunk = json.loads(decoded[6:])
                                if "choices" in chunk and len(chunk["choices"]) > 0:
                                    delta = chunk["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        sys.stdout.write(delta["content"])
                                        sys.stdout.flush()
                            except Exception:
                                pass
        print("\n  " + "─"*76 + "\n")
    except urllib.error.URLError as e:
        print(f"\n  ❌ Error conectando a la IA Local: {e.reason}")
        print("  Asegúrate de que Ollama, LM Studio o tu IA local está encendida y el endpoint es correcto en config.json.\n")
    except Exception as e:
        print(f"\n  ❌ Error en RAG: {str(e)}\n")


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     🧠 NEURAL VAULT BRAIN v2.0                             ║
║            Motor de Consulta Neuronal Binario para Obsidian                ║
║                                                                            ║
║  Características: Caché Larga Duración | RAG (IA Local) | Inhibición       ║
║  Propagación Bidireccional | Math TF-IDF | Grosor Sináptico                ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)


def main():
    config = load_config()
    brain = NeuralVaultBrain(config)

    print_banner()
    print(f"  📂 Vault: {brain.vault_path}")
    print(f"  ⏳ Despertando red neuronal (verificando caché)...")
    total, parsed, cached = brain.load_vault()
    print(f"  ✅ {total} neuronas listas. ({cached} de caché, {parsed} parseadas frescas)\n")

    args = sys.argv[1:]
    if args:
        if args[0] == "--ask":
            query_text = " ".join(args[1:])
            ask_local_ai(brain, query_text)
            return

        output_format = "text"
        query_text = None

        if "--md" in args:
            output_format = "markdown"
            args.remove("--md")
        elif "--json" in args:
            output_format = "json"
            args.remove("--json")

        query_text = " ".join(args)
        if query_text:
            result = brain.query(query_text)
            if output_format == "json":
                print(json.dumps(result, ensure_ascii=False, indent=2))
            elif output_format == "markdown":
                print(brain.generate_report(result))
            else:
                print(brain.generate_report(result))
            return

    # Modo Interactivo
    print("  Escribe tu consulta y presiona Enter.")
    print("  Comandos especiales: 'salir', 'stats', 'config', 'help'")
    print("  Tip: Usa '-palabra' para inhibir. Escribe '--ask pregunta' para usar IA local.\n")

    while True:
        try:
            query = input("  🧠 Consulta > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  👋 ¡Hasta pronto!")
            break

        if not query:
            continue
        if query.lower() in ("salir", "exit", "quit", "q"):
            print("  👋 ¡Hasta pronto!")
            break
        if query.startswith("--ask "):
            ask_local_ai(brain, query[6:])
            continue
        if query.lower() == "stats":
            print(f"\n  📊 Neuronas cargadas: {brain.total_notes}")
            print(f"  🔗 Max enlaces entrantes: {brain.max_inbound}")
            print(f"  ⚙️  Umbral θ: {brain.threshold}")
            print(f"  ⚡ Bonus sináptico (Forward): {brain.synapse_bonus}")
            print(f"  ⚡ Bonus sináptico (Backward): {brain.backward_synapse_bonus}")
            print(f"  🔄 Profundidad max: {brain.max_depth}\n")
            continue
        if query.lower() == "config":
            print(f"\n  {json.dumps(config, ensure_ascii=False, indent=2)}\n")
            continue
        if query.lower() == "help":
            print("\n  Comandos disponibles:")
            print("    <consulta>      — Buscar en el vault con activación neuronal")
            print("    --ask <preg>    — Buscar + RAG (Hablar con tu Vault vía IA Local)")
            print("    stats           — Mostrar estadísticas del cerebro")
            print("    config          — Mostrar configuración actual")
            print("    salir           — Salir del programa\n")
            continue

        result = brain.query(query)
        print(brain.generate_report(result))


if __name__ == "__main__":
    main()
