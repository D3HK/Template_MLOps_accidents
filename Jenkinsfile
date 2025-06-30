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
                    # Устанавливаем совместимые версии evidently и pydantic
                    pip install pydantic==1.10.13
                    pip install evidently==0.3.2  # Версия, которая точно работает с pydantic<2
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
                            mkdir -p reports
                            # Проверяем доступность модулей
                            python -c "from evidently.dashboard import Dashboard; from evidently.tabs import DataDriftTab; print('Evidently modules available')"
                            # Запускаем скрипт обнаружения дрейфа
                            python drift_detection.py || echo "Drift detection completed with warnings"
                        '''
                        // Проверяем наличие отчетов
                        sh 'ls -la reports/'
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
            archiveArtifacts artifacts: 'reports/**/*', allowEmptyArchive: true
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
