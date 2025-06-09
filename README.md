# e1-aws: Excel to MySQL Data Ingestion and REST API

## Project Overview

This project consists of two main components:

1.  An automated workflow to transform Excel files from a local directory, upload them to AWS S3, process them using an AWS Lambda function, and store the data in a MySQL database hosted on Amazon RDS.
2.  A local REST API built with FastAPI to interact with the MySQL database.

## Architecture

The solution leverages a serverless architecture on AWS, primarily utilizing:

- **AWS S3:** For secure storage of raw Excel files.
- **AWS Lambda:** For event-driven processing of new Excel files.
- **Amazon RDS (MySQL):** For the relational database.

## Local Development Setup

### Prerequisites

- Python 3.12 (pinned for this project)
- `uv` (project/package manager)
- `ruff` (linter/formatter)
- Docker (for local MySQL database during development)
- AWS CLI configured with your AWS credentials.

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/GMartin-Data/e1-aws.git
    cd e1-aws
    ```

2.  **Set up virtual environment and install dependencies using `uv`**
    (if needed, install `uv` with [**its online documentation**](https://docs.astral.sh/uv/#__tabbed_1_1)):

    ```bash
    uv venv
    source .venv/bin/activate # On Linux
    # Dependencies will be added progressively using `uv add`
    ```

3.  **Environment Variables:**
    Create a `.env` file in the project root based on `.env.example` and fill in your actual credentials and settings.
    ```bash
    cp .env.example .env
    # Then open .env and modify
    ```

### Running the Project (Local)

_(Instructions will be added here as we build out the components)_

## Version Control

This project follows conventional commit messages and uses feature branches for development. The `main` branch is protected.

## Contact

Your Name - your.email@example.com

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.
