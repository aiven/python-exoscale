# -*- coding: utf-8 -*-
__version__ = "0.8.0"

import os
import pathlib
import toml
from attr import field
from .api.compute import ComputeAPI
from .api.dns import DnsAPI
from .api.storage import StorageAPI
from .api.runstatus import RunstatusAPI
from .api.iam import IamAPI

_API_KEY_ENVVAR = "EXOSCALE_API_KEY"
_API_SECRET_ENVVAR = "EXOSCALE_API_SECRET"
_COMPUTE_API_ENDPOINT_ENVVAR = "EXOSCALE_COMPUTE_API_ENDPOINT"
_DNS_API_ENDPOINT_ENVVAR = "EXOSCALE_DNS_API_ENDPOINT"
_RUNSTATUS_API_ENDPOINT_ENVVAR = "EXOSCALE_RUNSTATUS_API_ENDPOINT"
_STORAGE_API_ENDPOINT_ENVVAR = "EXOSCALE_STORAGE_API_ENDPOINT"
_IAM_API_ENDPOINT_ENVVAR = "EXOSCALE_IAM_API_ENDPOINT"
_STORAGE_ZONE_ENVVAR = "EXOSCALE_STORAGE_ZONE"
_CONFIG_FILE_ENVVAR = "EXOSCALE_CONFIG_FILE"
_DEFAULT_CONFIG_FILE = os.path.join(pathlib.Path.home(), "config.toml")


