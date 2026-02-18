from ..pomgen import Build
from ..pomgen import Dependency
from ..pomgen import DependencyManagement
from ..pomgen import Plugin
from ..pomgen import PluginManagement
from ..pomgen import Project
from ..pomgen import render_project_xml


##


PROJECT = Project(
    'com.wrmsr',
    'javastuff',
    '1.0-SNAPSHOT',

    'javastuff',

    properties={
        'project.build.sourceEncoding': 'UTF-8',
        'maven.compiler.release': 17,
    },

    dependency_management=DependencyManagement(
        dependencies=[
            Dependency('org.junit', 'junit-bom', '5.11.0', type='pom', scope='import'),
        ],
    ),

    dependencies=[
        Dependency('com.google.inject', 'guice', '7.0.0'),

        Dependency('io.netty', 'netty-all', '4.2.9.Final'),

        Dependency('org.apache.lucene', 'lucene-core', '10.3.2'),

        Dependency('org.junit.jupiter', 'junit-jupiter-engine', '5.11.0', scope='test'),

    ],

    build=Build(
        plugin_management=PluginManagement(
            plugins=[
                Plugin(None, 'maven-clean-plugin', '3.4.0'),

                Plugin(None, 'maven-resources-plugin', '3.3.1'),
                Plugin(None, 'maven-compiler-plugin', '3.13.0'),
                Plugin(None, 'maven-surefire-plugin', '3.3.0'),
                Plugin(None, 'maven-jar-plugin', '3.4.2'),
                Plugin(None, 'maven-install-plugin', '3.1.2'),
                Plugin(None, 'maven-deploy-plugin', '3.1.2'),

                Plugin(None, 'maven-site-plugin', '3.12.1'),
                Plugin(None, 'maven-info-reports-plugin', '3.6.1'),
            ],
        ),
    ),
)


def test_render():
    pom_xml = render_project_xml(PROJECT)
    print(pom_xml)
