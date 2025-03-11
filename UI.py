
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# Ensure set_page_config is the first Streamlit command
st.set_page_config(page_title="PostgreSQL Data Viewer", layout="wide")

@st.cache_data
def load_data():
    db_url = "postgresql://postgres:test%40123@127.0.0.1:5432/postgres"
    engine = create_engine(db_url)
    query = """
    SELECT p.id, p.name, p.project_name, p.project_type, p.project_year, 
           p.project_roles, p.profile_url, c.name as contact_name, 
           c.project_roles as contact_role, c.connection as connections, p.created_at 
    FROM profiles p 
    LEFT JOIN contacts c ON p.project_name = c.project_name ORDER BY p.created_at DESC limit 1000;
    """
    df = pd.read_sql(query, engine)
    return df

@st.cache_data
def load_data_names_project():
    db_url = "postgresql://postgres:test%40123@127.0.0.1:5432/postgres"
    engine = create_engine(db_url)
    query = """
    SELECT name,project_name
    FROM profiles
    """
    df = pd.read_sql(query, engine)
    return df

@st.cache_data
def selected_name(selected_name):
    db_url = "postgresql://postgres:test%40123@127.0.0.1:5432/postgres"
    engine = create_engine(db_url)
    query = f"""
    SELECT p.id, p.name, p.project_name, p.project_type, p.project_year, 
           p.project_roles, p.profile_url, c.name as contact_name, 
           c.project_roles as contact_role, c.connection as connections, p.created_at 
    FROM profiles p 
    LEFT JOIN contacts c ON p.project_name = c.project_name where p.name='{selected_name}';
    """
    df = pd.read_sql(query, engine)
    return df

@st.cache_data
def selected_project(selected_project):
    db_url = "postgresql://postgres:test%40123@127.0.0.1:5432/postgres"
    engine = create_engine(db_url)
    query = f"""
    SELECT p.id, p.name, p.project_name, p.project_type, p.project_year, 
           p.project_roles, p.profile_url, c.name as contact_name, 
           c.project_roles as contact_role, c.connection as connections, p.created_at 
    FROM profiles p 
    LEFT JOIN contacts c ON p.project_name = c.project_name where p.project_name='{selected_project}';
    """
    df = pd.read_sql(query, engine)
    return df

@st.cache_data
def load_notifications():
    db_url = "postgresql://postgres:test%40123@127.0.0.1:5432/postgres"
    engine = create_engine(db_url)
    query = "SELECT * FROM notification order by date desc"
    df = pd.read_sql(query, engine)
    return df

@st.cache_data
def load_contacts_notifications():
    db_url = "postgresql://postgres:test%40123@127.0.0.1:5432/postgres"
    engine = create_engine(db_url)
    query = "SELECT * FROM contacts_notifications order by date desc"
    df = pd.read_sql(query, engine)
    return df

def refresh_data():
    st.cache_data.clear()
    st.rerun()

def authenticate_user(username, password):
    db_url = "postgresql://postgres:test%40123@127.0.0.1:5432/postgres"
    engine = create_engine(db_url)
    query = text("SELECT * FROM login WHERE username = :username AND password = :password")
    with engine.connect() as conn:
        result = conn.execute(query, {"username": username, "password": password}).fetchone()
        return result is not None

def login_page():
    """Login Page UI"""
    st.markdown("<h1 style='text-align: center; color: #4CAF50;'>🔐 Welcome to IMDB Data Viewer</h1>", unsafe_allow_html=True)
    
    with st.container():
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            with st.form("login_form", clear_on_submit=True):
                username = st.text_input("Username", placeholder="Enter your username", key="username")
                password = st.text_input("Password", type="password", placeholder="Enter your password", key="password")
                submitted = st.form_submit_button("Login")
        
        if submitted:
            if authenticate_user(username, password):
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("❌ Invalid username or password")


