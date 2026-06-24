# 📊 Narrative-BI Smart Agent

An AI-powered Business Intelligence (BI) assistant that directly connects to your database, analyzes data, generates charts, and explains the root causes of events in plain, easy-to-understand language.

> 🚧 **Project Status: Work in Progress (WIP)**
> This project is in its early stages of development. New features and improvements will be added continuously.

## ✨ Features
- 🧠 **Text-to-SQL:** Converts natural language questions into executable database queries.
- 📈 **Visualization:** Automatically generates interactive Plotly charts based on the data.
- 📝 **Narrative:** Analyzes raw data and provides written insights and root-cause analysis.
- 🔒 **Secure Execution:** Safe execution environment without exposing the entire database to the LLM.

## 🚀 Quick Start

1. **Clone the repository:**
```bash
git clone [https://github.com/YOUR-USERNAME/narrative-bi.git](https://github.com/YOUR-USERNAME/narrative-bi.git)
cd narrative-bi
```

2. **Install the dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up your API key:**
Rename the `.env.example` file to `.env` and add your OpenAI API key:
```text
OPENAI_API_KEY=your_actual_api_key_here
```

4. **Run the application:**
```bash
streamlit run app/app.py
```

## 🤝 Contributing

This is an open-source project, and contributions are highly welcome! There is plenty of room for improving prompts, adding support for local LLMs (like Ollama), and enhancing the UI.

To contribute:
1. **Fork** the project.
2. Add or modify the code.
3. **Commit** your changes. 
4. Open a **Pull Request** so we can review and merge your code into the main branch.

---
*Built with ❤️ and powered by Streamlit & OpenAI*