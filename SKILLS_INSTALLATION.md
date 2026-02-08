# Anthropic Skills Installation Guide

## Quick Installation (3 Steps)

### Step 1: Add Marketplace
```bash
/plugin marketplace add anthropics/skills
```

### Step 2: Install Plugin Bundles
```bash
# Install document processing skills (4 skills)
/plugin install document-skills@anthropic-agent-skills

# Install example skills (12 skills)
/plugin install example-skills@anthropic-agent-skills
```

### Step 3: Restart Claude Code
Close and reopen Claude Code to load the new skills.

---

## What Gets Installed (16 Skills Total)

### Document Skills Bundle (4 skills)
1. **xlsx** - Excel spreadsheet creation, editing, and data extraction
2. **docx** - Word document processing with tracked changes and formatting
3. **pptx** - PowerPoint presentation creation and editing
4. **pdf** - Comprehensive PDF manipulation (extract, merge, split, create, fill forms)

### Example Skills Bundle (12 skills)

**Creative & Design (4):**
5. **algorithmic-art** - Generate algorithmic art patterns
6. **canvas-design** - Design canvas-based visual elements
7. **frontend-design** - Create frontend component designs and layouts
8. **theme-factory** - Generate color themes and design systems

**Development & Technical (4):**
9. **mcp-builder** - Build MCP (Model Context Protocol) servers
10. **skill-creator** - Create new custom skills
11. **webapp-testing** - Create test plans for web applications
12. **web-artifacts-builder** - Build web artifacts and components

**Enterprise & Communication (4):**
13. **brand-guidelines** - Apply and maintain brand consistency
14. **doc-coauthoring** - Collaborative document creation
15. **internal-comms** - Draft internal communications and announcements
16. **slack-gif-creator** - Create GIFs for Slack

---

## Verification

### Option 1: Use Verification Script
```bash
python verify_skills_installation.py
```

This will check:
- ✅ Claude plugins directory exists
- ✅ Marketplace is registered
- ✅ Plugins are installed
- ✅ All 16 skills are present

### Option 2: Manual Verification
In Claude Code, run:
```bash
/plugin list
```

You should see:
- document-skills@anthropic-agent-skills
- example-skills@anthropic-agent-skills

---

## Testing

After installation, see **test_skills.md** for comprehensive testing guide with:
- Individual test cases for each skill
- Quick verification commands
- Batch testing scripts
- Expected outcomes
- Troubleshooting guide

### Quick Test
Try these commands in Claude Code after installation:

```
Create a simple Excel file with 3 columns: Name, Age, City
```

```
Create a Word document with a title and two paragraphs
```

```
Create a PowerPoint with 2 slides: title slide and content slide
```

```
Create a PDF with "Hello World" text
```

---

## Files Created

- **SKILLS_INSTALLATION.md** (this file) - Installation instructions
- **test_skills.md** - Comprehensive testing guide for all 16 skills
- **verify_skills_installation.py** - Python script to verify installation
- **skills/** - Local clone of anthropics/skills repository

---

## Troubleshooting

### Skills don't appear after installation
1. Restart Claude Code completely
2. Check installation: `/plugin list`
3. Verify marketplace: `/plugin marketplace list`

### Marketplace not found
```bash
# Re-add the marketplace
/plugin marketplace add anthropics/skills

# Verify it was added
/plugin marketplace list
```

### Plugin installation fails
```bash
# Try reinstalling
/plugin uninstall document-skills@anthropic-agent-skills
/plugin install document-skills@anthropic-agent-skills
```

### Skills don't trigger automatically
- Explicitly mention the skill name in your request
- Example: "Use the PDF skill to extract text from document.pdf"
- Check the skill's description to understand when it triggers

---

## Next Steps

1. ✅ Run installation commands above
2. ✅ Restart Claude Code
3. ✅ Run verification: `python verify_skills_installation.py`
4. ✅ Test skills using test_skills.md
5. ✅ Start using skills in your workflow!

---

## Resources

- **Official Skills Repo**: https://github.com/anthropics/skills
- **What are skills?**: https://support.claude.com/en/articles/12512176
- **Using skills**: https://support.claude.com/en/articles/12512180
- **Creating custom skills**: https://support.claude.com/en/articles/12512198

---

## Current Status

- [x] Downloaded skills repository
- [ ] Added anthropic-agent-skills marketplace
- [ ] Installed document-skills plugin
- [ ] Installed example-skills plugin
- [ ] Restarted Claude Code
- [ ] Verified installation
- [ ] Tested skills

---

**Ready to install? Run the 3 commands in the Quick Installation section above!**
