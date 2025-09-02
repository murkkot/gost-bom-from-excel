pipeline {
    agent none
    stages {
        stage("test") {
            agent {
                docker {
                    image 'python:3.9-slim'
                }
            }
            steps {
                echo 'testing...'
                sh "pip install -r requirements.txt"
                sh "pip install pytest"
                sh "pytest -v"
            }
        }
        stage("build") {
            agent {
                docker {
                    image 'cdrx/pyinstaller-windows:python3'
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