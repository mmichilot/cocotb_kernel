import argparse
import json
import sys
import tempfile
from pathlib import Path

from jupyter_client.kernelspec import install_kernel_spec



def install_cocotb_kernelspec(
    user: bool = True,
    prefix: (str | None) = None,
    config_name: (str | None) = None,
    kernel_name: (str | None) = None
) -> str:
    kernel_json = {
        "argv": [sys.executable,
                 "-m", "cocotb_kernel",
                 "--connection-file", "{connection_file}",
                 "--config-name", config_name],
        "display_name": kernel_name,
        "language": "python",
        "metadata": {"debugger": True},
    }
    with tempfile.TemporaryDirectory() as td:
        with open(Path(td, "kernel.json"), "w") as f:
            json.dump(kernel_json, f, sort_keys=True)

        print("Installing cocotb kernelspec")
        return install_kernel_spec(td, kernel_name=kernel_name, user=user, prefix=prefix)


def main() -> None:
    parser = argparse.ArgumentParser(description="Install kernelspec for cocotb kernel")

    prefix_locations = parser.add_mutually_exclusive_group()
    prefix_locations.add_argument(
        "--user", help="Install kernelspec in user's home directory", action="store_true"
    )
    prefix_locations.add_argument(
        "--sys-prefix",
        help="Install kernelspec in sys.prefix. Useful in conda / virtualenv",
        action="store_true",
    )
    prefix_locations.add_argument(
        "--prefix", help="Install kernelspec in this prefix", default=None
    )

    parser.add_argument(
        "--config-name", help="Name of the toml file (default is cocotb)", default="cocotb"
    )

    parser.add_argument(
        "--kernel_name", help="Name of the kernel (default is cocotb)", default="cocotb"
    )

    args = parser.parse_args()

    user = False
    prefix = None
    if args.sys_prefix:
        prefix = sys.prefix
    elif args.prefix:
        prefix = args.prefix
    elif args.user:
        user = True

    destination = install_cocotb_kernelspec(user=user,
                                            prefix=prefix,
                                            config_name=args.config_name,
                                            kernel_name=args.kernel_name)
    print(f"Installed cocotb kernel to {destination}")


if __name__ == "__main__":
    main()
