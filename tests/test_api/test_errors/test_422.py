import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from starlette.status import HTTP_404_NOT_FOUND, HTTP_422_UNPROCESSABLE_ENTITY


class TestRoutes:
    @pytest.mark.asyncio
    async def test_routes_exist(self,
            app: FastAPI, client: AsyncClient) -> None:
        res = await client.post("/wrong_path/asd", json={})
        assert res.status_code == HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_invalid_input_raises_error(self,
            app: FastAPI, client: AsyncClient) -> None:
        res = await client.post("/api/dataset", json={})
        assert res.status_code == HTTP_422_UNPROCESSABLE_ENTITY
