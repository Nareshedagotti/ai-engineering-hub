import streamlit as st
from utils import (
    initialize_database,
    process_pdfs,
    generate_sql,
    retrieve_context,
    execute_query,
    synthesize_response,
    pdf_files,
    pdf_data,
    engine,
    city_stats_table,
    device,
)

# Set page config FIRST
st.set_page_config(
    page_title="RAG + Text to SQL",
    layout="wide"
)

# Initialize database
initialize_database()

# Process PDFs
vector_db = process_pdfs()

# Display GPU/CPU info in sidebar
st.sidebar.info(f"Running on: {device.upper()}")

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def main():
    st.title("RAG + Text to SQL")
    
    # Sidebar for technical details, PDF preview, and database preview
    with st.sidebar:
        st.header("Document Explorer")
        
        # PDF Selection
        selected_pdf = st.selectbox("Choose PDF Document", pdf_files)
        
        # PDF Preview
        if selected_pdf in pdf_data:
            with st.expander("PDF Preview"):
                tab1, tab2 = st.tabs(["Visual Preview", "Text Content"])
                
                with tab1:
                    if pdf_data[selected_pdf]["images"]:
                        for img in pdf_data[selected_pdf]["images"]:
                            st.image(img, use_container_width=True)
                    else:
                        st.warning("No renderable pages found")
                
                with tab2:
                    st.write(pdf_data[selected_pdf]["full_text"])
        
        # Database Preview
        with st.expander("Database Preview"):
            try:
                with engine.connect() as conn:
                    data = conn.execute(city_stats_table.select()).fetchall()
                    st.dataframe(data, use_container_width=True)
            except Exception as e:
                st.error(f"Database error: {str(e)}")
        
        # Technical Details
        st.header("Retrived Details")
        
        if "sql_query" in st.session_state:
            with st.expander("SQL Query"):
                st.code(st.session_state.sql_query, language="sql")
        
        if "sql_result" in st.session_state:
            with st.expander("Database Results"):
                if st.session_state.sql_result["error"]:
                    st.error(st.session_state.sql_result["error"])
                else:
                    st.write(st.session_state.sql_result["data"])
        
        if "context" in st.session_state:
            with st.expander("Context Used"):
                st.write(st.session_state.context)

    # Main chat interface
    st.subheader("Chat with your data")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # User input
    question = st.chat_input("Ask your question about city data...")
    
    if question:
        # Add user question to chat history
        st.session_state.chat_history.append({"role": "user", "content": question})
        
        with st.spinner("Processing your request..."):
            # Step 1: Generate SQL
            sql_query = generate_sql(question)
            
            # Step 2: Execute SQL
            sql_result = execute_query(sql_query)
            
            # Step 3: Retrieve Context
            context = retrieve_context(question)
            
            # Step 4: Generate Final Response
            final_response = synthesize_response(question, sql_result, context)
            
            # Store results in session state
            st.session_state.update({
                "sql_query": sql_query,
                "sql_result": sql_result,
                "context": context,
                "final_response": final_response
            })
            
            # Add assistant response to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": final_response})
        
        # Rerun to update the chat interface
        st.rerun()

if __name__ == "__main__":
    main()