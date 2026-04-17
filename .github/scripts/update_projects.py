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

def generate_projects_section(projects):
    """
    Génère la section HTML des 3 projets les plus récents
    """
    if not projects:
        return "<!-- Aucun projet trouvé -->"
    
    # Trier par date décroissante et prendre les 3 plus récents
    sorted_projects = sorted(
        projects,
        key=lambda p: p.get('date', ''),
        reverse=True
    )[:3]
    
    html = "## **Recent Projects**\n\n<table>\n  <tr>\n"
    
    for idx, project in enumerate(sorted_projects):
        # Nouvelle ligne tous les 3 projets
        if idx > 0 and idx % 3 == 0:
            html += "  </tr>\n  <tr>\n"
        
        # Récupérer les infos du projet
        title = project.get('content', {}).get('en', {}).get('title', 'Untitled Project')
        repo_url = project.get('links', {}).get('github', '#')
        live_url = project.get('links', {}).get('live', repo_url)
        demo_url = project.get('links', {}).get('primary', repo_url)
        
        # Image
        cover_src = project.get('cover', {}).get('src', '')
        if cover_src.startswith('/'):
            # Utilisation de la branche 'master' et du dossier 'public' correct
            cover_url = f"https://raw.githubusercontent.com/aurvl/portfolio/master/public{cover_src}"
        else:
            cover_url = cover_src
        
        # Tags / Tools
        tools = project.get('taxonomy', {}).get('tools', [])
        tools_str = ', '.join(tools[:3]) if tools else 'Project'
        
        # Lien principal (demo si dispo, sinon repo)
        link_url = demo_url if demo_url else repo_url
        
        # Liens (repo + démo si disponible) — sur une seule ligne sans saut de ligne vide
        links_line = f'<a href="{repo_url}" target="_blank">📘 Repo</a>'
        if live_url and live_url != repo_url:
            links_line += f' | <a href="{live_url}" target="_blank">🚀 Demo</a>'

        # Générer la carte du projet
        html += f"""    <td align="center" width="33%">
      <a href="{link_url}" target="_blank">
        <img src="{cover_url}" alt="{title}" style="width:100%; height:150px; object-fit:cover; border-radius:8px;"/>
      </a>
      <br/>
      <b>{title}</b><br/>
      {links_line}
      <br/>
      <sub>{tools_str}</sub>
    </td>
"""
    
    html += "  </tr>\n</table>\n"
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
