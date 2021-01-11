# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright (C) 2019 Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from testtools.matchers import Equals

from snapcraft.internal.meta import errors
from snapcraft.internal.meta.package_repository import (
    PackageRepository,
    PackageRepositoryApt,
    PackageRepositoryAptPpa,
)
from tests import unit


class PpaTests(unit.TestCase):
    def test_valid_apt_ppa(self):
        repo = PackageRepositoryAptPpa(ppa="test/ppa")

        self.assertThat(repo.marshal(), Equals({"type": "apt", "ppa": "test/ppa"}))

    def test_invalid_apt_ppa_type(self):
        test_dict = {"type": "aptx", "ppa": "test/ppa"}

        error = self.assertRaises(
            errors.PackageRepositoryValidationError,
            PackageRepositoryAptPpa.unmarshal,
            test_dict,
        )

        assert error.brief == "Unsupported type 'aptx'."
        assert error.resolution == "You can use type 'apt'."

    def test_invalid_apt_ppa(self):
        test_dict = {"type": "apt", "ppa": ""}

        error = self.assertRaises(
            errors.PackageRepositoryValidationError,
            PackageRepositoryAptPpa.unmarshal,
            test_dict,
        )

        assert error.brief == "Invalid PPA ''."
        assert error.resolution == "You can update 'ppa' to a non-empty string."

    def test_invalid_apt_ppa_extras(self):
        test_dict = {"type": "apt", "ppa": "test/ppa", "test": "foo"}

        error = self.assertRaises(
            errors.PackageRepositoryValidationError,
            PackageRepositoryAptPpa.unmarshal,
            test_dict,
        )

        assert error.brief == "Invalid keys present ('test')."


class DebTests(unit.TestCase):
    def test_valid_apt_deb(self):
        repo = PackageRepositoryApt(
            architectures=["amd64", "i386"],
            components=["main", "multiverse"],
            formats=["deb", "deb-src"],
            key_id="test-key-id",
            key_server="keyserver.ubuntu.com",
            name="test-name",
            suites=["xenial", "xenial-updates"],
            url="http://archive.ubuntu.com/ubuntu",
        )

        self.assertThat(
            repo.marshal(),
            Equals(
                {
                    "architectures": ["amd64", "i386"],
                    "components": ["main", "multiverse"],
                    "formats": ["deb", "deb-src"],
                    "key-id": "test-key-id",
                    "key-server": "keyserver.ubuntu.com",
                    "name": "test-name",
                    "suites": ["xenial", "xenial-updates"],
                    "type": "apt",
                    "url": "http://archive.ubuntu.com/ubuntu",
                }
            ),
        )

    def test_valid_default_name(self):
        repo = PackageRepositoryApt(
            architectures=["amd64", "i386"],
            components=["main", "multiverse"],
            formats=["deb", "deb-src"],
            key_id="test-key-id",
            key_server="keyserver.ubuntu.com",
            suites=["xenial", "xenial-updates"],
            url="http://archive.ubuntu.com/ubuntu",
        )

        self.assertThat(
            repo.marshal(),
            Equals(
                {
                    "architectures": ["amd64", "i386"],
                    "components": ["main", "multiverse"],
                    "formats": ["deb", "deb-src"],
                    "key-id": "test-key-id",
                    "key-server": "keyserver.ubuntu.com",
                    "name": "http_archive_ubuntu_com_ubuntu",
                    "suites": ["xenial", "xenial-updates"],
                    "type": "apt",
                    "url": "http://archive.ubuntu.com/ubuntu",
                }
            ),
        )

    def test_invalid_type(self):
        test_dict = {
            "architectures": ["amd64", "i386"],
            "components": ["main", "multiverse"],
            "formats": ["deb", "deb-src"],
            "key-id": "test-key-id",
            "key-server": "keyserver.ubuntu.com",
            "name": "test-name",
            "suites": ["xenial", "xenial-updates"],
            "type": "aptx",
            "url": "http://archive.ubuntu.com/ubuntu",
        }

        error = self.assertRaises(
            errors.PackageRepositoryValidationError,
            PackageRepositoryApt.unmarshal,
            test_dict,
        )

        assert error.brief == "Unsupported type 'aptx'."
        assert error.resolution == "You can use type 'apt'."

    def test_invalid_url(self):
        test_dict = {
            "architectures": ["amd64", "i386"],
            "components": ["main", "multiverse"],
            "formats": ["deb", "deb-src"],
            "key-id": "test-key-id",
            "key-server": "keyserver.ubuntu.com",
            "name": "test-name",
            "suites": ["xenial", "xenial-updates"],
            "type": "apt",
            "url": "",
        }

        error = self.assertRaises(
            errors.PackageRepositoryValidationError,
            PackageRepositoryApt.unmarshal,
            test_dict,
        )

        assert error.brief == "Invalid URL ''."
        assert error.resolution == "You can update 'url' to a non-empty string."

    def test_invalid_apt_extra_key(self):
        test_dict = {
            "architectures": ["amd64", "i386"],
            "components": ["main", "multiverse"],
            "formats": ["deb", "deb-src"],
            "key-id": "test-key-id",
            "key-server": "keyserver.ubuntu.com",
            "name": "test-name",
            "suites": ["xenial", "xenial-updates"],
            "type": "apt",
            "url": "http://archive.ubuntu.com/ubuntu",
            "foo": "bar",
            "foo2": "bar",
        }

        error = self.assertRaises(
            errors.PackageRepositoryValidationError,
            PackageRepositoryApt.unmarshal,
            test_dict,
        )

        assert error.brief == "Invalid keys present ('foo', 'foo2')."


