# CampusShield AI

## Overview
CampusShield AI is a Smart Campus Safety & Emergency Response System designed to enhance safety and security on campus through advanced technologies such as AI, IoT, and real-time communication. The system integrates various components to provide a comprehensive solution for incident detection, emergency response, and data management.

## Project Structure
The project is organized into several modules, each serving a specific purpose:

- **src**: Contains the source code for the application.
  - **backend**: Implements the server-side logic using FastAPI.
  - **frontend**: Comprises web and mobile applications built with React and React Native.
  - **ai**: Contains AI modules for vision and natural language processing.
  - **data**: Manages data ingestion, storage, and schemas.
  - **edge**: Interfaces with edge devices for real-time monitoring.
  - **common**: Contains shared types and interfaces.

- **infra**: Holds infrastructure as code configurations for deployment.
- **models**: Stores model checkpoints for AI models.
- **notebooks**: Includes Jupyter notebooks for data exploration.
- **scripts**: Contains scripts for deployment and environment setup.
- **tests**: Includes unit and integration tests for the application.
- **configs**: Contains configuration files for the application.
- **docs**: Provides architectural documentation.

## Installation
To set up the project, follow these steps:

1. Clone the repository:
   ```
   git clone <repository-url>
   cd CampusShield-AI
   ```

2. Set up the environment:
   ```
   ./scripts/setup-env.sh
   ```

3. Install dependencies:
   - For the backend:
     ```
     cd src/backend
     pip install -r requirements.txt
     ```
   - For the frontend:
     ```
     cd src/frontend/web
     npm install
     ```

## Usage
To run the application, execute the following commands:

- Start the backend server:
  ```
  cd src/backend
  uvicorn server:app --reload
  ```

- Start the frontend application:
  ```
  cd src/frontend/web
  npm start
  ```

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.

## Acknowledgments
Thanks to all contributors and the open-source community for their support and resources.