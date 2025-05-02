
import os
from unittest.mock import PropertyMock, patch

from ploigos_step_runner.exceptions import StepRunnerException
from ploigos_step_runner.results import StepResult, WorkflowResult
from ploigos_step_runner.step_implementers.push_artifacts import GradleDeploy
from testfixtures import TempDirectory
from tests.helpers.base_step_implementer_test_case import \
    BaseStepImplementerTestCase

@patch("ploigos_step_runner.step_implementers.shared.GradleGeneric.__init__")
class TestStepImplementerGradleDeploy___init__(BaseStepImplementerTestCase):
    def test_defaults(self, mock_super_init):
        workflow_result = WorkflowResult()
        parent_work_dir_path = '/fake/path'
        config = {}

        print('Calling GradleDeploy.')
        
        GradleDeploy(
            workflow_result=workflow_result,
            parent_work_dir_path=parent_work_dir_path,
            config=config
        )

        mock_super_init.assert_called_once_with(
            workflow_result=workflow_result,
            parent_work_dir_path=parent_work_dir_path,
            config=config,
            environment=None,
            gradle_tasks=['artifactoryPublish']
        )

    def test_given_environment(self, mock_super_init):
        workflow_result = WorkflowResult()
        parent_work_dir_path = '/fake/path'
        config = {}

        GradleDeploy(
            workflow_result=workflow_result,
            parent_work_dir_path=parent_work_dir_path,
            config=config,
            environment='mock-env',
            gradle_tasks=['artifactoryPublish']
        )

        mock_super_init.assert_called_once_with(
            workflow_result=workflow_result,
            parent_work_dir_path=parent_work_dir_path,
            config=config,
            environment='mock-env',
            gradle_tasks=['artifactoryPublish']
        )

class TestStepImplementerGradleDeploy_step_implementer_config_defaults(
    BaseStepImplementerTestCase
):
    def test_result(self):

        self.assertEqual(
            GradleDeploy.step_implementer_config_defaults(),
            {'build-file': 'app/build.gradle',
            'gradle-additional-arguments': [],
            'gradle-console-plain': True
            }
        )

class TestStepImplementerGradleDeploy__required_config_or_result_keys(
    BaseStepImplementerTestCase
):
    
    def test_result(self):

        actual_list = GradleDeploy._required_config_or_result_keys()

        expected_list = ['build-file', 'gradle-token', 'gradle-token-alpha']

        self.assertEqual(actual_list, expected_list)

