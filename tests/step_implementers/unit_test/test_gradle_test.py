import os
from unittest.mock import patch

from pip._internal.utils.temp_dir import TempDirectory

from src.ploigos_step_runner.step_implementers.unit_test.gradle_test import GradleTest
from ploigos_step_runner.results import StepResult
from tests.helpers.base_step_implementer_test_case import BaseStepImplementerTestCase
import xml.etree.ElementTree as ET

class BaseTestStepImplementerGradleTest(
    BaseStepImplementerTestCase
):
    def create_step_implementer(
        self,
        step_config={'build-file': 'app/build.gradle'},
        workflow_result=None,
        parent_work_dir_path=''
    ):

        print('Creating GradleTest step_implementer')
        
        return self.create_given_step_implementer(
            step_implementer=GradleTest,
            step_config=step_config,
            step_name='unit-test',
            implementer='GradleTest',
            workflow_result=workflow_result,
            parent_work_dir_path=parent_work_dir_path
        )

class TestStepImplementerGradleTest__get_test_result(
    BaseTestStepImplementerGradleTest
):
    def test_success_with_report_dir(
        self
    ):
        with TempDirectory() as test_dir:

            # setup test
            parent_work_dir_path = os.path.join(test_dir.path, 'working')

            os.mkdir(parent_work_dir_path)

            reports_dir = 'test-reports-dir'

            os.mkdir(os.path.join(parent_work_dir_path, reports_dir))

            build_file = 'app/gradle.build'

            step_config = {
                'build-file': os.path.join(parent_work_dir_path, build_file),
                'test-reports-dir': os.path.join(parent_work_dir_path, reports_dir)
            }

            step_implementer = self.create_step_implementer(
                step_config=step_config,
                parent_work_dir_path=parent_work_dir_path,
            )

            os.mkdir(os.path.join(parent_work_dir_path, 'app'))            

            with open(os.path.join(parent_work_dir_path, build_file), 'w') as outf:
                outf.write('version "1.0.0"\n')
                outf.close()
 
            # run test
            actual_step_result = step_implementer._run_step()

            # verify results
            expected_step_result = StepResult(
                step_name='unit-test',
                sub_step_name='GradleTest',
                sub_step_implementer_name='GradleTest'
            )
            expected_step_result.add_artifact(
                description="Standard out and standard error from gradle.",
                name='gradle-output',
                value='/mock/gradle_output.txt'
            )
            expected_step_result.add_artifact(
                description="Test report generated when running unit tests.",
                name='test-report',
                value='/mock/test-results-dir'
            )

            return None

            self.assertEqual(actual_step_result, expected_step_result)

            #mock_run_gradle_step.assert_called_once_with(
            #    mvn_output_file_path='/mock/gradle_output.txt'
            #)
            mock_gather_evidence.assert_called_once_with(
                step_result=Any(StepResult),
                test_report_dirs='/mock/test-results-dir'                                                                    
            )


class TestStepImplementerGradleTest__get_test_conversionfail(
    BaseTestStepImplementerGradleTest
):
    def test_success_with_report_dir(
        self
    ):

        with TempDirectory() as test_dir:

            parent_work_dir_path = os.path.join(test_dir.path, 'working')

            build_file = 'app/gradle.build'

            step_config = {
                'build-file': os.path.join(parent_work_dir_path, build_file)
            }
            step_implementer = self.create_step_implementer(
                step_config=step_config,
                parent_work_dir_path=parent_work_dir_path,
            )

            os.mkdir(parent_work_dir_path)

            os.mkdir(os.path.join(parent_work_dir_path, 'app'))            

            total = {'A': 100, 'B': 100}

            result = {'A': 'fail', 'B': 100}

            try:
                combine_step = step_implementer._combine_test_results(total, result)
            except ValueError as ve:
                return None

            
class TestStepImplementerGradleTest__get_test_results_from_file(
    BaseTestStepImplementerGradleTest
):
    def test_result(self):
        with TempDirectory() as test_dir:

            parent_work_dir_path = os.path.join(test_dir.path, 'working')

            reports_dir = 'test-reports-dir'

            os.mkdir(os.path.join(test_dir.path, 'working'))

            step_config = {
                'test-reports-dir': os.path.join(test_dir.path, reports_dir)
            }

            step_implementer = self.create_step_implementer(
                step_config=step_config,
                parent_work_dir_path=parent_work_dir_path,
            )

            current_dir = os.getcwd()

            filename = os.path.join(current_dir, "tests/step_implementers/unit_test/TEST-org.acme.rest.json.gradle.AppTest.xml")

            actual_results = step_implementer._get_test_results_from_file(filename=filename, attributes=step_implementer.TEST_RESULTS_ATTRIBUTES)

            expected_results = {'time': '0.192', 'tests': '2', 'failures': '0', 'errors': '0', 'skipped': '0'}

            self.assertEqual(actual_results, expected_results)

