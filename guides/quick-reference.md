# 🗺️ Fiche récap — Interagir avec Hermes

> Dernière mise à jour : 2026-05-29 (v2 — ajout Slide Generator web app)
> Ce fichier évolue au fil des améliorations. Reviens vérifier les nouvelles sections.

---

## 1. 📱 Telegram (interaction quotidienne)

**Canal principal.** Tu parles à Hermes directement ici.

| Ce que tu fais | Comment |
|---|---|
| Parler à Hermes | Écris un message dans cette conversation |
| Demander du code, un audit, une recherche | Décris ce que tu veux — Hermes le construit et le push sur GitHub |
| Envoyer une note vocale | Hermes la transcrit automatiquement et la traite (si un skill est activé) |
| Recevoir des fichiers/images | Hermes envoie les fichiers directement dans la conversation (MEDIA:) |

**Rappel :** tout ce qu'Hermes produit (code, specs, rapports) est pushé sur GitHub → `baptlagae-hue/hermes`.

---

## 2. 💻 Terminal (SSH — pour les actions avancées)

Quand tu veux faire toi-même des actions sur le VPS, ou ouvrir une session pour explorer.

### Connexion

```bash
ssh hermes
```
*La clé est déjà configurée, pas de mot de passe.*

### Ce que tu peux faire depuis le terminal

| Commande | Action |
|---|---|
| `hermes` | Lancer Hermes en mode terminal (CLI) |
| `hermes-dash` | Ouvrir le Dashboard Web UI dans le navigateur (port 9119) |
| `hermes-xp` | Ouvrir l'Expertise Transfer Engine (port 8011) |
| `cd ~/hermes-workspace` | Aller dans le dossier de travail partagé |

### Services en écoute

| Service | Port local (via SSH tunnel) | Accès |
|---|---|---|
| Hermes Dashboard | `http://127.0.0.1:9119` | Web UI |
| Expertise Transfer Engine (API) | `http://127.0.0.1:8010` | Backend |
| Expertise Transfer Engine (frontend) | `http://127.0.0.1:8011` | `hermes-xp` |

### Alias Mac disponibles (dans ~/.zshrc)

- `hermes` → `ssh hermes`
- `hermes-dash` → ouvre `http://127.0.0.1:9119` dans le navigateur
- `hermes-xp` → ouvre `http://127.0.0.1:8011` dans le navigateur

---

## 3. 🗂️ Projets — Mapping des dossiers

Tout le code et les travaux sont structurés dans le repo GitHub unique :  
**`github.com/baptlagae-hue/hermes`**

### Arborescence

```
hermes-workspace/
├── projects/          ← Code source complet de chaque projet
│   ├── expertise-transfer-engine/
│   └── slide-generator/      ← App web exposée : http://2.24.11.116:8012
├── specs/             ← Spécifications techniques générées
├── prompts/           ← Prompts prêts à l'emploi
├── reports/           ← Audits, recherches, recommandations
└── guides/            ← Documentation d'architecture (dont ce fichier)
```

### Accès local sur le Mac

```bash
# Cloner le repo une première fois (chez toi sur le Mac)
git clone git@github.com:baptlagae-hue/hermes.git ~/hermes-workspace

# Puis pour récupérer le travail d'Hermes
cd ~/hermes-workspace && git pull
```

### Pour Claude Code (sur le Mac)

Claude Code a accès à ce même repo. Tu peux lui demander :
> *« Va chercher le travail qu'Hermes a fait sur [sujet] dans le repo hermes-workspace »*

Il ira directement fouiller dans `~/hermes-workspace/projects/`, `specs/`, etc.

---

## 5. 🌐 Apps exposées (accessibles depuis n'importe où)

Ces apps sont accessibles via le navigateur, sans SSH tunnel :

| App | URL | Description |
|-----|-----|-------------|
| Slide Generator | `http://2.24.11.116:8012` | Générateur de .pptx depuis template + plan + contenu |

**Sécurité :** le Dashboard Hermes (9119), l'Expertise Engine (8010/8011) ne sont pas exposés — uniquement accessibles via tunnel SSH.

---

## 4. 🔒 Règle MCP (sécurité)

**Claude Code n'utilise les outils MCP `hermes_*` que si tu dis explicitement :**  
> *« Utilise le MCP Hermès »*

Tant que tu ne dis pas cette phrase, Claude Code n'appelle rien sur le VPS.  
Cette règle est déjà dans son `CLAUDE.md` / `.mcp.json` — pas besoin d'y penser.

---

## 📌 Pour ajouter une commande ou un process

Quand Hermes ajoute une nouvelle fonctionnalité, il mettra à jour **ce fichier** (`guides/quick-reference.md`) automatiquement.  
Tu n'as qu'à faire `git pull` sur le Mac pour voir les changements.
