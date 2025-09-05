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
                    venv/bin/pip install -r requirements.txt
                    venv/bin/pip install pytest
                    venv/bin/pytest --junit-xml=test-reports/results.xml
                """
            }
            post {
                always {
                    junit 'test-reports/results.xml'
                }
            }
        }
        stage("build") {
            agent any
            steps {
                echo 'building...'
                sh "docker run --rm -v "$PWD:/src" cdrx/pyinstaller-windows:python3 "pyinstaller --clean --onefile main.py""
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