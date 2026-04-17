#!/usr/bin/env python3
"""
Script pour mettre à jour les projets du README.md depuis projects.json
À placer dans : .github/scripts/update_projects.py
"""

import json
import re
import os
from pathlib import Path

# Chemin vers projects.json
PORTFOLIO_PATH = os.getenv('PORTFOLIO_PATH', '../portfolio-repo')
PROJECTS_FILE = Path(PORTFOLIO_PATH) / 'src' / 'data' / 'projects.json'
README_FILE = Path('README.md')

def load_projects():
    """Charge les projets depuis projects.json"""
    try:
        with open(PROJECTS_FILE, 'r', encoding='utf-8') as f:
            projects = json.load(f)
        return projects
    except FileNotFoundError:
        print(f"❌ Fichier non trouvé: {PROJECTS_FILE}")
        return []

def get_latest_projects(projects, n=3):
    """Retourne les n projets les plus récents, triés par date décroissante."""
    dated = [p for p in projects if p.get('date')]
    dated.sort(key=lambda p: p['date'], reverse=True)
    return dated[:n]

def generate_projects_section(projects):
    """
    Génère la section HTML des projets (3 cartes sur une ligne).
    """
    if not projects:
        return "<!-- Aucun projet trouvé -->"

    latest = get_latest_projects(projects, n=3)

    cells = []
    for project in latest:
        title = project.get('content', {}).get('en', {}).get('title', 'Untitled Project')
        repo_url = project.get('links', {}).get('github', '#')
        live_url = project.get('links', {}).get('live', '')

        # Image : chemin relatif → URL raw GitHub
        cover_src = project.get('cover', {}).get('src', '')
        if cover_src.startswith('/'):
            cover_url = f"https://raw.githubusercontent.com/aurvl/portfolio/main{cover_src}"
        else:
            cover_url = cover_src

        # Tags / outils (3 max)
        tools = project.get('taxonomy', {}).get('tools', [])
        tools_str = ', '.join(tools[:3]) if tools else 'Project'

        demo_part = f'\n      | <a href="{live_url}">🚀 Demo</a>' if live_url else ''

        img_link = live_url if live_url else repo_url
        cells.append(
            f'    <td align="center" width="33%">\n'
            f'      <a href="{img_link}">\n'
            f'        <img src="{cover_url}" alt="{title}" width="260"/>\n'
            f'      </a>\n'
            f'      <br/>\n'
            f'      <b>{title}</b><br/>\n'
            f'      <a href="{repo_url}">📘 Repo</a>{demo_part}\n'
            f'      <br/>\n'
            f'      <sub>{tools_str}</sub>\n'
            f'    </td>'
        )

    rows = '\n'.join(cells)
    html = f"## **Recent Projects**\n\n<table>\n  <tr>\n{rows}\n  </tr>\n</table>\n"
    return html

def update_readme(projects_section):
    """
    Met à jour le README avec la nouvelle section projets
    """
    try:
        with open(README_FILE, 'r', encoding='utf-8') as f:
            readme_content = f.read()
    except FileNotFoundError:
        print(f"❌ Fichier non trouvé: {README_FILE}")
        return False
    
    # Chercher les marqueurs
    start_marker = "<!-- PROJECTS_START -->"
    end_marker = "<!-- PROJECTS_END -->"
    
    if start_marker in readme_content and end_marker in readme_content:
        # Remplacer entre les marqueurs
        pattern = f"{re.escape(start_marker)}.*?{re.escape(end_marker)}"
        new_section = f"{start_marker}\n{projects_section}{end_marker}"
        updated_content = re.sub(pattern, new_section, readme_content, flags=re.DOTALL)
    else:
        # Ajouter avant "Get in Touch" ou à la fin
        if "## Get in Touch" in readme_content:
            pattern = r"(## Get in Touch)"
            new_section = f"{start_marker}\n{projects_section}{end_marker}\n\n\\1"
            updated_content = re.sub(pattern, new_section, readme_content)
        else:
            updated_content = readme_content + f"\n\n{start_marker}\n{projects_section}{end_marker}\n"
    
    # Écrire le nouveau README
    try:
        with open(README_FILE, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print("✅ README.md mis à jour avec succès!")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'écriture: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Chargement des projets...")
    projects = load_projects()
    
    if projects:
        print(f"✅ {len(projects)} projets chargés")
        projects_section = generate_projects_section(projects)
        
        print("📝 Mise à jour du README...")
        if update_readme(projects_section):
            print("✅ Succès!")
        else:
            print("❌ Erreur lors de la mise à jour")
    else:
        print("❌ Aucun projet trouvé")
