pipeline {
    agent none
    stages {
        stage("checkout scm"){
            checkout scm
        }
        stage("read version number") {
            script {
                def versionOutput = sh(script: "cat _version.py | grep -Eo '[0-9]+\\.[0-9]+\\.[0-9]+'", returnStdout: true).trim()
                def buildNumberOutput = sh(script: "cat _version.py | grep -Eo '[0-9]+' | tail -1", returnStdout: true).trim()
                env.VERSION = versionOutput
                env.BUILD_NUMBER = buildNumberOutput
                echo "VERSION is ${env.VERSION}"
                echo "BUILD_NUMBER is ${env.BUILD_NUMBER}"
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
            sh """
                mkdir -p release/input
                mkdir -p release/output
                cp -r dist/main.exe templates release
                tar -cvf gbfe_${env.VERSION}_build_${env.BUILD_NUMBER}.tar -C release .
            """
            archiveArtifacts artifacts: "gbfe_${env.VERSION}_build_${env.BUILD_NUMBER}.tar", fingerprint: true
            sh "rm -r release"
        }
        stage("release") {
            agent any
            steps {
                echo 'releasing...'
            }

        }
    }
}