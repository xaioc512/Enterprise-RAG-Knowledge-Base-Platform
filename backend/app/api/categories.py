"""知识分类管理路由 — /api/categories"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.category import Category
from app.models.user import User
from app.middleware.auth_middleware import get_current_user, get_current_admin

router = APIRouter(prefix="/api/categories", tags=["知识分类"])


@router.get("/")
async def list_categories(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取所有知识分类"""
    result = await db.execute(
        select(Category).order_by(Category.sort_order)
    )
    categories = result.scalars().all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "sort_order": c.sort_order,
        }
        for c in categories
    ]


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_category(
    name: str,
    description: str = "",
    sort_order: int = 0,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """创建知识分类（管理员）"""
    # 检查重名
    result = await db.execute(select(Category).where(Category.name == name))
    if result.scalar_one_or_none():
        raise HTTPException(status.HTTP_409_CONFLICT, detail="分类名称已存在")

    category = Category(name=name, description=description, sort_order=sort_order)
    db.add(category)
    await db.flush()
    await db.refresh(category)
    return {"id": category.id, "name": category.name, "message": "创建成功"}


@router.put("/{category_id}")
async def update_category(
    category_id: int,
    name: str | None = None,
    description: str | None = None,
    sort_order: int | None = None,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """修改知识分类（管理员）"""
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="分类不存在")

    if name is not None:
        category.name = name
    if description is not None:
        category.description = description
    if sort_order is not None:
        category.sort_order = sort_order

    await db.flush()
    await db.refresh(category)
    return {"id": category.id, "name": category.name, "message": "修改成功"}


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """删除知识分类（管理员）"""
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="分类不存在")

    await db.delete(category)
    await db.flush()