class RepoTests(unit.TestCase):
    def test_marshal_none(self):
        self.assertThat(
            PackageRepository.unmarshal_package_repositories(None), Equals(list())
        )

    def test_marshal_empty(self):
        self.assertThat(
            PackageRepository.unmarshal_package_repositories(list()), Equals(list())
        )

    def test_marshal_ppa(self):
        test_dict = {"type": "apt", "ppa": "test/foo"}
        test_list = [test_dict]

        unmarshalled_list = [
            repo.marshal()
            for repo in PackageRepository.unmarshal_package_repositories(test_list)
        ]

        self.assertThat(unmarshalled_list, Equals(test_list))

    def test_marshal_deb(self):
        test_dict = {
            "architectures": ["amd64", "i386"],
            "components": ["main", "multiverse"],
            "formats": ["deb", "deb-src"],
            "key-id": "test-key-id",
            "key-server": "keyserver.ubuntu.com",
            "name": "test-name",
            "suites": ["xenial", "xenial-updates"],
            "type": "apt",
            "url": "http://archive.ubuntu.com/ubuntu",
        }

        test_list = [test_dict]

        unmarshalled_list = [
            repo.marshal()
            for repo in PackageRepository.unmarshal_package_repositories(test_list)
        ]

        self.assertThat(unmarshalled_list, Equals(test_list))

    def test_marshal_all(self):
        test_ppa = {"type": "apt", "ppa": "test/foo"}

        test_deb = {
            "architectures": ["amd64", "i386"],
            "components": ["main", "multiverse"],
            "formats": ["deb", "deb-src"],
            "key-id": "test-key-id",
            "key-server": "keyserver.ubuntu.com",
            "name": "test-name",
            "suites": ["xenial", "xenial-updates"],
            "type": "apt",
            "url": "http://archive.ubuntu.com/ubuntu",
        }

        test_list = [test_ppa, test_deb]

        unmarshalled_list = [
            repo.marshal()
            for repo in PackageRepository.unmarshal_package_repositories(test_list)
        ]

        self.assertThat(unmarshalled_list, Equals(test_list))