from pydantic import BaseModel,Field
from typing import Annotated,List
class ThinkResult(BaseModel):
    plan: Annotated[List[str], Field(title="计划列表", description="计划列表")]


class JudgeResult(BaseModel):
    match: Annotated[bool, Field(title="是否匹配", description="判断当前 SQL 执行结果是否满足用户问题")]
    explain: Annotated[str, Field(title="解释", description="解释当前 SQL 执行结果是否满足用户问题")]
