def remote = [:]

pipeline{
    agent any

    environment{
        branch = "${params['branch']}"
        image_name = "${params['image_name']}"
        image_tag = "${params['image_tag']}"
        host = "${params['host']}"
        user = "${params['user']}"
        password = "${params['password']}"
    }

    stages{

        stage("Git Cloning"){
            steps{
                git branch: '${branch}', credentialsId: 'github_fatalerrortan_token', url: 'https://github.com/fatalerrortan/Binance_Trade_Tool'
            }
        }
    
        stage("Building und pushing Docker Image"){
            steps{
                script {
                    def docker_image = docker.build "${image_name}"
                    // docker_image.inside {
                    //         sh 'uname -a'
                    //         sh 'cd /opt && ls -al'
                    // } 
                    
                    withDockerRegistry(credentialsId: 'dockerhub_fatalerrortxl_token') {
                        docker_image.push("${image_tag}")
                    }
                }
            }
        }

        stage("connecting to the target server"){
            steps{
                script { 

                    // param = "${params['param_A']}"

                    remote.name = "${host}"
                    remote.host = "${host}"
                    remote.user = "${user}"
                    remote.password = "${password}"
                    remote.allowAnyHosts = true

                    sshCommand remote: remote, command: "hostname"
                }
            }

            post{
                always{
                    sh "docker rmi ${image_name}:${image_tag}"
                    sh "docker image ls -a"
                }
            }
        }

        stage("pulling the target docker image"){
            steps{
                script{
                    sshCommand remote: remote, command: "docker pull ${image_name}:${image_tag}"
                }
            }           
        }

        stage("stop and remove previous container"){
            steps{
                script{
                    sshCommand remote: remote, command: "[ -z \$(docker ps -a -q -f 'label=app=abtt') ] && echo 'no running abtt containers exists' || docker rm -f \$(docker ps -a -q -f 'label=app=abtt')"
                }
            }
        }

        stage("run container via docker compose"){
            steps{
                script{

                    def docker_compose_yml = readFile(file: "docker-compose.yml")
                    // sshCommand remote: remote, command: "docker run -dit --name abtt --privileged --network host ${image_name}:${image_tag}"

                    sshCommand remote: remote, command: "echo '${docker_compose_yml}' > docker-compose.yml"
                    
                    sshCommand remote: remote, command: "export IMAGE=${image_name}:${image_tag} && docker-compose config && docker-compose up -d"
                 
                    sshCommand remote: remote, command: "yes | rm docker-compose.yml"
                    
                    sshCommand remote: remote, command: "docker container ls -a"
                }
            }
        }
    }

    post{
        always{
            cleanWs()  
        }
    }
}
