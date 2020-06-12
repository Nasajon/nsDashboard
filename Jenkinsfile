node('master') {
	try {
		properties([disableConcurrentBuilds()])

		stage('Checkout') {
            timeout(time: 300, unit: 'SECONDS') {
                checkout scm
            }
		}

		stage('Build') {
            bat 'build.bat'
		}

	} catch (e) {
		currentBuild.result = "FAILED"
    	notifyFailed()
    	throw e
	} finally {
		if(currentBuild.result == "FAILED"){
            notifyFailed()
        }
	}
}

def notifyFailed() {
  emailext(
		subject: '''${DEFAULT_SUBJECT}''',
		body: '''${DEFAULT_CONTENT}''',
		recipientProviders: [[$class: 'CulpritsRecipientProvider'],
							[$class: 'DevelopersRecipientProvider'],
							[$class: 'RequesterRecipientProvider'],
							[$class: 'UpstreamComitterRecipientProvider']],
		to: "${env.EMAILS_FAILED}"
	)
}