def main_app():
    """Main Data Viewer UI"""
    st.cache_data.clear()
    st.markdown("""
    <style>
    div[role="radiogroup"] {
        display: flex;
        justify-content: start;
        gap: 10px;
    }
    div[role="radiogroup"] label {
        background-color: #f0f0f5;
        border: 2px solid #d1d1d1;
        padding: 12px 24px;
        margin: 5px;
        border-radius: 12px;
        cursor: pointer;
        font-weight: bold;
        text-align: center;
        transition: all 0.3s ease-in-out;
    }
    div[role="radiogroup"] label:hover {
        background-color: #e6e6e6;
        border-color: #bbbbbb;
    }
    div[role="radiogroup"] label[data-selected="true"] {
        background-color: #007BFF !important;
        color: white !important;
        border-color: #007BFF !important;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
    }
    </style>
""", unsafe_allow_html=True)
    page = st.radio("Navigation", (["📊 IMDB Profile Data", "🔔 Notifications","👤 Contacts Notifications"]), horizontal=True,label_visibility="hidden")
    
    
    with st.sidebar:
        if page == "📊 IMDB Profile Data":
            st.header("🔍 IMDB Data Filters")
            df = load_data()
            df_names=load_data_names_project()
            name_filter = st.selectbox("Search by Name", options=["All"] + list(df_names['name'].dropna().unique()))
            project_filter = st.selectbox("Search by Project Name", options=["All"] + list(df_names['project_name'].dropna().unique()))
            sort_column = st.selectbox("Sort by", df.columns)
            sort_order = st.radio("Order", ("Ascending", "Descending"))
        elif page == "🔔 Notifications":
            st.header("🔍 Notification Filters")
            df = load_notifications()
            title_filter = st.selectbox("Filter by Title", ["All"] + list(df['title'].dropna().unique()))
            type_filter = st.selectbox("Filter by Type", ["All"] + list(df['type'].dropna().unique())) if 'type' in df.columns else None

        elif page == "👤 Contacts Notifications":
            st.header("🔍 Contacts Notification Filters")
            df = load_contacts_notifications()
            title_filter = st.selectbox("Filter by Title", ["All"] + list(df['title'].dropna().unique()))
            type_filter = st.selectbox("Filter by Type", ["All"] + list(df['type'].dropna().unique())) if 'type' in df.columns else None
    
    if page == "📊 IMDB Profile Data":
        if df.empty:
            st.stop()
        
        
        
        filtered_df = df.copy()
        if name_filter != "All":
            # filtered_df = filtered_df[filtered_df['name'].str.contains(name_filter, case=False, na=False, regex=True)]
            filtered_df = selected_name(name_filter)
            st.title(f"📊 Connections to {name_filter}")
        else:
            st.title(f"📊 IMDB Profile Data")
        if project_filter != "All":
            # filtered_df = filtered_df[filtered_df['project_name'].str.contains(project_filter, case=False, na=False, regex=True)]
            filtered_df = selected_project(project_filter)
        
        
        ascending = True if sort_order == "Ascending" else False
        filtered_df = filtered_df.sort_values(by=sort_column, ascending=ascending)
        filtered_df["project_year"] = filtered_df["project_year"].astype(str)
        st.data_editor(
            filtered_df[["project_year","contact_name","contact_role","project_name","project_roles"]],
            # column_config={"profile_url": st.column_config.LinkColumn("Profile Link", display_text="🔗"),},
            
            hide_index=True,
            use_container_width=True,
            height=600,
        )
    
    elif page == "🔔 Notifications":
        if df.empty:
            st.stop()
        
        st.title("🔔 Notifications")
        
        filtered_df = df.copy()
        if title_filter != "All":
            filtered_df = filtered_df[filtered_df['title'].str.contains(title_filter, case=False, na=False, regex=True)]
        if type_filter and type_filter != "All":
            filtered_df = filtered_df[filtered_df['type'].str.contains(type_filter, case=False, na=False, regex=True)]
        
        st.dataframe(filtered_df[['latest', 'date']], use_container_width=True, height=600)

    elif page == "👤 Contacts Notifications":
        if df.empty:
            st.stop()

        st.title("👤 Contacts Notifications")

        # Copy and filter the DataFrame
        filtered_df = df.copy()

        if title_filter != "All":
            filtered_df = filtered_df[filtered_df['title'].str.contains(title_filter, case=False, na=False, regex=True)]
        if type_filter and type_filter != "All":
            filtered_df = filtered_df[filtered_df['type'].str.contains(type_filter, case=False, na=False, regex=True)]

        # Convert 'name' column into clickable hyperlinks
        filtered_df["name"] = filtered_df.apply(
            lambda row: f'<a href="{row["profile_url"]}" target="_blank">{row["name"]}</a>', axis=1
        )

        filtered_df["latest"] = filtered_df.apply(
            lambda row: f'<a href="{row["project_urls"]}" target="_blank">{row["latest"]}</a>', axis=1
        )
        # Apply custom CSS for height and width
        st.markdown(
            """
            <style>
            .stDataFrame { height: 600px !important; }
            table { width: 100%; border-collapse: collapse; }
            th { background-color: #f4f4f4; text-align: center !important; padding: 10px; }
            td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
            </style>
            """,
            unsafe_allow_html=True
        )

        # Display combined table with hyperlinks using markdown
        st.markdown(filtered_df[["name", "title", "latest", "date"]].to_html(escape=False, index=True), unsafe_allow_html=True)



        if st.sidebar.button("🔄 Refresh Data"):
            refresh_data()
        if st.sidebar.button("🔒 Logout"):
            st.session_state["authenticated"] = False
            st.rerun()

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    login_page()
else:
    main_app()



#streamlit run UI.py --server.port=8501
