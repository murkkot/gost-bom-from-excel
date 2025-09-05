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
            // Use a minimal agent to execute the scripted docker block
            agent any 
            steps {
                script {
                    // Use a scripted pipeline block for maximum control
                    docker.image('cdrx/pyinstaller-windows:python3').inside('-u root') {
                        echo 'Building inside scripted docker block...'
                        
                        // We will try one last time with the most basic command structure
                        // inside this more controlled environment.
                        sh """
                            pip install --user -r requirements.txt
                            /root/.wine/drive_c/users/root/AppData/Roaming/Python/Python38/Scripts/pyinstaller --clean --onefile main.py
                        """
                    }
                }
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