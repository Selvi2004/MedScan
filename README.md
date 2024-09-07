# MedScan: Patient Data Retrieval Assistant

MedScan is a streamlined AI-powered application that helps users query and retrieve patient data through a conversational interface. It integrates with databases to generate and execute SQL queries, returning relevant information to the user in a chat-based format. This project leverages powerful AI models, including Google's Gemini API and OpenAI’s GPT-3.5, to enhance query generation and data summarization.

## Features

- **Conversational Interface**: Ask natural language questions, and MedScan will generate SQL queries based on your input.
- **Data Query Execution**: The app automatically runs SQL queries on your database and displays results in a user-friendly format.
- **Summarization**: Provides a concise summary of large datasets when requested.
- **Customizable Prompts**: The conversation chain utilizes an entity-based memory system to maintain context.
- **Responsive Design**: Built with Streamlit, offering an intuitive and visually appealing UI.
- **Session Management**: Each chat session is stored and can be revisited for reference.

## Technologies Used

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Backend**: Python, Snowflake, SQL query execution via custom `json_execution.py`
- **AI Models**: 
  - Google Gemini API (for query generation and conversational AI)
  - OpenAI GPT-3.5-turbo
  - Langchain for conversation memory and prompt generation
- **Database Support**: Snowflake (can be extended to support multiple databases)

