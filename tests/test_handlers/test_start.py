import pytest
from unittest.mock import AsyncMock
from main import process_start_command


@pytest.mark.asyncio
async def test_start_handler():
    message = AsyncMock()
    await process_start_command()

    message.answer.assert_called_with()
