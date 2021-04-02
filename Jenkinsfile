pipeline {
    // Run the pipeline on the NTS specific agent
    agent { label 'nts' }

    // Parameters are available as environment variables to 'sh' steps (several of these parameters are used by the 'buildtools' python scripts)
    parameters {
        string(name: 'BITBUCKET_PROJECT',
            description: 'The bitbucket project tag, sent from Bitbucket "Parameterized build for Jenkins" plugin.',
            defaultValue: 'ISN'
        )
        string(name: 'BITBUCKET_REPO',
            description: 'The bitbucket project repo_slug, sent from Bitbucket "Parameterized build for Jenkins" plugin.',
            defaultValue: 'buildtools'
        )
        string(name: 'PR_ID',
            description: 'Pull request ID, sent from Bitbucket "Parameterized build for Jenkins" plugin.'
        )
        string(name: 'PR_AUTHOR',
            description: 'Pull request Author, sent from Bitbucket "Parameterized build for Jenkins" plugin.'
        )
        string(name: 'PR_DESTINATION',
            description: 'Pull request destination branch, sent from Bitbucket "Parameterized build for Jenkins" plugin.'
        )
        string(name: 'PR_TITLE',
            description: 'Pull request title, sent from Bitbucket "Parameterized build for Jenkins" plugin.'
        )
        string(name: 'PR_DESCRIPTION',
            description: 'Pull request description, sent from Bitbucket "Parameterized build for Jenkins" plugin (only when the pull request is first opened).',
            defaultValue: ' '
        )
        string(name: 'PR_UPDATE',
            description: 'Is this an update to an existing pull request? Sent from Bitbucket "Parameterized build for Jenkins" plugin.',
            defaultValue: 'no'
        )
    }

    options {
        ansiColor('xterm')
    }

    environment {
        BITBUCKET_URL = 'https://git.uoregon.edu'
        PR_URL = "${BITBUCKET_URL}/projects/${params.BITBUCKET_PROJECT}/repos/${params.BITBUCKET_REPO}/pull-requests/${params.PR_ID}"
        TEST_REPORT_FILE = "test_report.xml"
    }

    stages {
        stage('Abort if missing params') {
            when {
                expression { return params.PR_ID == null }
            }
            steps {
                script {
                    currentBuild.result = 'NOT_BUILT'
                    error('''Missing required parameters to run this pipeline. NOTE: This is expected for the
                        *first build for each new git branch* in this multibranch pipeline. (the "Parameterized 
                        build for Jenkins" Bitbucket plugin triggers a build with missing parameters when a new 
                        branch is pushed to Bitbucket.)''')
                }
            }
        }
        stage('Prep workspace') {
            steps {
                script {
                    // Determine the 'GIT_COMMIT' for this build (needed to POST 'build statuses' to Bitbucket)
                    GIT_COMMIT = sh(script: 'git log -n 1 --format=%H', returnStdout: true).trim()
                }
                withPythonEnv('python3') {
                    sh 'pip install --upgrade pip'
                    sh '''python3 -m pip install --user --force-reinstall --upgrade 'ntsbuildtools==1.2.6' '''
                }
            }
        }
        stage('Notify bitbucket that build started') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'nts_git_uoregon_api', passwordVariable: 'BITBUCKET_PASSWORD', usernameVariable: 'BITBUCKET_USER')]) {
                    sh "buildtools post bitbucket build-status --commit ${GIT_COMMIT} --build-status STARTED"
                }
            }
        }
        stage('Notify Teams channel') {
            steps {
                withCredentials([string(credentialsId: 'nts_buildtools_CICD_teams_channel_webhook', variable: 'TEAMS_WEBHOOK_URL')]) {
                    sh 'buildtools post teams card pull-request'
                }
            }
        }

        stage('Test') {
            steps {
                withPythonEnv('python3') {
                        sh "pytest --junitxml=${TEST_REPORT_FILE} || true"
                        junit(keepLongStdio: true, healthScaleFactor: 100.0, testResults: TEST_REPORT_FILE)
                }
            }
        }

        stage('Package') {
            steps {
                withPythonEnv('python3') {
                    sh 'python setup.py sdist'
                }
                archiveArtifacts(artifacts: "${TEST_REPORT_FILE},dist/*", followSymlinks: false)
            }
        }

        stage('Build Status Notifications') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'nts_git_uoregon_api', passwordVariable: 'BITBUCKET_PASSWORD', usernameVariable: 'BITBUCKET_USER')]) {
                    // Set the 'build status' in Bitbucket
                    sh "buildtools post bitbucket build-status --commit ${GIT_COMMIT} --build-status ${currentBuild.currentResult}"
                    // Notify bitbucket of changes (pull request comment)
                    sh "buildtools post bitbucket pr-comment --build-annotation --build-status ${currentBuild.currentResult} --file *.egg-info/PKG-INFO"
                }

                withCredentials([string(credentialsId: 'nts_buildtools_CICD_teams_channel_webhook', variable: 'TEAMS_WEBHOOK_URL')]) {
                    // Notify MSFT Teams of build status
                    sh "buildtools post teams card build-status ${currentBuild.currentResult} --pull-request-url ${PR_URL} --file *.egg-info/PKG-INFO"
                }
            }
        }

        // TODO Only ask for approval if building off of a "X.Y.Z tag".
        stage('Request Release Approval') {
            steps {
                // Get user input before proceeding with a release to PyPI
                // Some colorized ascii to call attention to which version is being deployed to PyPI
                script {
                    gitCommit = sh(returnStdout: true, script: 'git rev-parse HEAD').trim()
                    version = sh(returnStdout: true, script: 'grep ^Version: *.egg-info/PKG-INFO').trim()
                }
                sh """set +x
                echo "\033[35m================================================================================"
                printf "== \n== The version to be deployed is ${version}\n"
                printf "== Corresponds to git commit: ${gitCommit} \n==\n"
                printf '== \033[32m--> See the "Test Pull Request" for the e2e Automated Test output: \033[34m https://git.uoregon.edu/projects/ISN/repos/buildtools/pull-requests/2/overview\n'
                printf "== \033[32m--> See the 'Test Teams Channel' for the e2e Automated Test output: \033[34m https://teams.microsoft.com/l/channel/19%%3a3ae7d6ab87634991b95460a86c38023a%%40thread.tacv2/General?groupId=fbad72b7-0313-4b24-a114-d956c46e911c&tenantId=8f0b198f-f447-4cfe-ba03-526b46c661f8\n"
                echo "\033[35m================================================================================\033[0m"
                set -x
                """
                // Deployments must be confirmed within 30 minutes
                // TODO can we expose this approval process through a Jenkins Web API?
                timeout(30) {
                    input('Are you certain that you want to deploy this version to the PyPI package index?')
                }
            }
        }
        stage('Publish to PyPI') {
            steps {
                withPythonEnv('python3') {
                    withCredentials([usernamePassword(credentialsId: 'nts_pypi', passwordVariable: 'PASS', usernameVariable: 'USER')]) {
                        sh 'pip install twine'
                        sh 'twine upload dist/* -u \$USER -p \$PASS --verbose'
                    }
                }
            }
        }
    }

    post {
        success {
            withCredentials([usernamePassword(credentialsId: 'nts_git_uoregon_api', passwordVariable: 'BITBUCKET_PASSWORD', usernameVariable: 'BITBUCKET_USER')]) {
                // Set the 'build status' in Bitbucket (with the new 'deployment' build-key, so it registers as a 2nd build in Bitbucket)
                sh "buildtools post bitbucket build-status --build-key deployment --commit ${GIT_COMMIT} --build-status ${currentBuild.currentResult}"
            }

            withCredentials([string(credentialsId: 'nts_buildtools_CICD_teams_channel_webhook', variable: 'TEAMS_WEBHOOK_URL')]) {
                // Notify MSFT Teams of Deployment status
                sh "buildtools post teams card build-status ${currentBuild.currentResult} --build-type DEPLOYMENT --pull-request-url ${PR_URL} --file *.egg-info/PKG-INFO"
            }
        }
    }
}