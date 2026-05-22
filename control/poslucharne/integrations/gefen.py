import asyncio

from poslucharne.devices import Matrix, PowerState


class GefenMatrix(Matrix):
    async def _send_command(self, payload: str) -> None:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(
                self.config.get("address"), self.config.get("port", 23)
            ),
            timeout=5,
        )

        try:
            writer.write(payload.encode() + b"\r\n")
            await asyncio.wait_for(writer.drain(), timeout=5)
        finally:
            writer.close()
            await writer.wait_closed()

    async def get_power(self) -> PowerState:
        # gefen does not have any command to retrieve power
        return PowerState.UNKNOWN

    async def power_on(self) -> None:
        await self._send_command("#power 1")

    async def power_off(self) -> None:
        await self._send_command("#power 0")

    async def reboot(self) -> None:
        await self._send_command("#reboot")

    async def connect(self, input: str, output: str) -> None:
        input_i = int(input)
        output_i = int(output)

        if input_i <= 0 or input > self.config.get("inputs", 0):
            raise ValueError(f"input {input_i} not available")
        if output_i <= 0 or output > self.config.get("outputs", 0):
            raise ValueError(f"output {output_i} not available")

        await self._send_command(f"r {input_i} {output_i}")
