<div align="center">

# Neural Vault Brain v2.0

**Neural binary query engine for Obsidian vaults with Local AI (RAG) capabilities**

<p>
  <img src="https://img.shields.io/badge/Python-3.7+-3776AB?logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/Obsidian-Integration-7C3AED?logo=obsidian&logoColor=white" alt="Obsidian" />
  <img src="https://img.shields.io/badge/Dependencies-None%20(Stdlib)-success" alt="Dependencies" />
  <img src="https://img.shields.io/badge/RAG-Local%20AI-blue" alt="Local AI RAG" />
  <img src="https://img.shields.io/badge/License-MIT-lightgrey" alt="License" />
</p>

</div>

---

## Overview

Neural Vault Brain models your personal knowledge base as a biological neural network:

| Component | Biological Analogy | Function |
| :--- | :--- | :--- |
| `.md` Note | **Neuron** | Unit of knowledge holding content, tags, and state |
| `[[WikiLink]]` | **Synapse** | Weighted edge routing context across concepts |
| Search Query | **Action Potential** | Electrical impulse triggering network traversal |
| Output | **Binary State** | Activated (`1`, relevant) or Inactive (`0`, irrelevant) |

Compatible with all major AI coding assistants: **Antigravity**, **Claude Code**, **OpenClaw**, **ChatGPT**, **Cursor**, **Copilot**, **Codex**, **Aider**, and **Windsurf**.

---

## System Architecture

```mermaid
flowchart TD
    subgraph Input_Layer [1. Input Layer]
        A[User Query Tokenization]
        A1[Inhibitory Token Filter '-term']
        A --> A1
    end

    subgraph Sensory_Layer [2. Sensory Layer]
        B[LTM Cache Loader]
        B1[Parse Tags, Titles, Content, Wikilinks]
        B --> B1
    end

    subgraph Hidden_Layer [3. Hidden Layer - 4D Scoring Matrix]
        C1[Tags: 25%]
        C2[Title: 30%]
        C3[TF-IDF: 25%]
        C4[Links: 20%]
        C5{Threshold Evaluation: score >= 0.40}
        C1 & C2 & C3 & C4 --> C5
    end

    subgraph Propagation_Layer [4. Synaptic Propagation]
        D[Bidirectional Traversal]
        D1[Synaptic Thickness Multiplier]
        D2[Max Depth: 3 Levels]
        D --> D1 --> D2
    end

    subgraph Output_Layer [5. Output Layer]
        E[Activated Neurons Report]
        E1[Local AI RAG Context Ingestion]
        E --> E1
    end

    Input_Layer --> Sensory_Layer
    Sensory_Layer --> Hidden_Layer
    C5 -- Active: 1 --> Propagation_Layer
    Propagation_Layer --> Output_Layer
