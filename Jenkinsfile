node('master') {
	def dirArtifactName = "nsDashboard"
	def artifactUrl = "github.com/Nasajon/${dirArtifactName}.git"
	def artifactId = "nsDash"
	def artifactIdCreateUser = "nsDashCreateUser"
	def artifactBuildPath = "${env.WORKSPACE}\\${dirArtifactName}\\"
	def nasajonCIBaseDir = "${env.NASAJON_CI_BASE_DIR}"
	def branchName = "${env.BRANCH_NAME}"
	try {
		properties([disableConcurrentBuilds()])

		stage('Checkout') {
			dir("${dirArtifactName}") {
                	checkout scm
			    timeout(time: 3600, unit: 'SECONDS') {
          		}
			}
		}

		stage('Build') {
			

			dir("${nasajonCIBaseDir}\\build\\erp") {
				bat 'init.bat'
			}

			generateVersionNumber()

			dir("${artifactBuildPath}") {
				bat 'npm install'
				bat 'npm run build_windows'
				bat 'jenkins_build.bat'
			}
		}
		if(!branchName.startsWith("PR")){
			stage('Deploy') {
				dir("${nasajonCIBaseDir}\\build\\erp") {
					bat "sign_file.bat ${env.WORKSPACE}\\output\\bin\\${artifactId}.exe"

					bat "deploy.bat ${artifactBuildPath} exe ${env.WORKSPACE}\\output\\bin\\${artifactId}.exe ${artifactId}"

					bat "sign_file.bat ${env.WORKSPACE}\\output\\bin\\${artifactIdCreateUser}.exe"

					bat "deploy.bat ${artifactBuildPath} exe ${env.WORKSPACE}\\output\\bin\\${artifactIdCreateUser}.exe ${artifactIdCreateUser}"
				}

				def subFolders = currentBuild.displayName.replace(".", "/")

				withAWS(credentials: 'JENKINS_AWS_CREDENTIALS') {
					def bucket = env.ERP_BUCKET

					//Upload do artefato
					s3Upload(
						file: "${env.WORKSPACE}\\output\\bin\\${artifactId}.exe",
						bucket:"${bucket}",
						path:"erp-update/artifacts/${artifactId}/${subFolders}/${artifactId}.exe",
						acl:'PublicRead')

					s3Upload(
						file: "${env.WORKSPACE}\\output\\bin\\${artifactIdCreateUser}.exe",
						bucket:"${bucket}",
						path:"erp-update/artifacts/${artifactId}/${subFolders}/${artifactIdCreateUser}.exe",
						acl:'PublicRead')
				}

				def checksum = powershell(
					returnStdout: true,
					script: "(Get-FileHash -Algorithm MD5 -Path '${env.WORKSPACE}\\output\\bin\\${artifactId}.exe' | Select -ExpandProperty Hash).ToLower()"
				)

				def isMaster = (env.BRANCH_NAME == 'master')
				def version = currentBuild.displayName
				def dateTime = new Date().format("yyyy-MM-dd HH:mm")

				//Registra o build na Api do diretório
				def body = """
					{
						\"nome\": \"${artifactId}.exe\",
						\"versao\": \"${version}\",
						\"master\": ${isMaster},
						\"datahora\": \"${dateTime}\",
						\"checksum\":\"${checksum.trim()}\",
						\"pathdestino\": \".\",
						\"tipo\": \"exe\",
						\"url\": \"artifacts/${artifactId}/${subFolders}/${artifactId}.exe\",
						\"artefatosfilhos\": [\"${artifactIdCreateUser}.exe\"]
					}
				"""
			}
		}

	} catch (e) {
		currentBuild.result = "FAILED"
    	notifyFailed()
    	throw e
	} finally {
		stage('Clean') {
			dir("${env.WORKSPACE}\\output") {
				deleteDir()
			}
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

def generateVersionNumber() {
	def version = ""
	def branchName = "${env.BRANCH_NAME}"

	if (branchName == "master") {
		version = "2.${env.CURRENT_SPRINT}.0.${env.BUILD_NUMBER}"
	} else if (branchName.startsWith("v2.")) {
		def sprint = branchName.substring(3)
		version = "2.${sprint}.${env.BUILD_NUMBER}.0"
	} else {
		version = "2.0.0.0"
	}

	println("Version: " + version)

	currentBuild.displayName = version

	def file_version_template = readFile("${env.WORKSPACE}\\nsDashboard\\version_info.txt")

	file_version_template = file_version_template
		.replaceAll("__VERSION_INFO1__", version.replace(".", ", "))
		.replaceAll("__VERSION_INFO2__", version)

	writeFile file: "${env.WORKSPACE}\\output\\VersionInfo", text: version
	writeFile file: "${env.WORKSPACE}\\output\\VersionInfo2", text: file_version_template
}
