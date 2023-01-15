pipeline {
    agent {
        label 'Home'
    }
    environment {
        SECRET_FILE = credentials('secret-file')
    }
    stages {
        stage('Build') {
            steps {
                script {
                    // Build doownloader-app docker
                    dir("downloader-app") {
                        sh 'ls -a'
                        sh 'docker-compose --env-file $SECRET_FILE build'
                    }

                    // Build back-end
                    dir("server-app") {
                        sh 'ls -a'
                        sh 'docker-compose --env-file $SECRET_FILE build'
                    }

                    // Build front-end
                    dir("dashboard-app") {
                        sh 'ls -a'
                        sh 'docker-compose --env-file $SECRET_FILE build'
                    }
                }
            }
        }
        stage('Setup') {
            steps {
                script {
                    // TODO: Copy .env

                    // Bring down old downloader-app docker
                    dir("downloader-app") {
                        sh 'docker-compose down'
                        sh 'docker-compose rm -f'
                    }

                    // Bring down old back-entered
                    dir("server-app") {
                        sh 'docker-compose down'
                        sh 'docker-compose rm -f'
                    }
                    
                    // Bring down old front-end
                    dir("dashboard-app") {
                        sh 'docker-compose down'
                        sh 'docker-compose rm -f'
                    }
                }
            }
        }
        stage('Deploy') {
            steps {
                script {
                    // Bring up downloader-app
                    dir("downloader-app") {
                        sh 'docker-compose --env-file $SECRET_FILE up -d'
                        sleep 5
                        sh 'docker ps -a'
                    }

                    // Bring up back-end
                    dir("server-app") {
                        sh 'docker-compose --env-file $SECRET_FILE up -d'
                        sleep 5
                        sh 'docker ps -a'
                    }

                    // Bring up front-end
                    dir("dashboard-app") {
                        sh 'docker-compose --env-file $SECRET_FILE up -d'
                        sleep 5
                        sh 'docker ps -a'
                    }
                }
            }
        }
    }
}