import streamlit as st
import pandas as pd
import ontology
import os
import importlib
import streamlit.components.v1 as components

importlib.reload(ontology)

# Page Config
st.set_page_config(page_title="ISAAC Portal", layout="wide")

st.title("ISAAC AI-Ready Record Portal")
st.markdown("### The Middleware for Scientific Semantics")

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Ontology Editor", "Record Validator", "About"])

# --- CONFIG: Display Names ---
DISPLAY_MAP = {
    "Record Info": "1. Record Info",
    "Sample": "2. Subject (Sample)",
    "Context": "3. Conditions (Context)",
    "System": "4. Setup (System)",
    "Measurement": "5. Measurement",
    "Assets": "6. Assets (Files)",
    "Links": "7. Links (Lineage)",
    "Descriptors": "8. Results (Descriptors)"
}

def get_display_name(key):
    return DISPLAY_MAP.get(key, key)

# --- CONFIG: Wiki Mapping ---
WIKI_BASE = "https://github.com/dimosthenisSLAC/isaac-ai-ready-record/wiki"

WIKI_MAP = {
    "Record Info": "Record-Overview",
    "Sample": "Sample",
    "Context": "Context",
    "System": "System",
    "Measurement": "Measurement",
    "Assets": "Assets",
    "Links": "Links",
    "Descriptors": "Descriptors"
}

