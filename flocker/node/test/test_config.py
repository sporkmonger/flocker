# Copyright Hybrid Logic Ltd.  See LICENSE file for details.

"""
Tests for ``flocker.node._config``.
"""

from twisted.trial.unittest import SynchronousTestCase, SkipTest
from .._config import Configuration
from .._model import Application, DockerImage, Deployment, Node


class ModelFromConfigurationTests(SynchronousTestCase):
    """
    Other tests for ``model_from_configuration``.
    """
    def test_error_on_missing_application_key(self):
        """
        ``model_from_configuration`` raises an ``KeyError`` if the
        application_configuration does not contain an `application` key.
        """
        config = Configuration()
        self.assertRaises(KeyError,
                          config._applications_from_configuration, {})

    def test_error_on_missing_application_attributes(self):
        """
        ``model_from_configuration`` raises an exception if the
        application_configuration does not contain all the attributes of an
        `Application` record.
        """
        config = dict(applications={u'mysql-hybridcluster': {}})
        parser = Configuration()
        exception = self.assertRaises(KeyError,
                                      parser._applications_from_configuration,
                                      config)
        self.assertEqual(
            "Application 'mysql-hybridcluster' has a config error. "
            "Missing value for 'image'.",
            exception.message
        )

    def test_error_on_extra_application_attributes(self):
        """
        ``model_from_configuration`` raises an exception if the
        application_configuration contains unrecognised Application attribute
        names.
        """
        config = dict(applications={
            u'mysql-hybridcluster': dict(image=b'foo/bar:baz', foo=b'bar',
                                         baz=b'quux')})
        parser = Configuration()
        exception = self.assertRaises(KeyError,
                                      parser._applications_from_configuration,
                                      config)
        self.assertEqual(
            "Application 'mysql-hybridcluster' has a config error. "
            "Unrecognised keys: foo, baz.",
            exception.message
        )

    def test_error_invalid_dockerimage_name(self):
        """
        ``model_from_configuration`` raises an exception if the
        application_configuration uses invalid Docker image names.
        """
        invalid_docker_image_name = b':baz'
        config = dict(
            applications={u'mysql-hybridcluster': dict(
                image=invalid_docker_image_name)})
        parser = Configuration()
        exception = self.assertRaises(KeyError,
                                      parser._applications_from_configuration,
                                      config)
        self.assertEqual(
            "Application 'mysql-hybridcluster' has a config error. "
            "Invalid Docker image name. "
            "Docker image names must have format 'repository[:tag]'. "
            "Found ':baz'.",
            exception.message
        )

    def test_error_on_invalid_volume_path(self):
        """
        ``model_from_configuration`` raises an exception if the
        application_configuration uses invalid unix paths for volumes.
        """
        # The implementation can use os.path.isabs to check that an absolute
        # path is used.
        raise SkipTest('Volumes configuration can not be parsed yet.')
        config = dict(
            applications={u'mysql-hybridcluster': dict(
                image=u'repository:tag', volume=u'invalid//path//')})
        parser = Configuration()
        exception = self.assertRaises(KeyError,
                                      parser._applications_from_configuration,
                                      config)
        self.assertEqual(
            "Application 'mysql-hybridcluster' has a config error. "
            "The volume mount path must be an absolute path.",
            exception.message
        )

    def test_dict_of_applications(self):
        """
        ``model_from_configuration`` returns a dict of ``Application``
        instances, one for each application key in the supplied configuration.
        """
        config = dict(
            applications={
                u'mysql-hybridcluster': dict(image=u'flocker/mysql:v1.0.0'),
                u'site-hybridcluster': dict(image=u'flocker/wordpress:v1.0.0')
            }
        )
        parser = Configuration()
        applications = parser._applications_from_configuration(config)
        expected_applications = {
            u'mysql-hybridcluster': Application(
                name=u'mysql-hybridcluster',
                image=DockerImage(repository=u'flocker/mysql', tag=u'v1.0.0')),
            u'site-hybridcluster': Application(
                name=u'site-hybridcluster',
                image=DockerImage(repository=u'flocker/wordpress',
                                  tag=u'v1.0.0'))
        }

        self.assertEqual(expected_applications, applications)


class DeploymentFromConfigurationTests(SynchronousTestCase):
    """
    Tests for ``_deployment_from_configuration``.
    """
    def test_error_on_missing_nodes_key(self):
        """
        ``_deployment_from_config`` raises an ``KeyError`` if the
        deployment_configuration does not contain an `nodes` key.
        """
        config = Configuration()
        self.assertRaises(
            KeyError, config._deployment_from_configuration, {}, set([]))

    def test_error_on_non_list_applications(self):
        """
        ``_deployment_from_config`` raises an ``ValueError`` if the
        deployment_configuration contains application values not in the form of
        a list.
        """
        config = Configuration()
        exception = self.assertRaises(
            ValueError,
            config._deployment_from_configuration,
            dict(nodes={u'node1.example.com': None}),
            set([])
        )
        self.assertEqual(
            u'Node node1.example.com has a config error. '
            u'Wrong value type: NoneType. '
            u'Should be list.',
            exception.message
        )

    def test_error_on_unrecognized_application_name(self):
        """
        ``_deployment_from_config`` raises an ``ValueError`` if the
        deployment_configuration refers to a non-existent application.
        """

    def test_error_on_duplicate_applications(self):
        """
        ``_deployment_from_config`` raises an ``ValueError`` if the
        deployment_configuration contains duplicate applications.
        """

    def test_error_on_invalid_node_hostname(self):
        """
        ``_deployment_from_config`` raises an ``ValueError`` if the
        deployment_configuration contains invalid DNS hostnames.
        """

    def test_set_on_success(self):
        """
        ``_deployment_from_config`` returns a set of Node objects. One for each
        key in the supplied nodes dictionary.
        """
        applications = {
            'mysql-hybridcluster': Application(
                name='mysql-hybridcluster',
                image=Application(
                    name=u'mysql-hybridcluster',
                    image=DockerImage(repository=u'flocker/mysql', tag=u'v1.0.0'))
            )
        }
        config = Configuration()
        result = config._deployment_from_configuration(
            dict(nodes={'node1.example.com': ['mysql-hybridcluster']}), applications)

        expected = Deployment(nodes=set([
            Node(hostname='node1.example.com', applications=set(applications.values()))
        ]))

        self.assertEqual(expected, result)
