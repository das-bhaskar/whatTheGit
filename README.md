# whatTheGit
# GitHub Repo Analyzer

This is a Streamlit web application for analyzing GitHub repositories. It clones the repository from the provided URL, traverses its content, and provides various metadata about the files present in the repository.

## Usage

1. **Clone Repository:** Enter the URL of the GitHub repository you want to analyze.
2. **Submit:** Click the submit button to start the analysis process.
3. **Analysis Result:** Once the repository is cloned and analyzed, you will see a summary of its content along with metadata such as file size, last modified date, and MIME type.
4. **Gemini Analysis:** The application uses the Gemini AI to analyze the content of files, including README files. The analysis provides insights into the content and structure of the repository.

## Installation

To run this application locally, make sure you have Python installed along with the necessary dependencies. You can install the required packages using pip:

```bash
pip install streamlit gitpython google.generativeai

Try it:
https://whatthegit.streamlit.app
