pipeline {
    agent any
    stages {
        stage("test") {
            steps {
                echo 'testing...'
                sh "pip install -r requirements.txt"
                sh "pytest -v"
            }
        }
        stage("build") {
            steps {
                echo 'building...'
            }
        }
        stage("release") {
            steps {
                echo 'releasing...'
            }

        }
    }
}