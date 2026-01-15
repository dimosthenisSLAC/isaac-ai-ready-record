# ISAAC Portal Architecture (v0.1)

**Goal**: A lightweight, locally deployable Web Interface ("The Middleware") to manage the ISAAC Ontology and validate scientific records.

## 1. Technology Stack
*   **Frontend/Backend**: [Streamlit](https://streamlit.io/) (Python)
    *   *Why*: Rapid prototyping, native support for JSON/DataFrames, fits scientific python ecosystem.
*   **Data Store**: Local File System (JSON)
    *   `vocabulary.json`: The "Database" of allowed terms.
    *   `records/`: Folder where validated records are Staged.

## 2. Core Modules

### Module A: The Ontology Engine (`ontology.py`)
A python class that interface with `vocabulary.json`.
*   `load_vocabulary()`: Reads the JSON.
*   `get_options(category, subtype)`: Returns allowed values (e.g. "cell_types" for "operando").
*   `add_term(category, term, metadata)`: Adds a new term to the JSON.

### Module B: The Web Interface (`app.py`)
Streamlit app with 3 tabs:

#### Tab 1: "The Dictionary" (Ontology Viewer/Editor)
*   **Tree View**: Visualize `Context` -> `Environment` -> `Operando` -> `Cell Types`.
*   **Action**: "Request New Term" form.
    *   User inputs: `Category="Cell Type"`, `Name="New_Flow_Cell"`, `Description="..."`.
    *   Button: "Save to Vocabulary".

#### Tab 2: "Record Validator" (The Gatekeeper)
*   **Input**: Drag & Drop Excel File (using our Template).
*   **Process**:
    1.  Parses Excel rows.
    2.  Checks against `vocabulary.json`.
    3.  **Visual Feedback**: Green checkmarks for valid rows, Red flags for invalid terms (e.g. "insitu" != "in_situ").
*   **Action**: "Convert to JSON". (Calls our ingestion logic).

#### Tab 3: "Record Builder" (The Wizard - Future Scope)
*   A form-based wizard to create a record from scratch without Excel.

## 3. Data Flow
1.  **User** opens `app.py`.
2.  **App** loads `vocabulary.json`.
3.  **User** uploads `experiment_data.xlsx`.
4.  **App** validates entries against Vocabulary.
    *   *If Invalid*: App suggests "Did you mean 'in_situ'?"
5.  **App** generates `record_uuid.json` packages.

## 4. Immediate Tasks
1.  Extract hardcoded lists from `generate_excel.py` into `vocabulary.json`.
2.  Build `app.py` with Tab 1 (Ontology Editor).
