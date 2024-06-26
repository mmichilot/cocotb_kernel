import tomllib
import argparse
from pathlib import Path
from typing import Any

import cocotb_kernel.module as test_module
from cocotb.runner import get_runner # type: ignore

# TODO: Add support for custom configuration file name
def find_config() -> Path | None:
    cwd = Path().resolve()
    dirs = [cwd, *cwd.parents]
    for dir in dirs:
        config_file = dir / "cocotb.toml"
        if config_file.exists():
            return config_file
    return None

def resolve_sources(sources: list[str]) -> list[Path]:
    resolved_sources: list[Path] = []
    for source in sources:
        paths = Path('.').glob(source)
        resolved_sources.append(*[path.resolve() for path in paths])
    
    return resolved_sources

def main() -> None:
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--connection-file', type=str)
    parser.add_argument('--config-name', type=str) # TODO: Add support for custom config name
    args = parser.parse_args()

    # Load config
    if (config := find_config()) is None:
        raise RuntimeError("Cannot start cocotb kernel: couldn't find cocotb.toml")
    with open(config, 'rb') as f:
        options = tomllib.load(f)
    
    # Get simulator runner
    simulator = options['sim']
    runner = get_runner(simulator)

    # Common options
    hdl_toplevel = options['hdl_toplevel']
    hdl_toplevel_lang = options['hdl_toplevel_lang']
    parameters = options.get('parameters', dict())
    
    # Build
    build_options: dict[str, Any] = options['build']
    verilog_sources = resolve_sources(build_options.pop('verilog_sources', []))
    vhdl_sources = resolve_sources(build_options.pop('vhdl_sources', []))
    runner.build(**build_options,
                 verilog_sources=verilog_sources,
                 vhdl_sources=vhdl_sources,
                 hdl_toplevel=hdl_toplevel,
                 parameters=parameters)

    # Test
    test_options: dict[str, Any] = options['test']
    test_args = [*test_options.pop('test_args', []), '-f', args.connection_file]
    runner.test(**test_options, 
                test_module=test_module.__name__, 
                hdl_toplevel=hdl_toplevel,
                hdl_toplevel_lang=hdl_toplevel_lang,
                parameters=parameters,
                test_args=test_args,
                # TODO: Remove workaround for cocotb v2.0
                # Workaround for Verilator since its doesn't use test_args in cocotb v1.8.1
                plusargs=test_args if simulator == 'verilator' else test_options.pop('plusargs', []))

if __name__ == '__main__':
    main()