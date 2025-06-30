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
                    pip install evidently==0.4.11  # Указываем конкретную версию
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
                            mkdir -p reports  # Создаем директорию для отчетов
                            python -c "from evidently.report import Report; print('Evidently report module available')"
                            python drift_detection.py || echo "Drift detection script failed"
                        '''
                        // Проверяем и архивируем отчеты, если они есть
                        sh '''
                            if [ -f "reports/drift_report.html" ]; then
                                echo "Found drift report"
                            else
                                echo "No drift report found"
                            fi
                        '''
                        archiveArtifacts artifacts: 'reports/**/*', allowEmptyArchive: true
                    } catch (Exception e) {
                        echo "Warning: Drift detection encountered an issue - ${e.getMessage()}"
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }
    }

    post {
        always {
            // Всегда архивируем отчеты, даже если их нет
            archiveArtifacts artifacts: 'reports/**/*', allowEmptyArchive: true
            // Очищаем виртуальное окружение
            sh 'rm -rf venv'
        }
        unstable {
            echo "Pipeline completed with warnings - check drift detection"
        }
        failure {
            echo "Pipeline failed - check the logs"
        }
    }
}
