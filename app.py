import streamlit as st
import requests

# Define CSS styles
STYLE = """
h1 {
    text-align: center;
    color: #353d4b;
}

h2 {
    color: #353d4b;
    margin-top: 3rem;
}

p {
    color: #505966;
    font-size: 1.2rem;
    line-height: 1.5rem;
}

a {
    color: #008ae6;
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

.search-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 3rem;
    margin-bottom: 3rem;
}

.search-box {
    width: 60%;
    padding: 1rem;
    font-size: 1.2rem;
    border: 1px solid #d8dde6;
    border-radius: 5px;
}

.search-btn {
    background-color: #008ae6;
    color: #fff;
    padding: 1rem 2rem;
    border: none;
    border-radius: 5px;
    margin-left: 1rem;
    cursor: pointer;
}

.results-container {
    margin-top: 3rem;
    margin-bottom: 3rem;
}

.result-item {
    padding: 1rem;
    border: 1px solid #d8dde6;
    border-radius: 5px;
    margin-bottom: 1rem;
    transition: background-color 0.2s;
}

.result-item:hover {
    background-color: #f2f2f2;
}

.result-title {
    font-size: 1.4rem;
    color: #353d4b;
    margin-bottom: 0.5rem;
}

.result-link {
    font-size: 1.2rem;
    color: #008ae6;
    margin-bottom: 0.5rem;
}
"""

# Set the page style
st.set_page_config(page_title="Salesforce Search Engine", page_icon=":mag:", layout="wide")

# Set the style using the STYLE variable
st.write(f'<style>{STYLE}</style>', unsafe_allow_html=True)




# Set the page title
st.title("Salesforce Search Engine")

# Create a search box
search_query = st.text_input("Enter your search query:")

num_docs = st.number_input("Number of documents to retrieve:", min_value=1, max_value=50, step=1, value=10)

# Create a search button
search_button = st.button("Search")



if search_button:
    # Perform the search and retrieve the results
    base_url = "https://salesforce.stackexchange.com/questions/"
    results = requests.get("http://127.0.0.1:8000/query", params={"q": search_query, "k": num_docs})
    results = results.json()
    # Display the results
    if results:
        st.header(f"Search results for '{search_query}':")
        for result in results:
            print(result)
            link = base_url + result["question_id"]
            st.markdown(
                f"""
                <div class="result-item">
                    <h3 class="result-title">{result['title']}</h3>
                    <a class="result-link" href="{link}" target="_blank">{link}</a>
                    <p>{result['description']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.warning(f"No results found for '{search_query}'")
