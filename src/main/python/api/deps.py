"""FastAPI 依赖项：内部服务鉴权等。"""
from __future__ import annotations

import os

from fastapi import Header, HTTPException, status

INTERNAL_TOKEN_ENV = "INTERNAL_API_TOKEN"
DEFAULT_DEV_TOKEN = "dev-internal-token"


def verify_internal_token(
    x_internal_token: str | None = Header(default=None, alias="X-Internal-Token"),
) -> None:
    """校验 X-Internal-Token 请求头。

    通过环境变量 INTERNAL_API_TOKEN 配置；未配置时使用默认开发 token，便于本地联调。
    """
    expected = os.getenv(INTERNAL_TOKEN_ENV, DEFAULT_DEV_TOKEN)
    if x_internal_token != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": 40101, "message": "invalid X-Internal-Token"},
        )
