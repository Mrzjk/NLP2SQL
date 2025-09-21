from pydantic import BaseModel, Field
from typing import Annotated
from langchain_core.output_parsers import PydanticOutputParser
class SqlFormat(BaseModel):
    """
    SQL文本格式化模型
    用于将自然语言文本或业务问题转换为标准SQL语句。
    支持所有SQL操作类型，包括查询、插入、更新、删除和表结构变更。
    
    Attributes:
        sql (str): 生成的标准SQL语句，必须符合目标数据库（如MySQL）的语法规范。
    """
    sql: Annotated[
        str,
        Field(
            title="SQL语句",
            description="生成的标准SQL语句，可为SELECT/INSERT/UPDATE/DELETE/DDL等类型",
            example="INSERT INTO students (id, name, age) VALUES (1, 'Alice', 20);"
        )
    ]
class QuestionFormat(BaseModel):
    """
    用户文本的改写输出格式

    Attributes:
        change_question (str): 将用户的问题改写为更专业的
    """
    change_question: Annotated[list[str], Field(title="改写后的问题", description="将用户的问题改写为更专业的表达")]
if __name__ == '__main__':
    parser = PydanticOutputParser(pydantic_object=SqlFormat)
    print(parser.get_format_instructions())
    print(SqlFormat.model_json_schema())