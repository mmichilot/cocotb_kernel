import sys
import tomllib
from pathlib import Path

import cocotb_kernel.module as test_module
from cocotb.runner import get_runner # type: ignore


def find_config() -> Path | None:
    cwd = Path().resolve()
    dirs = [cwd, *cwd.parents]
    for dir in dirs:
        config_file = dir / "cocotb.toml"
        if config_file.exists():
            return config_file
    return None

def main() -> None:
    if (config := find_config()) is None:
        raise RuntimeError("Cannot start cocotb kernel: couldn't find cocotb.toml")

    with open(config, 'rb') as f:
        options = tomllib.load(f)
    
    simulator = options['sim']
    runner = get_runner(simulator)

    # Common options
    hdl_toplevel = options['hdl_toplevel']
    hdl_toplevel_lang = options['hdl_toplevel_lang']
    parameters = options.get('parameters', dict())
    
    build_options = options['build']
    runner.build(**build_options, 
                 hdl_toplevel=hdl_toplevel,
                 parameters=parameters)

    test_options = options['test']
    if 'test_args' in options:
        test_args = [*options['test_args'], *sys.argv[1:]]
    else:
        test_args = [*sys.argv[1:]]
    
    runner.test(**test_options, 
                test_module=test_module.__name__, 
                hdl_toplevel=hdl_toplevel,
                hdl_toplevel_lang=hdl_toplevel_lang,
                parameters=parameters,
                test_args=test_args,
                # Workaround for Verilator since its doesn't use test_args in cocotb v1.8.1
                # This has been fixed in cocotb v2.0
                plusargs=test_args if simulator == 'verilator' else test_options.get('plusargs', []))

if __name__ == '__main__':
    main()