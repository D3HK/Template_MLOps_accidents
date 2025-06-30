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
                script {
                    try {
                        sh '''
                        . venv/bin/activate  # Активируем виртуальное окружение
                        python src/monitoring/drift_detection.py
                        '''
                        // Если скрипт выполнился успешно - сохраняем отчет
                        archiveArtifacts artifacts: 'reports/drift_report.html, reports/drift_metrics.json'
                    } catch(e) {
                        // При обнаружении дрейфа отправляем уведомление
                        emailext body: "Data drift detected!\n${e}", 
                                 subject: "DRIFT ALERT: ${env.JOB_NAME}", 
                                 to: 'your-email@example.com'
                        error "Data drift detected"  // Падаем на этом этапе
                    }
                }
            }
        }
    }

    post {
        always {
            // Всегда сохраняем артефакты, даже при ошибке
            archiveArtifacts artifacts: 'reports/**/*'
        }
    }
}
