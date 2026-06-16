# SHR Command Dashboard

## Product Definition

- Product name: `SHR Command Dashboard`
- Product type: local-first property accountability dashboard
- Product register: product
- Derived from: `shr-extractor` parsing workflow and export pipeline
- Primary artifact: a self-contained HTML dashboard commanders can open, update, save, and use as a living document

## Purpose

`SHR Command Dashboard` turns GCSS-Army Sub Hand Receipt extraction into a commander-facing operations surface. The product should help command teams answer three questions quickly:

1. What property do we have?
2. Who is each accountable item signed down to?
3. Where is that item physically located right now?

The dashboard is not just a report viewer. It is a daily working record that combines extracted SHR data with commander-entered accountability context, discrepancy notes, and local annotations.

## Primary Users

- Commanders who need fast visibility into accountability risk
- Property book officers and supply sergeants supporting command inventories
- Hand receipt holders and sub-hand-receipt managers maintaining current location and signature context

## Core User Workflow

1. Upload an SHR PDF into the local generator app.
2. Extract serial-level property records from the PDF.
3. Generate a self-contained dashboard HTML file for daily use.
4. Open the dashboard locally without needing a server.
5. Review exception-focused summaries first:
   - missing assignee
   - missing location
   - unresolved discrepancy
   - newly imported items
   - items missing from the latest SHR
6. Update annotations directly in the dashboard:
   - assignee
   - sub-holder
   - location
   - labels
   - notes
   - discrepancy status
   - review date
7. Save an updated local copy of the dashboard for continued use.
8. Re-import a later SHR and preserve existing annotations by merge.

## Product Principles

- Manage by exception: surface risk, gaps, and unresolved issues before raw inventory browsing.
- Local first: the workflow must remain fully useful on a local machine without cloud services.
- Daily usability: the saved dashboard is meant to stay open, be edited often, and support recurring command review.
- Serial-level truth: each accountable item should be trackable at the serial number level whenever source data allows it.
- Low-friction updates: commanders and supply staff should be able to keep the record current without complex setup.

## Scope For V1

- Parse SHR PDFs using the existing extractor foundation.
- Normalize extracted data into serial-level records.
- Generate an offline-capable HTML dashboard with embedded data.
- Allow local editing of accountability metadata and discrepancy tracking.
- Preserve annotations across re-imports using serial-number-first merge behavior.
- Export updated HTML, JSON backups, and CSV outputs useful for reporting.

## Explicitly Out Of Scope For V1

- Multi-user synchronization
- Remote hosting or cloud accounts
- Authentication or role management
- Real-time collaboration
- GIS or floorplan mapping
- Automatic assignee/location extraction from other Army systems
- Encryption or key management

## Data And Privacy Posture

- Treat all extracted and annotated property data as sensitive operational data.
- The exported dashboard must make no network calls.
- The generator app should operate locally and should not require cloud APIs.
- Saved HTML files will contain embedded inventory and annotation data.
- The UI must clearly warn users that exported files contain property accountability information and should be stored accordingly.

## Accessibility Target

- Minimum target: WCAG AA for contrast, focus visibility, keyboard navigation, and status communication.
- Status cannot rely on color alone.
- Dense operational layouts are acceptable, but keyboard access and text clarity are mandatory.

## Success Criteria

- A commander can open the generated HTML locally and understand accountability gaps within minutes.
- A supply team member can annotate items without needing the Flask app to remain open.
- Re-importing a new SHR preserves existing notes and accountability context for matching items.
- The dashboard remains useful as a living document over time, not just a one-time export.

## Naming And Language

Use command-oriented product language throughout the app and docs.

- Prefer: `command dashboard`, `accountability`, `assignee`, `signed down to`, `location`, `discrepancy`, `review`
- Avoid leading with: `extractor`, `conversion tool`, `parser output`

The extractor remains an implementation detail. The user-facing product is the dashboard.