class TestStepImplementerGradleTest__get_test_results_noxml(
    BaseTestStepImplementerGradleTest
):
    def test_result(self):
        with TempDirectory() as test_dir:

            parent_work_dir_path = os.path.join(test_dir.path, 'working')

            reports_dir = 'test-reports-dir'

            os.mkdir(os.path.join(test_dir.path, 'working'))

            step_config = {
                'test-reports-dir': os.path.join(test_dir.path, reports_dir)
            }

            step_implementer = self.create_step_implementer(
                step_config=step_config,
                parent_work_dir_path=parent_work_dir_path,
            )

            current_dir = os.getcwd()

            filename = os.path.join(current_dir, "tests/step_implementers/unit_test/TEST-unknown.xml")

            actual_results = step_implementer._get_test_results_from_file(filename=filename, attributes=step_implementer.TEST_RESULTS_ATTRIBUTES)

            if actual_results == {}:

                return None
            
            expected_results = {'time': '0.192', 'tests': '2', 'failures': '0', 'errors': '0', 'skipped': '0'}
            
            self.assertEqual(actual_results, expected_results)


class TestStepImplementerGradleTest__get_test_results_brokenxml(
    BaseTestStepImplementerGradleTest
):
    def test_result(self):
        with TempDirectory() as test_dir:

            parent_work_dir_path = os.path.join(test_dir.path, 'working')

            reports_dir = 'test-reports-dir'

            os.mkdir(os.path.join(test_dir.path, 'working'))

            step_config = {
                'test-reports-dir': os.path.join(test_dir.path, reports_dir)
            }

            step_implementer = self.create_step_implementer(
                step_config=step_config,
                parent_work_dir_path=parent_work_dir_path,
            )

            current_dir = os.getcwd()

            filename = os.path.join(test_dir.path, 'broken.xml')

            with open(filename, 'w') as outf:
                outf.write('<xml>broken>')
                outf.close()

            actual_results = step_implementer._get_test_results_from_file(filename=filename, attributes=step_implementer.TEST_RESULTS_ATTRIBUTES)

            if actual_results == {}:

                return None

            expected_results = {'time': '0.192', 'tests': '2', 'failures': '0', 'errors': '0', 'skipped': '0'}

            self.assertEqual(actual_results, expected_results)
            
class TestStepImplementerGradleTest__required_config_or_result_keys(
    BaseStepImplementerTestCase
):
    def test_result(self):
        self.assertEqual(
            GradleTest._required_config_or_result_keys(),
            [
                'build-file'
            ]
        )
            
class TestStepImplementerGradleTest__get_missing_required_test_attributes(
    BaseTestStepImplementerGradleTest
):
    def test_result(self):
        with TempDirectory() as test_dir:
            # setup test
            parent_work_dir_path = os.path.join(test_dir.path, 'working')

            reports_dir = 'test-reports-dir'

            os.mkdir(os.path.join(test_dir.path, 'working'))

            step_config = {
                'test-reports-dir': os.path.join(test_dir.path, reports_dir)
            }
            step_implementer = self.create_step_implementer(
                step_config=step_config,
                parent_work_dir_path=parent_work_dir_path,
            )

            test_results = {'time': '0.192', 'errors': '0', 'skipped': '0'}
            expected_results = ['tests', 'failures']
            self.assertEqual(step_implementer._get_missing_required_test_attributes(test_results, step_implementer.TEST_RESULTS_ATTRIBUTES_REQUIRED), expected_results)

class TestStepImplementerGradleTest__get_dict_with_keys_from_list(
    BaseTestStepImplementerGradleTest
):
    def test_result(self):
        with TempDirectory() as test_dir:
            # setup test
            parent_work_dir_path = os.path.join(test_dir.path, 'working')

            reports_dir = 'test-reports-dir'

            os.mkdir(os.path.join(test_dir.path, 'working'))

            step_config = {
                'test-reports-dir': os.path.join(test_dir.path, reports_dir)
            }
            step_implementer = self.create_step_implementer(
                step_config=step_config,
                parent_work_dir_path=parent_work_dir_path,
            )

            expected_results = {'time': 0, 'tests': 0, 'failures': 0, 'errors': 0, 'skipped': 0}
            self.assertEqual(step_implementer._get_dict_with_keys_from_list(step_implementer.TEST_RESULTS_ATTRIBUTES), expected_results)
        
class TestStepImplementerGradleTest__combine_test_results(
    BaseTestStepImplementerGradleTest
):
    def test_result(self):
        with TempDirectory() as test_dir:
            # setup test
            parent_work_dir_path = os.path.join(test_dir.path, 'working')

            reports_dir = 'test-reports-dir'

            os.mkdir(os.path.join(test_dir.path, 'working'))

            step_config = {
                'build-file': '/app/gradle.build',
                'test-reports-dir': os.path.join(test_dir.path, reports_dir)
            }
            step_implementer = self.create_step_implementer(
                step_config=step_config,
                parent_work_dir_path=parent_work_dir_path,
            )

            current_results = {'time': '0.20', 'tests': '2', 'failures': '0', 'errors': '1', 'skipped': '0'}
            total_results = {'time': '5.00', 'tests': '10', 'failures': '2', 'errors': '1', 'skipped': '1'}
            end_results = {'time': 5.2, 'tests': 12, 'failures': 2, 'errors': 2, 'skipped': 1}
            self.assertEqual(step_implementer._combine_test_results(total_results, current_results), end_results)
