pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Train') {
            steps {
                sh '''
                    . venv/bin/activate
                    python src/models/train_model.py
                    ls -la models/  # Проверка содержимого
                '''
            }
        }

        stage('Archive Model') {
            steps {
                archiveArtifacts artifacts: 'src/models/*.joblib', fingerprint: true
            }
        }
    }
}
