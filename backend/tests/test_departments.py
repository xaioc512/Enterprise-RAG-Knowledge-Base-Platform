"""部门管理 API 测试"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.department import Department
from tests.conftest import create_test_user, auth_headers


@pytest.fixture
async def admin_user(db_session: AsyncSession):
    """创建管理员用户"""
    return await create_test_user(db_session, "admin", "admin123", role="admin")


@pytest.fixture
async def normal_user(db_session: AsyncSession):
    """创建普通用户"""
    return await create_test_user(db_session, "normal", "user123", role="user")


@pytest.mark.asyncio
async def test_list_departments_empty(client: AsyncClient, admin_user):
    """部门列表 — 初始为空"""
    response = await client.get(
        "/api/departments/", headers=auth_headers(admin_user)
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_create_department_as_admin(client: AsyncClient, admin_user):
    """管理员创建部门"""
    response = await client.post(
        "/api/departments/",
        json={"name": "技术部", "description": "研发团队"},
        headers=auth_headers(admin_user),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "技术部"
    assert data["id"] is not None


@pytest.mark.asyncio
async def test_create_department_duplicate_name(
    client: AsyncClient, admin_user
):
    """重复名称创建部门应失败"""
    await client.post(
        "/api/departments/",
        json={"name": "技术部", "description": "研发"},
        headers=auth_headers(admin_user),
    )
    response = await client.post(
        "/api/departments/",
        json={"name": "技术部", "description": "重复"},
        headers=auth_headers(admin_user),
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_create_department_as_normal_user(
    client: AsyncClient, normal_user
):
    """普通用户不能创建部门"""
    response = await client.post(
        "/api/departments/",
        json={"name": "黑客部"},
        headers=auth_headers(normal_user),
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_department_as_admin(
    client: AsyncClient, admin_user
):
    """管理员删除部门"""
    # 先创建
    create_resp = await client.post(
        "/api/departments/",
        json={"name": "临时部门"},
        headers=auth_headers(admin_user),
    )
    dept_id = create_resp.json()["id"]

    # 再删除
    response = await client.delete(
        f"/api/departments/{dept_id}",
        headers=auth_headers(admin_user),
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_department_not_found(client: AsyncClient, admin_user):
    """删除不存在的部门"""
    response = await client.delete(
        "/api/departments/99999",
        headers=auth_headers(admin_user),
    )
    assert response.status_code == 404
