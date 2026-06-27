"""部门管理路由 — /api/departments"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.department import Department
from app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentResponse
from app.middleware.auth_middleware import get_current_user, get_current_admin

router = APIRouter(prefix="/api/departments", tags=["部门管理"])


@router.get("/")
async def list_departments(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取所有部门（所有登录用户均可查看）"""
    result = await db.execute(
        select(Department).order_by(Department.id)
    )
    departments = result.scalars().all()
    return [DepartmentResponse.model_validate(d) for d in departments]


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_department(
    data: DepartmentCreate,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """创建部门（管理员）"""
    result = await db.execute(
        select(Department).where(Department.name == data.name)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status.HTTP_409_CONFLICT, detail="部门名称已存在")

    dept = Department(name=data.name, description=data.description)
    db.add(dept)
    await db.flush()
    await db.refresh(dept)
    return DepartmentResponse.model_validate(dept)


@router.put("/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: int,
    data: DepartmentUpdate,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """修改部门（管理员）"""
    result = await db.execute(
        select(Department).where(Department.id == department_id)
    )
    dept = result.scalar_one_or_none()
    if not dept:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="部门不存在")

    if data.name is not None:
        # 检查重名
        dup = await db.execute(
            select(Department).where(
                Department.name == data.name,
                Department.id != department_id,
            )
        )
        if dup.scalar_one_or_none():
            raise HTTPException(status.HTTP_409_CONFLICT, detail="部门名称已存在")
        dept.name = data.name
    if data.description is not None:
        dept.description = data.description

    await db.flush()
    await db.refresh(dept)
    return dept


@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    department_id: int,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """删除部门（管理员）"""
    result = await db.execute(
        select(Department).where(Department.id == department_id)
    )
    dept = result.scalar_one_or_none()
    if not dept:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="部门不存在")

    await db.delete(dept)
    await db.flush()
