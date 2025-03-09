from setuptools import setup, find_packages

setup(
    name="paper-helper",
    version="0.1.0",
    packages=find_packages(include=['utils', 'utils.*', 'services', 'services.*', 'scripts', 'scripts.*']),
    install_requires=[
        "PyPDF2>=3.0.0",
        "python-magic>=0.4.27",
        "pyyaml>=6.0.1",
        "langchain>=0.1.0",
        "transformers>=4.36.0",
        "fastapi>=0.109.0",
        "uvicorn>=0.27.0"
    ]
) 