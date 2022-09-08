import pytest
from unittest.mock import AsyncMock

import buttons
from main import process_start_command


@pytest.mark.asyncio
async def test_start_handler():
    message = AsyncMock()
    await process_start_command(message)

    message.answer.assert_called_with(reply_markup=buttons.check_promise_button)