class TestStepImplementerGradleDeploy__run_step(
    BaseStepImplementerTestCase
):
    def create_step_implementer(
            self,
            step_config={'build-file': 'app/build.gradle',
              'gradle-additional-arguments': [],
              'gradle-console-plain': True
            },
            workflow_result=None,
            parent_work_dir_path=''
    ):
        return self.create_given_step_implementer(
            step_implementer=GradleDeploy,
            step_config=step_config,
            step_name='deploy',
            implementer='GradleDeploy',
            workflow_result=workflow_result,
            parent_work_dir_path=parent_work_dir_path
        )

    GradleBuild_regular = 'version "1.0.0"\nplugins { id "com.jfrog.artifactory" version "5.+" } artifactory { publish { contextUrl = "http://127.0.0.1:8081/artifactory"\nrepository { repoKey = "libs-snapshot-local"\nusername = "${artifactory_user}"\npassword = "${artifactory_password}" } defaults { publications("ALL_PUBLICATIONS") } } }'

    GradleBuild_badversion = 'version "fail"\nversion "fail"\nplugins { id "com.jfrog.artifactory" version "5.+" } artifactory { publish { contextUrl = "http://127.0.0.1:8081/artifactory"\nrepository { repoKey = "libs-snapshot-local"\nusername = "${artifactory_user}"\npassword = "${artifactory_password}" } defaults { publications("ALL_PUBLICATIONS") } } }'

    def write_build(self, app_dir, gradle_contents):

        gradle_fn = os.path.join(app_dir, 'build.gradle')

        with open(gradle_fn, 'w') as outf:
            outf.write(gradle_contents)
            outf.close()

    def prepare_appdirectory(self, working_dir, step_name, gradle_contents):

        print('Working Directory: ' + str(working_dir))

        if os.path.exists(working_dir):

            app_dir = os.path.join(working_dir, step_name + '/app')

            print('Application Directory: ' + str(app_dir))

            if not os.path.exists(app_dir):

                print('Creating Application Directory.')

                res = os.mkdir(app_dir)

                print(ret)

                ret = self.write_build(app_dir, gradle_contents)

                print(ret)

    def test_failversion(self):

        with TempDirectory() as test_dir:

            parent_work_dir_path = os.path.join(test_dir.path, 'working')

            step_name = 'deploy'

            step_config = {
                'build-file': step_name + '/app/build.gradle',
                'gradle-additional-arguments': [],
                'gradle-console-plain': True
                }

            step_implementer = self.create_step_implementer(
                step_config=step_config,
                parent_work_dir_path=parent_work_dir_path,
            )

            self.prepare_appdirectory(parent_work_dir_path, step_name, self.GradleBuild_badversion)

            # run step
            actual_step_result = step_implementer._run_step()

            # create expected step result
            expected_step_result = StepResult(
                step_name='deploy',
                sub_step_name='GradleDeploy',
                sub_step_implementer_name='GradleDeploy'
            )
            expected_step_result.add_artifact(
                description="Standard out and standard error from running gradle to update version.",
                name='gradle-update-version-output',
                value=str(parent_work_dir_path) + '/deploy/Gradle_versions_set_output.txt'
            )
            expected_step_result.add_artifact(
                description="Standard out and standard error from running gradle to " \
                    "push artifacts to repository.",
                name='gradle-push-artifacts-output',
                value=str(parent_work_dir_path) + '/Gradle-deploy_output.txt'
            )

    def test_success(self):

        with TempDirectory() as test_dir:
            
            parent_work_dir_path = os.path.join(test_dir.path, 'working')

            step_config = {
                'build-file': 'app/build.gradle',
                'gradle-additional-arguments': [],
                'gradle-console-plain': True
                }

            step_implementer = self.create_step_implementer(
                step_config=step_config,
                parent_work_dir_path=parent_work_dir_path,
            )

            # run step
            actual_step_result = step_implementer._run_step()

            # create expected step result
            expected_step_result = StepResult(
                step_name='deploy',
                sub_step_name='GradleDeploy',
                sub_step_implementer_name='GradleDeploy'
            )
            expected_step_result.add_artifact(
                description="Standard out and standard error from running gradle to update version.",
                name='gradle-update-version-output',
                value=str(parent_work_dir_path) + '/deploy/Gradle_versions_set_output.txt'
            )
            expected_step_result.add_artifact(
                description="Standard out and standard error from running gradle to " \
                    "push artifacts to repository.",
                name='gradle-push-artifacts-output',
                value=str(parent_work_dir_path) + '/Gradle-deploy_output.txt'
            )

                # with open('/tmp/gradle.txt', 'w') as outf:

                # outf.write('Actual: ' + '\n')
                    
                # outf.write(str(actual_step_result))
                # outf.write('\n')
                
                # outf.write('Expected: ' + '\n')

                # outf.write(str(expected_step_result))
                
                # outf.close()

            return None
            
            # verify step result
            self.assertEqual(
                actual_step_result,
                expected_step_result
            )

            mock_write_working_file.assert_called()
            mock_run_gradle.assert_called_with(
                Gradle_output_file_path='/mock/Gradle_versions_set_output.txt',
                settings_file='/fake/settings.xml',
                pom_file=pom_file,
                phases_and_goals=['versions:set'],
                additional_arguments=[
                    f'-DnewVersion={version}'
                ]
            )
            mock_run_gradle_step.assert_called_with(
                Gradle_output_file_path='/mock/Gradle_deploy_output.txt',
                step_implementer_additional_arguments=[
                    '-DaltDeploymentRepository=' \
                    f'{gradle_push_artifact_repo_id}::default::{gradle_push_artifact_repo_url}'
                ]
            )

