# cocotb Jupyter Kernel
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/mmichilot/cocotb_kernel/HEAD?labpath=example%2FQuickstart+Guide.ipynb)

This kernel adds support for using [cocotb](https://docs.cocotb.org/en/stable/) within 
Jupyter notebooks. 

## Why is a dedicated kernel needed?
cocotb works in conjunction with an HDL simulator. As such, attempting to `import cocotb`
within a notebook will not work because no simulator is attached. This kernel works by first building the HDL design and launching the simulator using cocotb's [runners](https://docs.cocotb.org/en/stable/library_reference.html#cocotb.runner.Simulator), then
having a cocotb test module launch ipykernel, which will connect to the notebook and execute code cells.

## Installation
Prerequisites:
- Python 3.10+
- JupyterLab 4+ or Jupyter Notebook 6+
- An HDL simulator (such as Icarus Verilog, Verilator, or GHDL)

After installing the prerequisites, the kernel can be installed via pip.
```bash
pip install cocotb_kernel
```

## Usage
Before launching the kernel, create a TOML file named `cocotb.toml` within the project's root directory (similar to cocotb's Makefile).

The TOML file follows the cocotb [runner](https://docs.cocotb.org/en/stable/library_reference.html#cocotb.runner.Simulator) 
`build()` and `test()` arguments, with a few exceptions, as shown:

```toml
# The simulator to build and simulate the HDL design
# https://docs.cocotb.org/en/stable/simulator_support.html
simulator = "icarus"

# The top level HDL module
hdl_toplevel = "foo"

# The language of the top level HDL module
hdl_toplevel_lang = "verilog"

# Optional: Verilog parameters or VHDL generics
[parameters]

# Build options
# https://docs.cocotb.org/en/stable/library_reference.html#cocotb.runner.Simulator.build
[build]
verilog_sources = ["hdl/foo.sv", "../hdl/foo.sv"] # specify sources relative to cocotb.toml
vhdl_sources = ["hdl/*.vhdl", "**/*.vhdl"]        # wildcards are also supported

# Optional: Defines to set for building
[build.defines]

# Optional: Test options
# https://docs.cocotb.org/en/stable/library_reference.html#cocotb.runner.Simulator.test
[test]

# Optional: Extra environment variables to set for testing
[test.extra_env]
```

Once the TOML file is created, navigate to or launch JupyterLab within the project's
root directory and create or open a notebook with the cocotb kernel.

## Planned Features
- Move wavedrom support into kernel (cocotb v2.0 removes the wavedrom module)
