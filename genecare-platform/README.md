# GeneCare Health Data Protection Platform

GeneCare is a health data protection platform that utilizes AES-256 encryption to ensure the security and privacy of sensitive health information. This application is built using Flask, a lightweight web framework for Python.

## Features

- User authentication with secure password hashing
- AES-256 encryption for health data protection
- RESTful API for accessing health data
- User-friendly web interface for login and registration
- Modular architecture for easy maintenance and scalability

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd genecare-platform
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

   **Note:** Ensure `pycryptodome` is installed as it is required for AES encryption.

   If you encounter issues, you may need to reinstall the dependencies:
   ```
   pip install --force-reinstall -r requirements.txt
   ```

4. Set up environment variables:
   Copy `.env.example` to `.env` and update the configuration as needed.

## Usage

To run the application, execute the following command:
```
python run.py
```

The application will be accessible at `http://127.0.0.1:5000`.

## Testing

To run the tests, use the following command:
```
pytest
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.