# TODO: Create type stubs for CocotbKernelApp
import os
import signal
from types import FrameType
from typing import Any, Coroutine

import cocotb
from cocotb.handle import SimHandleBase
from cocotb.task import bridge, resume
from ipykernel.kernelapp import IPKernelApp
from IPython.core.interactiveshell import ExecutionResult


class CocotbKernelApp(IPKernelApp):
    # Patch init_signal because the kernel is ran in a separate thread
    def init_signal(self) -> None:
        pass

    # Disable shell channel thread to disable subshells
    def init_control(self, context):
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

    def interrupt_kernel(_signal: int, _frame: FrameType | None) -> None:
        # ipykernel<=6 uses a dedicated interrupt handler, however in this context the
        # kernel is ran within a thread, preventing signals from being passed to the kernel.
        #
        # TODO: ipykernel interrupts have been changed to use a queue in a recent pull request
        # https://github.com/ipython/ipykernel/pull/1079
        # Update this to call sigint_handler() on the next major update to ipykernel
        raise NotImplementedError("cocotb_kernel doesn't support interrupting execution")

    signal.signal(signal.SIGINT, interrupt_kernel)

    # Run ipykernel in a separate thread
    def _start_kernel() -> None:
        app.initialize(["-f", connection_file])
        app.shell.loop_runner = cocotb_loop_runner  # type: ignore
        app.start()
    start_kernel = bridge(_start_kernel)

    cocotb.log.info("starting ipykernel")
    await start_kernel()
