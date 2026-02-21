from setuptools import setup, find_packages

setup(
    name="ai-bug-bountyhunter",
    version="1.0.0",
    description="Advanced AI-Powered SAST/DAST Tool with Auto-Fix Capabilities",
    author="Gemini CLI Agent",
    packages=find_packages(),
    install_requires=[
        "requests",
        "colorama",
        "beautifulsoup4",
        "tqdm",
        "flask",
        "streamlit",
        "python-dotenv"
    ],
    entry_points={
        'console_scripts': [
            'ai-bug-hunter=aibughunter.cli:main',
            'ai-bug-hunter-gui=aibughunter.gui:run_gui'
        ],
    },
    python_requires='>=3.8',
)
