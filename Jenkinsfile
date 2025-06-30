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
                    pip install evidently  # Добавляем установку evidently
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
                            python drift_detection.py || exit 0  # Продолжаем даже при ошибке
                        '''
                        // Проверяем существование файлов перед архивированием
                        sh 'test -f reports/drift_report.html && test -f reports/drift_metrics.json'
                        archiveArtifacts artifacts: 'reports/drift_report.html, reports/drift_metrics.json'
                    } catch (Exception e) {
                        echo "Warning: Drift detection failed - ${e.getMessage()}"
                        // Не прерываем весь пайплайн, только предупреждение
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/**/*.html, reports/**/*.json', allowEmptyArchive: true
        }
        failure {
            echo "Pipeline failed - check the logs for details"
        }
        unstable {
            echo "Pipeline completed with warnings"
        }
    }
}
