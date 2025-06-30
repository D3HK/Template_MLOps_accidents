pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/master']],
                    extensions: [],
                    userRemoteConfigs: [[url: 'https://github.com/D3HK/Template_MLOps_accidents.git']]
                ])
            }
        }

        stage('Setup') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
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

        stage('Archive Model') {
            steps {
                archiveArtifacts artifacts: 'src/models/*.joblib', fingerprint: true
            }
        }

        stage('Drift Detection') {
            steps {
                script {
                    try {
                        sh '''
                            . venv/bin/activate
                            python drift_detection.py
                        '''
                        archiveArtifacts artifacts: 'reports/drift_report.html, reports/drift_metrics.json'
                    } catch (Exception e) {
                        error("Data drift detected or drift detection failed: ${e.getMessage()}")
                    }
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/**/*'
        }
    }
}