# --- HELPER: Mermaid HTML Generator ---
def render_mermaid(code, height=600):
    """
    Renders Mermaid diagram using custom HTML to support Click Events.
    We need 'securityLevel': 'loose' for clicks to work.
    """
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
        <script>
            mermaid.initialize({{
                startOnLoad: true,
                securityLevel: 'loose',
                theme: 'default'
            }});
        </script>
        <style>
            /* Ensure it fits */
            body {{ margin: 0; }}
            .mermaid {{ width: 100%; }}
        </style>
    </head>
    <body>
        <div class="mermaid">
        {code}
        </div>
    </body>
    </html>
    """
    components.html(html_code, height=height, scrolling=True)

def generate_mermaid_code(active_section=None, active_category=None):
    """
    Generates Mermaid JS syntax for the ontology tree.
    Includes click events to open Wiki pages in new tab.
    """
    sections = ontology.get_sections()
    
    # Theme settings
    color_root = "#f9f9f9"
    color_section = "#e1f5fe" 
    color_subblock = "#fff8e1"
    color_field = "#fff3e0"
    color_active = "#ffcccb" 
    stroke_active = "#ff0000"
    
    mm = ["graph LR", "Record(ISAAC Record)"]
    click_events = [] 
    styles = []
    
    # Link Root to Home
    click_events.append(f'click Record "{WIKI_BASE}" "Go to Wiki Home" _blank')

    for sec in sections:
        disp_sec = get_display_name(sec)
        sec_id = sec.replace(" ", "_").replace(".", "_")
        
        # Node Label
        mm.append(f'Record --> {sec_id}("{disp_sec}")')
        
        # Click for Section
        wiki_page = WIKI_MAP.get(sec, "")
        if wiki_page:
            url = f"{WIKI_BASE}/{wiki_page}"
            click_events.append(f'click {sec_id} "{url}" "Open {wiki_page}" _blank')
        
        is_active_sec = (sec == active_section)
        
        if is_active_sec:
            styles.append(f"style {sec_id} fill:{color_active},stroke:{stroke_active},stroke-width:2px")
        else:
            styles.append(f"style {sec_id} fill:{color_section}")
             
        # Drill down if active section
        if is_active_sec:
            cats = ontology.get_categories(sec)
            subblocks = {}
            
            for cat_key in cats:
                parts = cat_key.split('.')
                if len(parts) > 1:
                    field_name = parts[-1]
                    path = ".".join(parts[:-1]) 
                else:
                    field_name = cat_key
                    path = "root"
                
                if path not in subblocks:
                    subblocks[path] = []
                subblocks[path].append((field_name, cat_key))

            # Render Subblocks
            for path, fields in subblocks.items():
                if path == "root":
                    parent_node = sec_id
                else:
                    path_parts = path.split('.')
                    sub_name = path_parts[-1]
                    sub_id = path.replace(".", "_").replace(" ", "_")
                    
                    mm.append(f"{sec_id} --> {sub_id}({sub_name})")
                    styles.append(f"style {sub_id} fill:{color_subblock}")
                    parent_node = sub_id
                    
                    if wiki_page:
                        anchor = sub_name.lower().replace("_", "-")
                        sub_url = f"{WIKI_BASE}/{wiki_page}#{anchor}"
                        click_events.append(f'click {sub_id} "{sub_url}" "Open Section" _blank')
                
                # Render Fields
                for field_name, full_key in fields:
                    field_id = full_key.replace(".", "_").replace(" ", "_")
                    mm.append(f"{parent_node} --> {field_id}[{field_name}]")
                    
                    if wiki_page:
                         anchor = field_name.lower().replace("_", "-")
                         field_url = f"{WIKI_BASE}/{wiki_page}#{anchor}"
                         click_events.append(f'click {field_id} "{field_url}" "Def: {field_name}" _blank')

                    if full_key == active_category:
                        styles.append(f"style {field_id} fill:{color_active},stroke:{stroke_active},stroke-width:2px")
                        
                        # Show Values
                        vals = cats[full_key]['values'][:5]
                        for val in vals:
                             val_clean = val.replace(" ", "_").replace("/", "_").replace(".", "_")
                             mm.append(f"{field_id} -.-> {val_clean}({val})")
                    else:
                        styles.append(f"style {field_id} fill:{color_field}")

    mm.extend(styles)
    mm.extend(click_events)
    return "\n".join(mm)

# --- TAB 1: Ontology Editor ---
if page == "Ontology Editor":
    st.header("📚 Living Ontology")
    st.info("Navigate via the dropdowns on the left. The Visual Map updates to show context.")

    sections = ontology.get_sections()

    col_nav, col_map = st.columns([1, 1.5])

    # -- LEFT: Controls --
    with col_nav:
        st.subheader("1. Navigation")
        # Use Display Names in Selectbox
        selected_section = st.selectbox("Select Schema Section", sections, format_func=get_display_name)
        
        categories_dict = ontology.get_categories(selected_section)
        categories = list(categories_dict.keys())
        
        if categories:
            selected_category = st.radio("Select Category", categories)
        else:
            selected_category = None
            st.warning("No categories found.")
            
        # Add Category
        with st.expander("➕ Add New Category"):
            new_cat = st.text_input("New Key (e.g. context.transport.viscosity)")
            new_desc = st.text_input("Description")
            if st.button("Create Category"):
                success, msg = ontology.add_category(selected_section, new_cat, new_desc)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
                    
        st.divider()
        
        if selected_category:
            st.subheader(f"2. Edit: {selected_category}")
            if selected_category in categories_dict:
                 st.write(f"*{categories_dict[selected_category]['description']}*")
                 values = categories_dict[selected_category]['values']
                 df_vals = pd.DataFrame(values, columns=["Allowed Terms"])
                 st.dataframe(df_vals, use_container_width=True, height=200)
            
            # Add Term
            col_in, col_btn = st.columns([3, 1])
            with col_in:
                new_term = st.text_input("New Term", label_visibility="collapsed", placeholder="new_term")
            with col_btn:
                if st.button("Add"):
                    if new_term:
                        success, msg = ontology.add_term(selected_section, selected_category, new_term)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.warning(msg)

    # -- RIGHT: Pedagogic Map --
    with col_map:
        st.subheader("🧠 Concept Map")
        st.caption("Visualizing: " + get_display_name(selected_section))
        
        mermaid_code = generate_mermaid_code(selected_section, selected_category)
        render_mermaid(mermaid_code, height=600)


# --- TAB 2: Record Validator ---
elif page == "Record Validator":
    st.header("✅ Excel Validator")
    st.info("Upload an ISAAC Metadata Excel file to check for compliance.")
    
    uploaded_file = st.file_uploader("Upload Excel", type=["xlsx"])
    
    if uploaded_file:
        try:
            # Read 'File List' tab
            df = pd.read_excel(uploaded_file, sheet_name="File List")
            st.success(f"Loaded {len(df)} rows from 'File List'.")
            
            vocab = ontology.load_vocabulary()
            
            # EXACT Mapping
            mapping = {
                "Environment": ("Context", "context.environment"),
                "Cell Type": ("Context", "context.electrochemistry.cell_type"),
                "Flow Mode": ("Context", "context.transport.flow_mode"),
                "Sample Form": ("Sample", "sample.sample_form"), 
                "Potential Scale": ("Context", "context.electrochemistry.potential_scale"),
                "Reaction": ("Context", "context.electrochemistry.reaction"),
                "Record Type": ("Record Info", "record_type")
            }
            
            def get_allowed_values(sec, cat):
                if sec in vocab and cat in vocab[sec]:
                    return set(vocab[sec][cat]['values'])
                return set()

            all_valid = True
            
            for col, (sec, cat) in mapping.items():
                if col in df.columns:
                    st.subheader(f"Checking `{col}`...")
                    # Note: We must map the Display Name (if used in future Excel) back to Schema Key
                    # But current Excel uses "Environment", etc. 
                    # The mapping keys are safe.
                    allowed = get_allowed_values(sec, cat)
                    
                    if not allowed:
                         st.warning(f"⚠️ Schema definition for {col} ({cat}) not found.")
                         continue
                         
                    user_values = df[col].dropna().unique()
                    invalid = [v for v in user_values if v not in allowed]
                    
                    if not invalid:
                        st.write(f"✅ All {len(user_values)} values are valid.")
                    else:
                        all_valid = False
                        st.error(f"❌ Found {len(invalid)} invalid values!")
                        st.write("Invalid terms:", invalid)
                        st.write("Allowed terms:", allowed)
                else:
                     pass 

            if all_valid:
                st.balloons()
                st.success("🎉 This file is fully compliant with the ISAAC v1.0 Ontology!")
                
        except Exception as e:
            st.error(f"Error reading file: {e}")

# --- TAB 3: About ---
elif page == "About":
    st.markdown("""
    **ISAAC Portal v0.7 (Intuitive)**
    
    *   **Dual-Naming**: Shows "Setup (System)" to help users, but keeps "System" for the schema.
    *   **Structure**: Strictly aligned with Wiki.
    """)
