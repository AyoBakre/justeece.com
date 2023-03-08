pipeline {
   agent any
   stages {
        stage('Master Branch Deploy Code') {
            when {
                branch 'master'
            }
            steps {
                sh """
                echo "Building Artifact from Master branch"
                """

                sshagent (credentials: ['builder_old_testserver']) {
                    sh 'ssh -t -t builder@test.linuxjobber.com -p 2222 -o StrictHostKeyChecking=no "cd /justeece/prod/www && sudo git pull origin master && cd .. && sudo docker build -t registry.gitlab.com/showpopulous/justeece/justeece:prod . && sudo docker push registry.gitlab.com/showpopulous/justeece/justeece:prod" '

                }
 
                sh """
                echo "Deploying Code from Master branch"
                """
            }
        }
        stage('Integration Branch Deploy Code') {
            when {
                branch 'integration'
            }
            steps {
                sh """
                echo "Building integration branch"
                """
 
                sshagent (credentials: ['builder_old_testserver']) {
                    sh 'ssh -t -t builder@test.linuxjobber.com -p 2222 -o StrictHostKeyChecking=no "cd /justeece/int/www && sudo git pull origin integration --no-edit && cd .. && sudo docker build -t justeece:integration . && sudo docker tag justeece:integration registry.gitlab.com/showpopulous/justeece/justeece:integration && sudo docker push registry.gitlab.com/showpopulous/justeece/justeece:integration && kubectl rollout restart deployment/justeecedeploy --namespace justeece" '
                     sh 'ssh -t -t builder@test.linuxjobber.com -p 2222 -o StrictHostKeyChecking=no "sudo docker start test_justeece && cd /qa/qa_justeece/mount/justeece/test && sudo docker exec test_justeece ./run_automated_test_justeece.sh integration.justeece.com"'
                }
                
                sh """
                echo "Deploying Code from integration branch"
                """
           }
        }
        stage('Developer Branch Deploy Code without testing') {
            when {
                expression {env.BRANCH_NAME.substring(0,3) == 'dev'}
            }
            environment {
                DEVBRANCH = "${env.BRANCH_NAME}"
                ENVIRONMENTNUM="${env.BRANCH_NAME.substring(3,4)}"
            }
                steps {
                    script{
                            sshagent (credentials: ['builder_old_testserver']) {
                                sh 'ssh -t -t builder@test.linuxjobber.com -p 2222 -o StrictHostKeyChecking=no "cd /justeece/dev${ENVIRONMENTNUM}/www && sudo git pull --no-edit origin ${DEVBRANCH} && sudo git checkout ${DEVBRANCH} && sudo git fetch && cd .. && sudo docker build -t justeece:dev${ENVIRONMENTNUM} . && sudo docker tag justeece:dev${ENVIRONMENTNUM} registry.gitlab.com/showpopulous/justeece/justeece:dev${ENVIRONMENTNUM} && sudo docker push registry.gitlab.com/showpopulous/justeece/justeece:dev${ENVIRONMENTNUM} && kubectl rollout restart deployment/justeecedev${ENVIRONMENTNUM}deploy --namespace justeece" '
                            }    
                    } 
                    
                            sh """
                            echo "Deploying Code from branch"
                            """
                    }
        }
        stage('Developer Branch Deploy Code with testing') {
            when {
                expression {env.BRANCH_NAME.substring(0,4) == 'tdev'}
            }
            environment {
                DEVBRANCH = "${env.BRANCH_NAME}"
                ENVIRONMENTNUM="${env.BRANCH_NAME.substring(4,5)}"
            }
            steps{
                            sh """
                            echo "Running SonarQube"
                            """

                            script{
                                def scannerHome = tool 'SonarQubeScanner';
                                withSonarQubeEnv() {
                                    sh "${scannerHome}/bin/sonar-scanner"
                                }
                            }

                            sh """
                            echo "Building and running tests"
                            """
                            sshagent (credentials: ['builder_old_testserver']) {
                                sh 'ssh -t -t builder@test.linuxjobber.com -p 2222 -o StrictHostKeyChecking=no "cd /justeece/dev${ENVIRONMENTNUM}/www && sudo git pull --no-edit origin ${DEVBRANCH} && sudo git checkout ${DEVBRANCH} && sudo git fetch && cd .. && sudo docker build -t justeece:dev${ENVIRONMENTNUM} . && sudo docker tag justeece:dev${ENVIRONMENTNUM} registry.gitlab.com/showpopulous/justeece/justeece:dev${ENVIRONMENTNUM} && sudo docker push registry.gitlab.com/showpopulous/justeece/justeece:dev${ENVIRONMENTNUM} && kubectl rollout restart deployment/justeecedev${ENVIRONMENTNUM}deploy --namespace justeece" '
                                sh 'ssh -t -t builder@test.linuxjobber.com -p 2222 -o StrictHostKeyChecking=no "sudo docker start test_justeece && cd /qa/qa_justeece/mount/justeece/test && sudo docker exec test_justeece ./run_automated_test_justeece.sh dev${ENVIRONMENTNUM}.justeece.com"'
            }
            }
            }
        }
}
