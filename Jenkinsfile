pipeline {
    agent any
    
    stages {
        stage('Welcome'){
            steps {
                echo "This pipeline is from Gitlab repo!!!"
            }
        }
        stage('1st_stage_Built'){
            steps {
                echo "Beginning of build"
                echo "End of the build"
            }
        }
        stage('2nd_stage_Test'){
            steps {
                echo "Beginning of test"
                sh "pwd"
                sh '''
                ls -la
                cat sdsfsdsdfsdf.md
                '''
                echo "End of the test"
            }
        }
        stage('3rd_stage_Deploy'){
            steps {
                echo "Beginning of build"
                sh "hostname"
                echo "End of the build"
            }
        }
    }
}
