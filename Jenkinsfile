pipeline {
    agent any

    stages {
        // 1. Ambil kode terbaru dari GitHub
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        // 2. Cek syntax app.py pakai kontainer Python sementara
        stage('Syntax Check') {
            steps {
                sh 'docker run --rm -i python:3.12-slim python -c "import ast,sys; ast.parse(sys.stdin.read())" < backend/app.py'
            }
        }

        // 3. Build image backend
        stage('Build Image') {
            steps {
                sh 'docker compose build'
            }
        }

        // 4. Jalankan ulang kontainer dengan kode terbaru
        stage('Automated Deployment') {
            steps {
                sh 'docker compose up -d'
            }
        }

        // 5. Cek API dari dalam kontainer frontend
        stage('Health Check') {
            steps {
                sh 'sleep 5 && docker exec task-frontend wget -qO- http://backend:5000/tasks'
            }
        }
    }
}