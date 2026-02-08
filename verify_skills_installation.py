#!/usr/bin/env python3
"""
Skills Installation Verification Script

Checks if all Anthropic skills are properly installed in Claude Code.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Set

# Expected skills organized by category
EXPECTED_SKILLS = {
    'document-skills': {
        'xlsx': 'Excel spreadsheet processing',
        'docx': 'Word document processing',
        'pptx': 'PowerPoint presentation processing',
        'pdf': 'PDF manipulation'
    },
    'example-skills': {
        'algorithmic-art': 'Algorithmic art generation',
        'brand-guidelines': 'Brand guidelines application',
        'canvas-design': 'Canvas design creation',
        'doc-coauthoring': 'Document collaboration',
        'frontend-design': 'Frontend design',
        'internal-comms': 'Internal communications',
        'mcp-builder': 'MCP server development',
        'skill-creator': 'Create new skills',
        'slack-gif-creator': 'Slack GIF creation',
        'theme-factory': 'Theme generation',
        'web-artifacts-builder': 'Web artifacts building',
        'webapp-testing': 'Web application testing'
    }
}


def get_claude_plugins_dir() -> Path:
    """Get the Claude plugins directory path."""
    home = Path.home()
    plugins_dir = home / '.claude' / 'plugins'
    return plugins_dir


def read_installed_plugins() -> Dict:
    """Read the installed_plugins.json file."""
    plugins_dir = get_claude_plugins_dir()
    installed_file = plugins_dir / 'installed_plugins.json'

    if not installed_file.exists():
        print(f"❌ Plugins file not found: {installed_file}")
        return {}

    try:
        with open(installed_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error reading plugins file: {e}")
        return {}


def read_marketplaces() -> Dict:
    """Read the known_marketplaces.json file."""
    plugins_dir = get_claude_plugins_dir()
    marketplaces_file = plugins_dir / 'known_marketplaces.json'

    if not marketplaces_file.exists():
        print(f"❌ Marketplaces file not found: {marketplaces_file}")
        return {}

    try:
        with open(marketplaces_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error reading marketplaces file: {e}")
        return {}


def check_marketplace_exists(name: str = 'anthropic-agent-skills') -> bool:
    """Check if the skills marketplace is registered."""
    marketplaces = read_marketplaces()
    return name in marketplaces


def check_plugin_installed(plugin_name: str, marketplace: str = 'anthropic-agent-skills') -> bool:
    """Check if a specific plugin is installed."""
    installed = read_installed_plugins()
    plugin_key = f"{plugin_name}@{marketplace}"
    return plugin_key in installed.get('plugins', {})


def find_skill_directories() -> Set[str]:
    """
    Find all skill directories in the local skills repository.
    Returns a set of skill names found.
    """
    skills_dir = Path('skills') / 'skills'
    if not skills_dir.exists():
        return set()

    skill_names = set()
    for item in skills_dir.iterdir():
        if item.is_dir() and (item / 'SKILL.md').exists():
            skill_names.add(item.name)

    return skill_names


def verify_installation():
    """Main verification function."""
    print("=" * 70)
    print("ANTHROPIC SKILLS INSTALLATION VERIFICATION")
    print("=" * 70)
    print()

    # Check Claude Code plugins directory
    plugins_dir = get_claude_plugins_dir()
    if not plugins_dir.exists():
        print(f"❌ Claude plugins directory not found: {plugins_dir}")
        print("   Is Claude Code installed?")
        return False

    print(f"✅ Claude plugins directory found: {plugins_dir}")
    print()

    # Check for anthropic-agent-skills marketplace
    print("📦 Checking Marketplaces...")
    print("-" * 70)

    marketplaces = read_marketplaces()
    if 'anthropic-agent-skills' in marketplaces:
        print("✅ anthropic-agent-skills marketplace is registered")
    else:
        print("❌ anthropic-agent-skills marketplace NOT found")
        print("   Run: /plugin marketplace add anthropics/skills")
        print()
        print("Available marketplaces:")
        for name in marketplaces.keys():
            print(f"   - {name}")
        return False

    print()

    # Check for installed plugins
    print("🔌 Checking Installed Plugins...")
    print("-" * 70)

    all_installed = True

    # Check document-skills
    if check_plugin_installed('document-skills'):
        print("✅ document-skills plugin installed")
    else:
        print("❌ document-skills plugin NOT installed")
        print("   Run: /plugin install document-skills@anthropic-agent-skills")
        all_installed = False

    # Check example-skills
    if check_plugin_installed('example-skills'):
        print("✅ example-skills plugin installed")
    else:
        print("❌ example-skills plugin NOT installed")
        print("   Run: /plugin install example-skills@anthropic-agent-skills")
        all_installed = False

    print()

    # Check individual skills in local repository
    print("📁 Checking Local Skills Repository...")
    print("-" * 70)

    local_skills = find_skill_directories()
    if local_skills:
        print(f"✅ Found {len(local_skills)} skills in local repository")

        expected_count = sum(len(skills) for skills in EXPECTED_SKILLS.values())
        if len(local_skills) == expected_count:
            print(f"✅ All {expected_count} expected skills found")
        else:
            print(f"⚠️  Expected {expected_count} skills, found {len(local_skills)}")
    else:
        print("❌ No skills found in local repository")
        print("   Is the skills/ directory present?")

    print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    total_skills = sum(len(skills) for skills in EXPECTED_SKILLS.values())

    for category, skills in EXPECTED_SKILLS.items():
        print(f"\n{category.upper()} ({len(skills)} skills):")
        for skill_name, description in skills.items():
            if skill_name in local_skills:
                status = "✅"
            else:
                status = "❌"
            print(f"  {status} {skill_name:20s} - {description}")

    print()
    print("=" * 70)

    if all_installed and len(local_skills) == total_skills:
        print("✅ ALL SKILLS INSTALLED SUCCESSFULLY")
        print("\nNext steps:")
        print("1. Restart Claude Code to load the skills")
        print("2. Run tests from test_skills.md")
        print("3. Try: 'Create a simple PDF with Hello World text'")
        return True
    else:
        print("❌ INSTALLATION INCOMPLETE")
        print("\nRequired actions:")
        if 'anthropic-agent-skills' not in marketplaces:
            print("1. Add marketplace: /plugin marketplace add anthropics/skills")
        if not check_plugin_installed('document-skills'):
            print("2. Install document-skills: /plugin install document-skills@anthropic-agent-skills")
        if not check_plugin_installed('example-skills'):
            print("3. Install example-skills: /plugin install example-skills@anthropic-agent-skills")
        print("4. Restart Claude Code")
        return False


if __name__ == '__main__':
    try:
        success = verify_installation()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(2)
