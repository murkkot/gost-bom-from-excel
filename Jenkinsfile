pipeline {
    agent none
    options {
        skipDefaultCheckout()
    }
    stages {
        stage("checkout scm"){
            agent any
            steps {
                echo 'checking out scm....'
                checkout scm
            }
        }
        stage("read version number") {
            agent any
            steps {
                echo 'reading version number...'
                script {
                    def versionOutput = sh(script: "cat _version.py | grep -Eo '[0-9]+\\.[0-9]+\\.[0-9]+'", returnStdout: true).trim()
                    env.VERSION = versionOutput
                    echo "VERSION is ${env.VERSION}"
                    echo "BUILD_NUMBER is ${env.BUILD_NUMBER}"
                }
            }
        }
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
                echo "${WORKSPACE}"
                sh """
                    docker run --rm \
                    -v "/mnt/ssdpci/docker/jenkins/jenkins_home/workspace/gost-bom-from-excel:/src" \
                    -w /src \
                    cdrx/pyinstaller-windows:python3 \
                    "pyinstaller --clean --onefile main.py"
                """
            }
        }
        stage("archive artifact") {
            agent any
            steps {
                echo 'archiving...'
                sh """
                    mkdir -p release/input
                    mkdir -p release/output
                    cp -r dist/main.exe templates release
                    tar -cvf gbfe_${env.VERSION}_build_${env.BUILD_NUMBER}.tar -C release .
                    echo "__version__ = \\\"${env.VERSION} build ${env.BUILD_NUMBER}\\\"" > _version.py
                """
                archiveArtifacts artifacts: "gbfe_${env.VERSION}_build_${env.BUILD_NUMBER}.tar", fingerprint: true
                sh "rm -r release"
            }
        }
        stage("push version file") {
            agent any
            steps {
                echo 'pushing version file...'
                withCredentials([gitUsernamePassword(credentialsId: 'github-credentials', gitToolName: 'Default')]) {
                    sh """
                        git config user.name "jenkins-cli"
                        git config user.email "jenkins@server"
                        git add _version.py
                        git commit -m "Update version file from Jenkins build ${BUILD_NUMBER}"
                        git push origin HEAD:main
                    """
                }
            }
        }
        stage("release") {
            agent any
            when { tag "*" }
            steps {
                script {
                    def tag = sh(script: 'git describe --tags --exact-match HEAD', returnStdout: true).trim()
                    echo "Current Git tag(s): ${tag}"
                }
            }
        }
    }
}