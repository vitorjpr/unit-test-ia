## JUnit Test Generator with GPT-4

This project utilizes the power of OpenAI's GPT-4 model to automatically generate JUnit test cases for Java projects. It takes a zipped Java project as input, analyzes the code, and generates comprehensive JUnit tests for each class. The generated tests are then integrated back into the project, and a new zipped project with the tests is provided for download.

### Features

* **Automated test generation:** GPT-4 generates JUnit tests for all public methods in the provided Java classes.
* **Comprehensive test coverage:**  The generated tests aim to provide comprehensive coverage of the code, including edge cases and different scenarios.
* **Code quality enhancement:** The generated tests are formatted, corrected, and optimized for clarity and readability.
* **Easy-to-use interface:** A simple web interface allows users to upload their project and download the updated project with generated tests.
* **Progress tracking:** The progress of the test generation process is displayed in real-time, giving users feedback on the status of the operation.

### Usage

1. **Prepare your project:** Create a zip archive of your Java project.
2. **Run the application:**  Start the Flask application using the `docker-compose up -d` command.
3. **Upload your project:** Access the web interface at `http://localhost:5000` and upload the zipped project file.
4. **Download the updated project:** Once the process is complete, you will be able to download the updated project containing the generated JUnit tests.

### Project Structure

```
├── Dockerfile
├── app
│   ├── __pycache__
│   │   └── (...)
│   └── app.py
├── docker-compose.yml
├── output
│   ├── (...)
├── requirements.txt
└── templates
    └── index.html
```

**Dockerfile:** Defines the Docker image for the application, including dependencies and configuration.

**docker-compose.yml:**  Configures the Docker environment, setting up the API service and specifying port mappings and environment variables.

**app/app.py:** Contains the Flask application logic, including the web interface, file handling, and the interaction with the OpenAI API for test generation.

**templates/index.html:** Defines the HTML structure of the web interface.

**requirements.txt:** Lists the Python libraries required for the project.

**output:**  Contains the zipped projects with the generated tests.

### Requirements

* Docker
* Docker Compose
* Python 3.9+
* OpenAI API Key (obtained from [https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys))

### Setup

1. **Obtain OpenAI API Key:** Create an account at [https://platform.openai.com](https://platform.openai.com) and generate an API key.
2. **Set API Key:** Create a `.env` file in the root of the project and add the following line: `OPENAI_API_KEY=<your_openai_api_key>`
3. **Build and run the application:** Run the following commands in your terminal:
   ```bash
   docker-compose build
   docker-compose up -d
   ```

### Contributions

Contributions are welcome! Please feel free to open an issue or a pull request.

### Disclaimer

This project is for demonstration purposes only. The generated tests may require further adjustments to ensure full functionality and desired test coverage. It's recommended to review and modify the generated tests as needed.
