import streamlit as st
import os
import git
import shutil
import requests
import mimetypes
import google.generativeai as genai

# Configure the Gemini API key
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY", ""))

def clone_repository(repo_url, destination):
    """
    Clone a Git repository from the given URL to the specified destination.
    
    Args:
        repo_url (str): The URL of the Git repository.
        destination (str): The directory where the repository should be cloned.
        
    Returns:
        str: The path to the cloned repository.
    """
    try:
        if os.path.exists(destination):
            shutil.rmtree(destination)  # Delete the existing directory
        repo = git.Repo.clone_from(repo_url, destination)
        return repo.working_dir
    except git.exc.GitCommandError as e:
        raise RuntimeError(f"Failed to clone repository: {e}")

def traverse_repository(repo_path):
    """
    Traverse the cloned repository, collect README content, analyze it,
    and then collect information about all files.

    Args:
        repo_path (str): The path to the cloned repository.

    Returns:
        dict: A dictionary with file paths as keys and file metadata as values.
    """
    readme_content = ""
    file_metadata = {}

    # Collect README content
    readme_file = None
    for root, _, files in os.walk(repo_path):
        for file in files:
            file_path = os.path.join(root, file)
            if file.lower() == 'readme.md' or file.lower() == 'readme.rst':
                readme_file = file_path
                with open(readme_file, 'r', encoding='utf-8') as readme:
                    readme_content += readme.read() + "\n"  # Collect content of all README files
                break  # Analyzed the README, no need to continue searching

    # Analyze README content
    if readme_content:
        st.title("GitHub Repository Overview:")
        analysis_result = analyze_with_gemini(readme_content)
        st.write(analysis_result)
        st.write("-----")

    # Continue traversing repository and collecting file metadata
    for root, _, files in os.walk(repo_path):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path.lower() != readme_file:  # Skip README file
                try:
                    # Get file metadata
                    file_stat = os.stat(file_path)
                    file_metadata[file_path] = {
                        'size': file_stat.st_size,
                        'last_modified': file_stat.st_mtime,
                        'mime_type': mimetypes.guess_type(file_path)[0]
                    }
                except Exception as e:
                    st.warning(f"Failed to get metadata for {file_path}. Reason: {e}")
    return file_metadata

def analyze_with_gemini(content):
    """
    Analyze content using Gemini AI.

    Args:
        content (str): The content to analyze.

    Returns:
        str: The analysis result.
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        content = content + " analyse everything thoroughly then summarize and explain. guide how to use this GitHub repo and show all resources listed and categorise everything. present in great detail"
        response = model.generate_content(content)
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"

def main():
    st.title("GitHub Repo Analyzer")

    # Get GitHub repository URL from user
    repo_url = st.text_input("Enter GitHub repository URL:")
    if st.button("Submit"):
        if repo_url:
            destination = "cloned_repo"  # Specify destination directory for cloning
            cloned_repo_path = clone_repository(repo_url, destination)
            if cloned_repo_path:
                st.success("Repository cloned successfully.")
                repo_files_metadata = traverse_repository(cloned_repo_path)
                if repo_files_metadata:
                    for file_path, metadata in repo_files_metadata.items():
                        st.info(f"File: {file_path}")
                        st.write(f"Size: {metadata['size']} bytes")
                        st.write(f"Last Modified: {metadata['last_modified']}")
                        st.write(f"MIME Type: {metadata['mime_type']}")
                        # Read file content
                        if metadata['mime_type'] and metadata['mime_type'].startswith('audio'):
                            file_content = "Binary file - Audio"
                        else:
                            try:
                                with open(file_path, 'r', encoding='utf-8') as file:
                                    file_content = file.read()
                            except UnicodeDecodeError:
                                file_content = "Binary file - Unable to read as text"
                        # Push content through Gemini for analysis
                        analysis_result = analyze_with_gemini(file_content)
                        st.write("Analysis Result:")
                        st.write(analysis_result)
                        st.write("-----")
                    # Add conversation logic here based on context
                else:
                    st.warning("No files found in the repository.")
            else:
                st.error("Failed to clone repository.")
        else:
            st.warning("Please enter a valid GitHub repository URL.")

if __name__ == "__main__":
    main()
