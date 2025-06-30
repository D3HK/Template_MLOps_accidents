pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout([$class: 'GitSCM',
                branches: [[name: '*/master']],
                extensions: [],
                userRemoteConfigs: [[url: 'https://github.com/D3HK/Template_MLOps_accidents']]])
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
                '''
            }
        }

        stage('Archive') {
            steps {
                archiveArtifacts artifacts: 'src/models/*.joblib', fingerprint: true
            }
        }

        stage('Drift Detection') {
            steps {
        sh 'python drift_detection.py'
        archiveArtifacts 'reports/drift_report.html'
            }
        }
    }
}
