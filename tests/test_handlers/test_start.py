import pytest
from unittest.mock import AsyncMock


from main import help_command, promise, Promises


@pytest.mark.asyncio
async def test_help_command():
    message = AsyncMock()
    await help_command(message)

    message.answer.assert_called_with("Оставь обещание и я буду о нем напоминать . Используй клавиатуру для выбора")

@pytest.mark.asyncio
async def test_promise():
    message = AsyncMock()
    fsm = AsyncMock('123')
    await Promises.promis_text.set(fsm)
    message.answer.assert_called_with(message)