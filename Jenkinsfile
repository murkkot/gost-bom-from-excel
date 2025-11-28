pipeline {
    agent none
    options {
        skipDefaultCheckout()
        disableConcurrentBuilds()
    }
    stages {
        stage("checkout scm"){
            agent any
            steps {
                script {
                    echo 'checking out scm....'
                    def scmVars = checkout scm
                    env.GIT_COMMIT = scmVars.GIT_COMMIT
                    env.GIT_BRANCH = scmVars.GIT_BRANCH
                    echo "Commit: ${env.GIT_COMMIT}"
                    echo "Branch: ${env.GIT_BRANCH}"
                }
            }
        }
        stage("read version number") {
            agent any
            steps {
                echo 'reading version number...'
                script {
                    def versionOutput = sh(script: "cat _version.py | grep -Eo '[0-9]+\\.[0-9]+\\.[0-9]+'", returnStdout: true).trim()
                    env.VERSION = versionOutput
                    // Check if tag is present for this commit
                    sh 'git fetch --tags'
                    env.GIT_TAG = sh(script: 'git describe --tags --exact-match HEAD || echo ""', returnStdout: true).trim()
                    echo "Tag found: ${env.GIT_TAG ?: 'NO TAG'}"
                    if (env.GIT_TAG) {
                        env.VERSION = env.GIT_TAG.replaceFirst(/^v?/, '')
                    }
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
                    -v "/mnt/hdd/docker/jenkins/jenkins_home/workspace/gost-bom-from-excel:/src" \
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
                echo "__version__ = \\\"${env.VERSION} build ${env.BUILD_NUMBER}\\\"" > _version.py
                sh """
                    mkdir -p release/input
                    mkdir -p release/output
                    cp -r dist/main.exe templates examples release
                    tar -cvf gbfe_${env.VERSION}_build_${env.BUILD_NUMBER}.tar -C release .
                """
                archiveArtifacts artifacts: "gbfe_${env.VERSION}_build_${env.BUILD_NUMBER}.tar", fingerprint: true
            }
        }
        stage('release') {
            agent any
            steps {
                script {
                    if (env.GIT_TAG) {
                        echo "Building release for tag: ${env.GIT_TAG}"
                        sh "mv gbfe_${env.VERSION}_build_${env.BUILD_NUMBER}.tar gost-bom-from-excel-${env.GIT_TAG}.tar"
                        createGitHubRelease(
                            credentialId: 'github-token',
                            repository: 'murkkot/gost-bom-from-excel',
                            commitish: "${env.GIT_COMMIT}",
                            tag: "${env.GIT_TAG}",
                            bodyText: 'Jenkins automatic release',
                            draft: false
                        )
                        uploadGithubReleaseAsset(
                            credentialId: 'github-token',
                            repository: 'murkkot/gost-bom-from-excel',
                            tagName: "${env.GIT_TAG}",
                            uploadAssets: [
                                [filePath: "gost-bom-from-excel-${env.GIT_TAG}.tar"]
                            ]
                        )
                    } else {
                        echo "No tag found, skipping release"
                    }
                }
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
        stage("clean") {
            agent any
            steps {
                echo 'cleaning files....'
                sh "rm -r release"
                sh  "rm *.tar"
                sh 'rm -f main.spec'
            }
        }
    }
}