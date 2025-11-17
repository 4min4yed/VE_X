# Copilot Instructions for VE_X

## Project Overview
- This is a static website project with multiple HTML and CSS files, each representing a different page (e.g., `dashboard.html`, `login.html`, `contact.html`, etc.).
- All files are located in the root of the `VE_X` directory. There is also a `styles/` directory, but its usage is not clear from the current structure.
- There is no build system, backend, or JavaScript logic present in the codebase as of this analysis.

## Key Conventions
- Each HTML file is paired with a similarly named CSS file (e.g., `dashboard.html` with `dashboard.css`).
- Shared styles may be placed in `styles.css` or `common in everypage` (the latter may be a placeholder or a file for shared content).
- The main entry point is likely `Index.html` (note the capital 'I').
- All navigation and linking between pages should use relative paths and match the file names exactly (case-sensitive on some servers).

## Editing Guidelines
- When updating or creating a new page, always create a corresponding CSS file if custom styles are needed.
- Reuse shared styles from `styles.css` where possible to maintain consistency.
- If adding new shared components or styles, document their usage at the top of the relevant file.
- Keep file naming consistent (lowercase for new files, unless matching existing patterns).

## Examples
- To add a new page called `about`, create `about.html` and `about.css` in the root directory.
- To update navigation, edit all HTML files to include links to the new page.

## Special Notes
- If you find a file named `common in everypage`, clarify its purpose before editing or removing it.
- There are no automated tests, build scripts, or package dependencies in this project.

## Directory Reference
- `VE_X/` — All HTML and CSS files for the site
- `styles/` — Unused or legacy directory (verify before use)
- `.github/copilot-instructions.md` — This file

---

For any unclear conventions or missing documentation, ask the user for clarification before making structural changes.
