"""Server-owned model selection; no client endpoint, credential or fallback routing."""

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from .providers import HttpProvider, Profile, Provider


@dataclass(frozen=True)
class ProviderRoute:
    profile: Profile | None = None
    key: str = field(default="", repr=False)
    transport: object = field(default=None, repr=False, compare=False)

    @property
    def audit_name(self):
        if self.profile is None:
            return "offline-scripted-v1"
        return self.profile.name + "@" + self.profile.fingerprint

    @property
    def live_ready(self):
        return self.profile is not None and self.profile.live_ready

    @property
    def notice(self):
        return (
            "Scripted fixture, not a live language model."
            if self.profile is None
            else "Provider-generated draft; factual and business review required."
        )

    def build(self, evidence, refs, stage) -> Provider:
        if self.profile is None:
            from .runtime import fixture

            return fixture(evidence, refs, stage)
        return HttpProvider(self.profile, self.key, self.transport)


def load_route(path=None, *, environ=None, transport=None):
    """Load one deployment profile. Qualification is still enforced before transport.

    A config file is a trusted deployment input, never an HTTP parameter. Live
    approval is not inferred from protocol support or the presence of a key.
    """
    if not path:
        return ProviderRoute()
    env = os.environ if environ is None else environ
    try:
        raw = Path(path).read_bytes()
        if len(raw) > 32768:
            raise ValueError()
        config = json.loads(raw)
        if set(config) != {"selected", "profiles"} or not isinstance(config["profiles"], dict):
            raise ValueError()
        selected = config["selected"]
        if not isinstance(selected, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,63}", selected):
            raise ValueError()
        if selected == "offline-scripted-v1":
            return ProviderRoute()
        entry = dict(config["profiles"][selected])
        key_env = entry.pop("credential_env")
        if not isinstance(key_env, str) or not re.fullmatch(r"[A-Z][A-Z0-9_]{0,99}", key_env):
            raise ValueError()
        expected = {
            "protocol",
            "model",
            "endpoint",
            "allowed_endpoints",
            "internal_only",
            "internal_endpoints",
            "live_enabled",
            "qualified",
            "qualified_fingerprint",
        }
        if set(entry) != expected:
            raise ValueError()
        qualified_fingerprint = entry["qualified_fingerprint"]
        if qualified_fingerprint is not None and not (
            isinstance(qualified_fingerprint, str)
            and re.fullmatch(r"[0-9a-f]{12}", qualified_fingerprint)
        ):
            raise ValueError()
        for name in ("protocol", "model", "endpoint"):
            if not isinstance(entry[name], str) or not entry[name] or len(entry[name]) > 2048:
                raise ValueError()
        for name in ("internal_only", "live_enabled", "qualified"):
            if type(entry[name]) is not bool:
                raise ValueError()
        for name in ("allowed_endpoints", "internal_endpoints"):
            values = entry[name]
            if (
                not isinstance(values, list)
                or len(values) > 16
                or any(not isinstance(v, str) or len(v) > 2048 for v in values)
            ):
                raise ValueError()
            entry[name] = tuple(values)
        return ProviderRoute(
            Profile(name=selected, credential_ref=key_env, **entry), env.get(key_env, ""), transport
        )
    except (OSError, ValueError, TypeError, KeyError):
        # Do not expose config contents, endpoints, secrets or filesystem paths.
        raise ValueError("Invalid server provider configuration") from None


def main():
    """Print the route fingerprint a qualification report must cite. No network call."""
    import argparse

    parser = argparse.ArgumentParser(description="Show the server-selected model route")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    route = load_route(args.config, environ={})
    print(
        json.dumps(
            {
                "route": route.audit_name,
                "fingerprint": route.profile.fingerprint if route.profile else None,
                "live_ready": route.live_ready,
            }
        )
    )


if __name__ == "__main__":
    main()
