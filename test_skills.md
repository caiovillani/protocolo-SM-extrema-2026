# Skills Testing Guide

This document provides test cases for all 16 Anthropic skills.

## Installation Verification

After running the installation commands, verify skills are loaded by checking:
- `/skills` command should list all installed skills
- Skills should appear in the skills menu

---

## Document Skills (4 skills)

### 1. xlsx - Excel Spreadsheet Processing
**Test Cases:**
- [ ] Create a new Excel file with sample data
- [ ] Read and extract data from an existing .xlsx file
- [ ] Modify cells in an existing spreadsheet
- [ ] Add formulas and formatting

**Test Command:**
```
Create a simple Excel spreadsheet with a table of 5 products (name, price, quantity) and calculate total value using formulas
```

### 2. docx - Word Document Processing
**Test Cases:**
- [ ] Create a new Word document with formatted text
- [ ] Extract text from an existing .docx file
- [ ] Add tracked changes to a document
- [ ] Insert comments and formatting

**Test Command:**
```
Create a Word document with a title "Test Report", two paragraphs of content, and a bulleted list
```

### 3. pptx - PowerPoint Presentation Processing
**Test Cases:**
- [ ] Create a new PowerPoint with multiple slides
- [ ] Extract text and images from existing presentation
- [ ] Modify slide content
- [ ] Add formatting and layouts

**Test Command:**
```
Create a 3-slide PowerPoint presentation: title slide, content slide with bullets, and thank you slide
```

### 4. pdf - PDF Manipulation
**Test Cases:**
- [ ] Extract text from a PDF
- [ ] Extract tables from a PDF
- [ ] Merge multiple PDFs
- [ ] Split a PDF into separate pages
- [ ] Create a new PDF from scratch
- [ ] Fill PDF forms

**Test Command:**
```
Create a simple PDF with "Hello World" text and extract the text back to verify
```

---

## Creative & Design Skills (4 skills)

### 5. algorithmic-art
**Test Cases:**
- [ ] Generate algorithmic art patterns
- [ ] Create generative art using code
- [ ] Produce visual designs with mathematical algorithms

**Test Command:**
```
Create an algorithmic art piece using geometric patterns
```

### 6. canvas-design
**Test Cases:**
- [ ] Design canvas-based visual elements
- [ ] Create interactive canvas graphics
- [ ] Generate design mockups

**Test Command:**
```
Design a simple canvas with a gradient background and centered text
```

### 7. frontend-design
**Test Cases:**
- [ ] Create frontend component designs
- [ ] Generate responsive layouts
- [ ] Build UI mockups with HTML/CSS

**Test Command:**
```
Design a simple landing page layout with header, hero section, and footer
```

### 8. theme-factory
**Test Cases:**
- [ ] Generate color themes
- [ ] Create consistent design systems
- [ ] Build theme configurations

**Test Command:**
```
Create a professional dark theme with primary, secondary, and accent colors
```

---

## Development & Technical Skills (4 skills)

### 9. mcp-builder
**Test Cases:**
- [ ] Scaffold a new MCP server in TypeScript
- [ ] Create MCP server in Python
- [ ] Implement tools with proper schemas
- [ ] Generate evaluations for MCP servers

**Test Command:**
```
Create a simple MCP server outline that would provide weather information
```

### 10. skill-creator
**Test Cases:**
- [ ] Generate a new skill structure
- [ ] Create SKILL.md with proper frontmatter
- [ ] Organize scripts, references, and assets
- [ ] Package a skill into .skill file

**Test Command:**
```
Help me create a new skill for database query optimization with proper structure
```

### 11. webapp-testing
**Test Cases:**
- [ ] Create test plans for web applications
- [ ] Generate test cases for UI components
- [ ] Design testing strategies

**Test Command:**
```
Create a test plan for a simple login form with email and password fields
```

### 12. web-artifacts-builder
**Test Cases:**
- [ ] Build web artifacts
- [ ] Generate HTML/CSS/JS components
- [ ] Create standalone web elements

**Test Command:**
```
Build a simple interactive button component with hover effects
```

---

## Enterprise & Communication Skills (4 skills)

### 13. brand-guidelines
**Test Cases:**
- [ ] Apply brand guidelines to content
- [ ] Ensure brand consistency
- [ ] Format according to brand standards

**Test Command:**
```
Describe how to apply brand guidelines to a company newsletter
```

### 14. doc-coauthoring
**Test Cases:**
- [ ] Collaborate on document creation
- [ ] Track changes and suggestions
- [ ] Manage document revisions

**Test Command:**
```
Help me structure a collaborative document for a project proposal with sections for multiple authors
```

### 15. internal-comms
**Test Cases:**
- [ ] Draft internal communications
- [ ] Create announcements and memos
- [ ] Format company messages

**Test Command:**
```
Draft an internal communication announcing a new office policy about remote work
```

### 16. slack-gif-creator
**Test Cases:**
- [ ] Create GIFs for Slack
- [ ] Generate animated reactions
- [ ] Build custom Slack emoji/GIFs

**Test Command:**
```
Describe how to create a simple celebration GIF for Slack
```

---

## Batch Testing Script

To test multiple skills at once, use these prompts:

### Quick Verification (All Skills)
```
List all available skills and confirm the following are installed:
- Document skills: xlsx, docx, pptx, pdf
- Creative skills: algorithmic-art, canvas-design, frontend-design, theme-factory
- Development skills: mcp-builder, skill-creator, webapp-testing, web-artifacts-builder
- Enterprise skills: brand-guidelines, doc-coauthoring, internal-comms, slack-gif-creator
```

### Document Skills Test
```
1. Create a simple Excel file with test data
2. Create a Word document with formatted content
3. Create a PowerPoint with 2 slides
4. Create a PDF with sample text
```

### Creative Skills Test
```
Design a cohesive visual system:
1. Use theme-factory to create a color palette
2. Use frontend-design to create a landing page layout
3. Use canvas-design to create a logo mockup
```

### Development Skills Test
```
1. Use skill-creator to outline a new custom skill
2. Use mcp-builder to describe an MCP server structure
3. Use webapp-testing to create a test plan for a simple app
```

### Communication Skills Test
```
1. Use internal-comms to draft a company announcement
2. Use doc-coauthoring to structure a collaborative report
3. Use brand-guidelines to describe brand application
```

---

## Expected Outcomes

After successful installation and testing:

- ✅ All 16 skills should be listed when running `/skills`
- ✅ Skills should trigger automatically when relevant tasks are mentioned
- ✅ Each skill should provide specialized knowledge and workflows
- ✅ Skills should be able to create files, process documents, and provide guidance

---

## Troubleshooting

If skills don't appear:
1. Verify marketplace was added: `/plugin marketplace list`
2. Check installed plugins: `/plugin list`
3. Restart Claude Code completely
4. Try reinstalling: `/plugin uninstall <name>` then `/plugin install <name>`

If a skill doesn't trigger:
1. Explicitly mention the skill name in your request
2. Check the skill's description to understand when it triggers
3. Verify the skill is installed: `/plugin list`

---

## Notes

- Skills are loaded dynamically based on task relevance
- Not all skills will trigger for every request
- Some skills work together (e.g., theme-factory + frontend-design)
- Document skills (xlsx, docx, pptx, pdf) are production-quality tools
- Example skills demonstrate various skill patterns and capabilities
