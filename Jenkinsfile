project = "gem-py"
team = "gem-py"

pipeline {
     environment {
           ARTIFACTORY = credentials("all-team-artifactory")
     }
    agent {
        label 'agent-team'
    }
    stages {
        stage('Build') {
            steps {
                script {
                    if(BRANCH_NAME == "development") {
                        environment = "preprod"
                    }else if(BRANCH_NAME == "acceptance") {
                        environment = "uat"
                    }else if(BRANCH_NAME == "master") {
                        environment = "prod"
                    }else{
                        environment = "scratch"
                    }
                }
                sh """
                python3.6 -m pip install -e .[testing] --index https://${ARTIFACTORY}@artifactory.tools.digital.engie.com/artifactory/api/pypi/${project}-${team}-pypi-${environment}/simple --upgrade
                """
            }
        }
        stage('Test') {
            steps {
                sh """
                nosetests test --exe --with-doctest --with-xunit --xunit-file test-results.xml --with-coverage --cover-erase --cover-package=pycommon_server/. --cover-min-percentage=93 --cover-html
                """
            }
        }
        stage('Publish test results') {
            steps {
                junit '**/test-results.xml'
            }
        }
        stage('Deploy') {
            steps {
                sh """ cat << EOF > .pypirc
[distutils]
index-servers=local
[local]
repository=https://artifactory.tools.digital.engie.com/artifactory/api/pypi/${project}-${team}-pypi-${environment}
username=${ARTIFACTORY_USR}
password=${ARTIFACTORY_PSW}
EOF
"""
                sh """
                python3.6 setup.py sdist
                twine upload dist/* -r local --config-file ./.pypirc
                """
            }
        }
        stage('Generate coverage') {
            steps {
                sh """
                coverage xml -o cobertura.xml
                """
            }
        }
        stage('Record master coverage') {
            when { branch 'master' }
            steps {
                script {
                    currentBuild.result = 'SUCCESS'
                 }
                step([$class: 'MasterCoverageAction', scmVars: [GIT_URL: env.GIT_URL]])
            }
        }
        stage('PR Coverage to Github') {
            when { allOf {not { branch 'master' }; expression { return env.CHANGE_ID != null }} }
            steps {
                script {
                    currentBuild.result = 'SUCCESS'
                 }
                step([$class: 'CompareCoverageAction', publishResultAs: 'statusCheck', scmVars: [GIT_URL: env.GIT_URL]])
            }
        }
    }
}
