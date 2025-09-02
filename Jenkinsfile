pipeline {
    agent any
    stages {
        stage("test") {
            steps {
                echo 'testing...'
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