class Exoscale:
    """
    An Exoscale API client.

    Parameters:
        config_file (str): path to a configuration file
        profile (str): a configuration profile name
        api_key (str): an Exoscale client API key
        api_secret (str): an Exoscale client API secret
        compute_api_endpoint (str): an alternative Exoscale Compute API endpoint
        dns_api_endpoint (str): an alternative Exoscale DNS API endpoint
        storage_api_endpoint (str): an alternative Exoscale Object Storage API endpoint
        iam_api_endpoint (str): an alternative Exoscale IAM API endpoint
        storage_zone (str): an Exoscale Storage zone
        runstatus_api_endpoint (str): an alternative Exoscale Runstatus API endpoint
        max_retries (int): the API HTTP session retry policy number of retries to allow
        trace (bool): API requests/responses tracing flag

    Attributes:
        api_key (str): the Exoscale client API key
        api_secret (str): the Exoscale client API secret
        compute (api.compute.ComputeAPI): the Exoscale Compute API client
        dns (api.compute.DnsAPI): the Exoscale DNS API client
        storage (api.storage.StorageAPI): the Exoscale Object Storage API client
        runstatus (api.runstatus.RunstatusAPI): the Exoscale Runstatus API client
        iam (api.iam.IamAPI): the Exoscale IAM API client
    """

    def __init__(
        self,
        config_file=None,
        profile=None,
        api_key=None,
        api_secret=None,
        compute_api_endpoint=None,
        dns_api_endpoint=None,
        storage_api_endpoint=None,
        storage_zone=None,
        runstatus_api_endpoint=None,
        iam_api_endpoint=None,
        max_retries=3,
        trace=False,
    ):
        # Load settings from a configuration file profile
        config_file = (
            config_file
            if config_file
            else os.getenv(_CONFIG_FILE_ENVVAR, None)
        )
        if config_file:
            with open(config_file) as f:
                self._config = toml.load(f)

        if not getattr(self, "_config", None) and os.path.exists(
            _DEFAULT_CONFIG_FILE
        ):
            with open(_DEFAULT_CONFIG_FILE) as f:
                self._config = toml.load(f)

        if getattr(self, "_config", None) is not None:
            profile = self._get_profile(profile)
            for k in {"name", "api_key", "api_secret"}:
                if k not in profile:
                    raise ConfigurationError(
                        'profile missing "{}" key'.format(k)
                    )

            api_key = profile["api_key"] if not api_key else api_key
            api_secret = (
                profile["api_secret"] if not api_secret else api_secret
            )
            compute_api_endpoint = (
                profile.get("compute_api_endpoint", None)
                if not compute_api_endpoint
                else compute_api_endpoint
            )
            dns_api_endpoint = (
                profile.get("dns_api_endpoint", None)
                if not dns_api_endpoint
                else dns_api_endpoint
            )
            storage_api_endpoint = (
                profile.get("storage_api_endpoint", None)
                if not storage_api_endpoint
                else storage_api_endpoint
            )
            storage_zone = (
                profile.get("storage_zone", None)
                if not storage_zone
                else storage_zone
            )
            runstatus_api_endpoint = (
                profile.get("runstatus_api_endpoint", None)
                if not runstatus_api_endpoint
                else runstatus_api_endpoint
            )
            iam_api_endpoint = (
                profile.get("iam_api_endpoint", None)
                if not iam_api_endpoint
                else iam_api_endpoint
            )

        # Fallback: load settings from environment variables
        api_key = api_key if api_key else os.getenv(_API_KEY_ENVVAR, None)
        api_secret = (
            api_secret if api_secret else os.getenv(_API_SECRET_ENVVAR, None)
        )
        compute_api_endpoint = (
            compute_api_endpoint
            if compute_api_endpoint
            else os.getenv(_COMPUTE_API_ENDPOINT_ENVVAR, None)
        )
        dns_api_endpoint = (
            dns_api_endpoint
            if dns_api_endpoint
            else os.getenv(_DNS_API_ENDPOINT_ENVVAR, None)
        )
        storage_api_endpoint = (
            storage_api_endpoint
            if storage_api_endpoint
            else os.getenv(_STORAGE_API_ENDPOINT_ENVVAR, None)
        )
        storage_zone = (
            storage_zone
            if storage_zone
            else os.getenv(_STORAGE_ZONE_ENVVAR, None)
        )
        runstatus_api_endpoint = (
            runstatus_api_endpoint
            if runstatus_api_endpoint
            else os.getenv(_RUNSTATUS_API_ENDPOINT_ENVVAR, None)
        )
        iam_api_endpoint = (
            iam_api_endpoint
            if iam_api_endpoint
            else os.getenv(_IAM_API_ENDPOINT_ENVVAR, None)
        )

        if api_key is None or api_secret is None:
            raise ConfigurationError("missing API key/secret")

        self.api_key = api_key
        self.api_secret = api_secret

        kwargs = {
            "key": self.api_key,
            "secret": self.api_secret,
            "max_retries": max_retries,
            "trace": trace,
        }
        if compute_api_endpoint is not None:
            kwargs["endpoint"] = compute_api_endpoint
        self.compute = ComputeAPI(**kwargs)

        kwargs = {
            "key": self.api_key,
            "secret": self.api_secret,
            "max_retries": max_retries,
            "trace": trace,
        }
        if dns_api_endpoint is not None:
            kwargs["endpoint"] = dns_api_endpoint
        self.dns = DnsAPI(**kwargs)

        kwargs = {
            "key": self.api_key,
            "secret": self.api_secret,
            "max_retries": max_retries,
            "trace": trace,
        }
        if storage_api_endpoint is not None:
            kwargs["endpoint"] = storage_api_endpoint
        if storage_zone is not None:
            kwargs["zone"] = storage_zone
        self.storage = StorageAPI(**kwargs)

        kwargs = {
            "key": self.api_key,
            "secret": self.api_secret,
            "max_retries": max_retries,
            "trace": trace,
        }
        if runstatus_api_endpoint is not None:
            kwargs["endpoint"] = runstatus_api_endpoint
        self.runstatus = RunstatusAPI(**kwargs)

        kwargs = {
            "key": self.api_key,
            "secret": self.api_secret,
            "max_retries": max_retries,
            "trace": trace,
        }
        if iam_api_endpoint is not None:
            kwargs["endpoint"] = iam_api_endpoint
        self.iam = IamAPI(**kwargs)

    def _get_profile(self, profile=None):
        if (
            "profiles" not in self._config
            or len(self._config["profiles"]) == 0
        ):
            raise ConfigurationError("no profiles configured")

        if profile or "default_profile" in self._config:
            if "default_profile" in self._config and not profile:
                profile = self._config["default_profile"]

            for a in self._config["profiles"]:
                if a["name"] == profile:
                    return a

            raise ConfigurationError('profile "{}" not found'.format(profile))

        return self._config["profiles"][0]

    def __repr__(self):
        return "Exoscale(api_key='{}')".format(self.api_key)

    def __str__(self):
        return self.__repr__()


class ConfigurationError(Exception):
    """
    A generic configuration error.
    """

    reason = field()
