"""A tiny local imitation of `databricks bundle validate -t <target>` for practice.

It resolves variables the same way the real CLI does (highest wins):
  1. --var "name=value" on the command line      (here: cli_vars={...})
  2. environment variable BUNDLE_VAR_<name>         (here: env={...} or os.environ)
  3. targets.<target>.variables.<name>              (target override)
  4. variables.<name>.default
and merges targets.<target>.resources over the top-level resources.
It only checks the parts the exam asks about — it does not deploy anything.
"""
import copy
import os
import re

import yaml


class BundleError(Exception):
    pass


def _merge(a, b):
    out = copy.deepcopy(a)
    for k, v in (b or {}).items():
        out[k] = _merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else copy.deepcopy(v)
    return out


def validate(path, target=None, env=None, cli_vars=None, quiet=False):
    try:
        cfg = yaml.safe_load(open(path)) or {}
    except yaml.YAMLError as e:
        raise BundleError(f"YAML syntax error: {e}")
    if "bundle" not in cfg or "name" not in (cfg["bundle"] or {}):
        raise BundleError("missing `bundle: name:`")
    targets = cfg.get("targets") or {}
    if not targets:
        raise BundleError("no `targets:` defined (e.g. dev, prod)")
    if target is None:
        target = next((t for t, v in targets.items() if (v or {}).get("default")), None)
        if target is None:
            raise BundleError("no target given and no target has `default: true`")
    if target not in targets:
        raise BundleError(f"target '{target}' not found. Targets: {list(targets)}")
    t = targets[target] or {}
    env = dict(os.environ if env is None else env)
    values, source = {}, {}
    for name, spec in (cfg.get("variables") or {}).items():
        spec = spec or {}
        for src, val in (("--var", (cli_vars or {}).get(name)),
                         ("BUNDLE_VAR_" + name, env.get("BUNDLE_VAR_" + name)),
                         (f"targets.{target}.variables", (t.get("variables") or {}).get(name)),
                         ("default", spec.get("default"))):
            if val is not None:
                values[name], source[name] = val, src
                break
        else:
            raise BundleError(f"variable '{name}' has no value for target '{target}' "
                              f"(no default, no target override, no BUNDLE_VAR_{name})")
    resources = _merge(cfg.get("resources") or {}, t.get("resources"))
    text = yaml.safe_dump(resources, sort_keys=False)

    def repl(m):
        ref = m.group(1)
        if ref.startswith("var."):
            k = ref[4:]
            if k not in values:
                raise BundleError(f"reference ${{{ref}}} — variable '{k}' is not defined")
            return str(values[k])
        if ref == "bundle.target":
            return target
        if ref == "bundle.name":
            return cfg["bundle"]["name"]
        return m.group(0)  # leave other references (e.g. resources.*.id) as they are

    resolved = yaml.safe_load(re.sub(r"\$\{([^}]+)\}", repl, text)) or {}
    result = {"target": target, "mode": t.get("mode"), "variables": values, "sources": source, "resources": resolved}
    if not quiet:
        print(f"Validated bundle '{cfg['bundle']['name']}' for target '{target}' (mode: {t.get('mode')})")
        for k in values:
            shown = "******" if "pass" in k or "secret" in k or "token" in k else values[k]
            print(f"  var.{k:<14} = {shown!s:<22} ← from {source[k]}")
        for kind, items in resolved.items():
            for name, body in (items or {}).items():
                print(f"  {kind[:-1]:<9} {name}: name = {body.get('name')!r}")
    return result
