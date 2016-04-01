#
#  -*- coding: utf-8 -*-
#
# (C) Copyright 2016 Karellen, Inc. (http://karellen.co/)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from pybuilder.core import use_plugin, init, Project, Author

use_plugin("pypi:karellen_pyb_plugin", ">=0.0.1.dev")

name = "karellen-testing"
default_task = ["analyze", "publish"]
version = "0.0.1.dev"

url = "https://github.com/karellen/karellen-testing"
description = "Please visit %s for more information!" % url
summary = "Karellen Testing Library"

authors = [Author("Karellen, Inc", "supervisor@karellen.co")]
default_task = ["analyze", "publish"]
license = "Apache License, Version 2.0"


@init
def set_properties(project: Project):
    # Cram Configuration
    project.set_property("cram_fail_if_no_tests", False)

    # Integration Tests Coverage is disabled since there are no integration tests
    project.set_property("integrationtest_coverage_threshold_warn", 0)
    project.set_property("integrationtest_coverage_branch_threshold_warn", 0)
    project.set_property("integrationtest_coverage_branch_partial_threshold_warn", 0)

    project.set_property("distutils_classifiers", [
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Testing'])
