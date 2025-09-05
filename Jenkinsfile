pipeline {
    agent none
    stages {
        stage("test") {
            agent {
                docker {
                    image 'python:3.9-slim'
                    args '-v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            steps {
                echo 'testing...'
                sh """
                    python -m venv venv
                    source venv/bin/activate
                    pip install -r requirements.txt
                    pip install pytest
                    pytest --junit-xml=test-reports/results.xml
                """
            }
            post {
                always {
                    junit 'test-reports/results.xml'
                }
            }
        }
        stage("build") {
            agent {
                docker {
                    image 'cdrx/pyinstaller-windows:python3'
                    args '-v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            steps {
                echo 'building...'
                sh "pip install -r requirements.txt"
                sh "pyinstaller --clean --onefile main.py"
            }
        }
        stage("release") {
            agent any
            steps {
                echo 'releasing...'
            }

        }
    }
}