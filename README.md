## 🔧 Gas Utility Consumer Service API

# Key Features
RESTful APIs: Built API-first to support access from any device — web or mobile — via standard HTTP requests.

Databse : Postgressql 

Efficient Query Fetching:

Implemented pagination to reduce response payloads.

Used select_related and prefetch_related to optimize database query performance.

# Containerization with Docker:

Dockerized the entire application to simplify development, deployment, and environment consistency.

Ensures the project is ready for container orchestration tools like Kubernetes in the future.

Unit Testing:

Added unit tests in the accounts module to ensure code reliability and correctness.

 
## 🐳 Docker Setup
To run the application in a Docker container:
docker-compose up --build

Future Scalability
With Docker already in place, the system is ready to be deployed on Kubernetes (K8s) for horizontal scaling and microservices orchestration.

The API-centric architecture ensures seamless integration with modern frontends or third-party services.

Run testing with : 
python manage.py test
Unit tests are currently implemented in the accounts app, ensuring robust user-related logic.
![image](https://github.com/user-attachments/assets/3afad9aa-f481-4d98-be02-bec33013ab5d)

