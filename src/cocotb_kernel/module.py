# TODO: Create type stubs for CocotbKernelApp
import os
from typing import Any, Coroutine

import cocotb
from cocotb.handle import SimHandleBase
from cocotb.task import bridge, resume
from ipykernel.kernelapp import IPKernelApp
from IPython.core.interactiveshell import ExecutionResult
from zmq import Context


class CocotbKernelApp(IPKernelApp):
    # Patch init_signal because the kernel is ran in a separate thread
    def init_signal(self) -> None:
        pass

    # Disable shell channel thread to disable subshells
    def init_control(self, context: Context) -> None:
        super().init_control(context)
        self.shell_channel_thread = None


# Execute code cells in cocotb's event loop
def cocotb_loop_runner(coro: Coroutine[Any, Any, ExecutionResult]) -> ExecutionResult:
    async def _coro_wrapper() -> ExecutionResult:
        return await coro

    coro_wrapper = resume(_coro_wrapper)
    return coro_wrapper()


@cocotb.test()
async def kernel_entry(dut: SimHandleBase) -> None:
    connection_file = os.environ["COCOTB_CONNECTION_FILE"]

    app = CocotbKernelApp.instance(user_ns=dict(dut=dut))

    # Run ipykernel in a separate thread
    def _start_kernel() -> None:
        app.initialize(["-f", connection_file])
        app.shell.loop_runner = cocotb_loop_runner  # type: ignore
        app.start()

    start_kernel = bridge(_start_kernel)

    cocotb.log.info("starting ipykernel")
    await start_kernel()
