pipeline {
    agent any

    triggers {
        githubPush()
    }

    stages {
        stage('Clone Repository') {
            steps {
                echo 'Cloning repository...'
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Installing dependencies...'
                sh 'pip install -r requirements.txt' // Flask dependencies
            }
        }

        stage('Run Unit Tests') {
            steps {
                echo 'Running unit tests...'
                sh 'pytest' // Ensure pytest is used for Flask testing
            }
        }

        stage('Build Application') {
            steps {
                echo 'Building the application...'
                sh 'python setup.py build' // Adjust based on your Flask app structure
            }
        }

        stage('Deploy Application') {
            steps {
                echo 'Deploying the application...'
                sh './deploy.sh' // Replace with your Flask deployment script/command
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed! Check the logs for details.'
        }
    }
}
