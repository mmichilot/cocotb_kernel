import argparse
from pathlib import Path
from typing import Any

import tomllib
from cocotb_tools.runner import get_runner

import cocotb_kernel.module as test_module


def find_config(config_name:(str | None) = None) -> Path | None:
    cwd = Path().resolve()
    dirs = [cwd, *cwd.parents]
    for dir in dirs:
        config_file = dir / f"{config_name}.toml"
        if config_file.exists():
            return config_file
    return None


def resolve_sources(sources: list[str]) -> list[Path]:
    resolved_sources: list[Path] = []
    for source in sources:
        paths = Path(".").glob(source)
        resolved_sources.append(*[path.resolve() for path in paths])

    return resolved_sources


def main() -> None:
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--connection-file", type=str)
    parser.add_argument("--config-name", type=str)
    args = parser.parse_args()

    # Load config
    if (config := find_config(config_name=args.config_name)) is None:
        raise RuntimeError(f"Cannot start cocotb kernel: couldn't find {args.config_name}.toml")
    with open(config, "rb") as f:
        options = tomllib.load(f)

    # Get simulator runner
    simulator = options["sim"]
    runner = get_runner(simulator)

    # Common options
    hdl_toplevel = options["hdl_toplevel"]
    hdl_toplevel_lang = options["hdl_toplevel_lang"]
    parameters = options.get("parameters", dict())

    # Build
    build_options: dict[str, Any] = options["build"]
    sources = resolve_sources(build_options.pop("sources", []))
    try:
        runner.build(
            **build_options,
            sources=sources,
            hdl_toplevel=hdl_toplevel,
            parameters=parameters,
        )
    except Exception as ex:
        raise RuntimeError(f"An error occurred while building the design: {ex}")

    # Test
    test_options: dict[str, Any] = options.get("test", {})
    extra_env: dict[str, str] = test_options.pop("extra_env", {})
    extra_env["COCOTB_CONNECTION_FILE"] = args.connection_file
    try:
        runner.test(
            **test_options,
            test_module=test_module.__name__,
            hdl_toplevel=hdl_toplevel,
            hdl_toplevel_lang=hdl_toplevel_lang,
            parameters=parameters,
            extra_env=extra_env,
        )
    except Exception as ex:
        raise RuntimeError(f"An error occurred while launching the simulator: {ex}")


if __name__ == "__main__":
    main()
