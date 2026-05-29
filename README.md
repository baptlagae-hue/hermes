# Hermes Workspace

Bienvenue dans le workspace partagé entre **Hermes Agent (VPS)** et **Claude Code (Mac)**.

## Architecture

```
Claude Code (Mac) ◄── MCP (SSH) ──► Hermes Agent (VPS)
                                        │
                                        ▼ git push
                                   GitHub (ce repo)
                                        │
Claude Code (Mac) ◄── git pull ─────────┘
```

- **Sens 1 (MCP)** : Claude Code peut appeler Hermes via MCP (SSH) pour des actions sur le VPS
- **Sens 2 (Git)** : Hermes push son travail ici, Claude Code pull pour y accéder

## Structure du repo

```
hermes-workspace/
├── projects/       # Code source des applications complètes
│   └── expertise-transfer-engine/
├── specs/          # Spécifications techniques générées
├── prompts/        # Prompts générés (voice-note-to-prompt)
├── reports/        # Audits, recherches, recommandations
└── guides/         # Guides d'architecture, how-to
```

## Utilisation du MCP Hermes

Par défaut, Claude Code **n'utilise pas les outils MCP `hermes_*`** sauf autorisation explicite avec la phrase :

> « Utilise le MCP Hermès »

Cette règle est définie pour sécuriser l'accès au VPS.
