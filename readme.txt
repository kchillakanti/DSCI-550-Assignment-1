DSCI-550-2025b-Assignment-1

Team Members and Responsibilities:
- Kirthi Chillikanti - Witness Count parser, Tika Similarity Lead
- Lance Dsilva - Date parser, Tika Similarity Lead
- Rafayel Mirijanyan - Additional Datasets Lead
- Kavi Gill - Alcohol Abuse Dataset Lead
- Hyuntae Roh - Code conductor, Daylight dataset Lead
- Ryan Norring - Keyword-Category parser, Report conductor

For instructions on environment installation and script running, see README.md

This project is a collaborative effort by the team members listed above for the DSCI 550 course. The environment setup ensures all necessary dependencies are installed for proper running of python scripts.

Libraries Used and Their Purpose:

Our Assignment 1 python scripts use various Python libraries for natural language processing (NLP), geospatial analysis, machine learning, computer vision, and web scraping. Below is a breakdown of the dependencies specified in environment.yaml (sometimes called a requirements.txt file for other projects) and their purposes:

1. Core Python & Package Management
- python=3.9 - Ensures compatibility with spaCy 3.8.0.
- pip - Used for installing additional packages.

2. Natural Language Processing (NLP)
- spacy - Advanced NLP library for tokenization, POS tagging, and named entity recognition.
- spacy-model-en_core_web_sm - Small-sized English language model for spaCy.
- regex - Provides advanced regular expression capabilities for text processing.
- number-parser (via pip) - Parses numbers from text (e.g., "twenty-five" to 25).

3. Data Manipulation & Analysis
- pandas - Essential for handling structured data such as CSVs and tables.
- geopandas - Extends pandas for geospatial data analysis.
- matplotlib - A powerful plotting library for creating static, animated, and interactive visualizations in Python.
- numpy (>=2.0.0) - Enables fast numerical computations and array operations.

4. Geospatial Analysis
- shapely - Used for computational geometry and spatial operations.
- scipy - A scientific computing library that provides tools for optimization, signal processing, statistics, and numerical integration.

5. Machine Learning
- scikit-learn - Offers tools for classification, regression, clustering, and other ML tasks.

6. Computer Vision & Optical Character Recognition (OCR)
- OpenCV - A widely used library for image processing and computer vision.
- pytesseract - A wrapper for Tesseract OCR, enabling text extraction from images.

7. Web Scraping & HTML Parsing
- requests - Enables sending HTTP requests to fetch web pages or interact with APIs.
- beautifulsoup4 - Parses HTML and XML, making web scraping easier.
- lxml - A fast XML and HTML parser for web scraping tasks.

8. Utility Libraries
- tqdm - Provides progress bars for loops and data processing.

