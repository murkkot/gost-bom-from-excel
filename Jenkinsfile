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
            agent {
                docker {
                    image 'cdrx/pyinstaller-windows:python3'
                    args '-u root -v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            steps {
                echo 'building...'
                echo 'building...'
                sh """
                    # Redirect stdout and stderr to files to provide a valid handle
                    pip install --user -r requirements.txt > pip_install.log 2>&1
                    
                    # Check the exit code of the pip install command
                    if [ \$? -ne 0 ]; then
                        echo "pip install failed. See pip_install.log for details."
                        cat pip_install.log
                        exit 1
                    fi
                    
                    echo "pip install successful."

                    # Also redirect pyinstaller output
                    /root/.wine/drive_c/users/root/AppData/Roaming/Python/Python38/Scripts/pyinstaller --clean --onefile main.py > pyinstaller.log 2>&1
                    
                    # Check the exit code of the pyinstaller command
                    if [ \$? -ne 0 ]; then
                        echo "PyInstaller failed. See pyinstaller.log for details."
                        cat pyinstaller.log
                        exit 1
                    fi
                    
                    echo "PyInstaller build successful."
                """
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