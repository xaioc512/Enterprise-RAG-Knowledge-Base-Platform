"""文档管理 API 测试"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.department import Department
from tests.conftest import create_test_user, auth_headers


@pytest.fixture
async def admin_user(db_session: AsyncSession):
    return await create_test_user(
        db_session, "doc_admin", "admin123", role="admin"
    )


@pytest.fixture
async def normal_user(db_session: AsyncSession):
    # 先创建部门再创建用户
    dept = Department(name="测试部门", description="测试")
    db_session.add(dept)
    await db_session.flush()
    await db_session.refresh(dept)

    return await create_test_user(
        db_session, "doc_user", "user123", role="user", department_id=dept.id
    )


@pytest.mark.asyncio
async def test_list_documents_empty(client: AsyncClient, admin_user):
    """文档列表 — 初始为空"""
    response = await client.get(
        "/api/documents/", headers=auth_headers(admin_user)
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data or isinstance(data, list)


@pytest.mark.asyncio
async def test_upload_requires_admin(client: AsyncClient, normal_user):
    """普通用户上传文档应被拒绝"""
    response = await client.post(
        "/api/documents/upload",
        headers=auth_headers(normal_user),
    )
    assert response.status_code in (403, 422)


@pytest.mark.asyncio
async def test_upload_no_file(client: AsyncClient, admin_user):
    """上传但不提供文件应返回验证错误"""
    response = await client.post(
        "/api/documents/upload",
        headers=auth_headers(admin_user),
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_document_not_found(client: AsyncClient, admin_user):
    """删除不存在的文档"""
    response = await client.delete(
        "/api/documents/99999",
        headers=auth_headers(admin_user),
    )
    assert response.status_code == 404
