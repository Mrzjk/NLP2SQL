"""
文本转成SQL语言的智能体搭建
"""
import operator
import os
import json
import operator
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder,PromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import PydanticOutputParser
from langgraph.graph import StateGraph,START,END
from langgraph.types import Literal,Command
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig
from dotenv import load_dotenv
from typing import TypedDict,Annotated
import pymysql
### 导入自定义的模块
from prompts import GENERATE_QUESTION_TEMPLATE,QUESTION_CHANGE_TEMPLATE,COMPLETETION_QUESTION_TEMPLATE,THINK_TEMPLATE,JUDGE_TEMPLATE
from config.config import Configuration
from utils.table_util import get_table_schema_store,save_table_schema
from utils.output_format import SqlFormat,QuestionFormat
from agent.model import ThinkResult,JudgeResult
from utils.dataset_util import rows_to_dicts
load_dotenv()
# 创建数据库连接
conn = pymysql.connect(
    host=os.getenv('DB_HOST'),
    port=int(os.getenv('DB_PORT')),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME'),
)


def create_llm():
    api_key = os.getenv("API_KEY")
    base_url = os.getenv("BASE_URL")
    model = os.getenv("MODEL_NAME")
    llm =ChatOpenAI(
        model=model,
        api_key=api_key,
        base_url=base_url,
        temperature=0.0,
       
    ).with_retry(stop_after_attempt=5)
    return llm
#creat llm for  question change  of chain
def create_llm_for_question_change_chain():
    parser = PydanticOutputParser(pydantic_object=QuestionFormat)
    # 提示词模板
    prompt = PromptTemplate(
        template = QUESTION_CHANGE_TEMPLATE,
        input_variables = ["original_question"],
        partial_variables = {"question_sql_format":parser.get_format_instructions()}
    )

    llm = create_llm()
    
    return prompt |llm| parser

# 定义状态图 的状态机
class SqlState(TypedDict):
    """
    定义 该智能体的状态 
    包括 当前的SQL语句 、执行当前SQL的相应信息
    """
    original_question: Annotated[str, "原始问题"]
    question: Annotated[str, "当前问题"]
    rewritten_question: Annotated[list[str], "当前问题不同的表述形式"]
    related_tables: Annotated[str, "当前问题所关联的表"]
    sql: Annotated[list[str], operator.add]
    execute_info: Annotated[list[dict], operator.add]
    plan:Annotated[ThinkResult, "通过反思sql的结果和当前问题后生成的思考计划"]
# 创建 plan excute 模式的workflow
def create_agent()->StateGraph:
    
    def change_question(state:SqlState,config: RunnableConfig):
        original_question = state["original_question"]
        llm_chain = create_llm_for_question_change_chain()
        response = llm_chain.invoke({"original_question":original_question}).change_question
        print(response)
        return {"rewritten_question":response}
    # 多路召回 检索与问题最相关的k张表
    def rag(state:SqlState,config: RunnableConfig):
         # Step 1: Check if clarification is enabled in configuration
        # configurable = Configuration.from_runnable_config(config)
        # if not configurable.relation_table_count:
        relation_table_count = 5
        # relation_table_count = configurable.relation_table_count
        vectores = get_table_schema_store()
        original_question = state['original_question']
        rewritten_question = state['rewritten_question']
        table_infos = []
        all_questions = [original_question]+rewritten_question
        for question in all_questions:
            table_infos.extend(vectores.similarity_search(question,k=relation_table_count))
        # 对检索到的所有表信息进行去重 合并 
        print("=============开始进行表信息合并==============")
        # print(f"检索到的所有表信息为:{table_infos}")
        table_dicts = dict()
        for table_info in table_infos:
            if table_info.metadata['table_name'] not in table_dicts.keys():
                table_dicts[table_info.metadata['table_name']] = table_info.page_content
        related_tables = """
        当前任务场景设定为：郑州航空港区。请基于已知数据表信息进行业务分析或SQL查询构建。
        以下是可用的数据表及其描述信息：

        """ + "\n".join([f"- {table_name}: {table_info}" for table_name, table_info in table_dicts.items()]) + """

        请注意：
        1. 每个数据表包含的字段及其含义已在描述中标明。
        2. 根据业务问题选择相关表进行关联查询，必要时可使用JOIN、GROUP BY、WHERE等操作。
        3. 输出结果应紧贴航空港区实际业务场景，保证数据逻辑合理。
        4. 对于涉及时间、产业、企业等维度的问题，请优先考虑表中相关字段。
        """
        print("=============相关的表信息合并完毕==============")
        return {"related_tables":related_tables}
    # 完善问题
    def completetion_question(state:SqlState,config: RunnableConfig):
        original_question = state['original_question']
        rewritten_question = state['rewritten_question']
        related_tables = state['related_tables']
        prompt = COMPLETETION_QUESTION_TEMPLATE.format(
            original_question=original_question,
            rewritten_question=rewritten_question,
            related_tables=related_tables
        )
        llm = create_llm()
        question = llm.invoke(prompt).content
        return {"question":question}
    # 生成SQL语句
    def generate_sql(state:SqlState,config:RunnableConfig):
        related_tables = state['related_tables']
        sql = state['sql']
        execute_info = state['execute_info']
        sql_format = PydanticOutputParser(pydantic_object=SqlFormat)
        # 使用系统提示词模板
        plan = state['plan']
        if plan == None:
            question = state['question']
        else:
            question = plan.plan[0]
            
        print("当前的用户需求",question)
        prompt = GENERATE_QUESTION_TEMPLATE.format(question=question,sql=sql,execute_info=execute_info,related_tables=related_tables,sql_format=sql_format.get_format_instructions())  
        llm = create_llm()
        response = llm.invoke(prompt).content
        sql = sql_format.parse(response).sql
        print("根据问题生成的sql",sql)
        return {"sql":[sql]}
    #执行SQL代码
    def execute_sql(state: SqlState,config: RunnableConfig):
        """
        在数据库中执行 SQL（事务回滚），仅用于验证语法和执行是否成功。
        """
        try:
            with conn.cursor() as cursor:
                cursor.execute("START TRANSACTION;")
                try:
                    sql = state["sql"][-1]
                    print("当前的sql语句",sql)
                    cursor.execute(sql)
                    results = cursor.fetchall()
                    print(results)
                    print(type(results))
                    res = rows_to_dicts(cursor,results)
                    print("数据库的结果",res)
                    return {"execute_info":[res]}
                except pymysql.MySQLError as e:
                    return {"execute_info": [f"执行错误，错误信息：{e}"]}          
                finally:
                    cursor.execute("ROLLBACK;")
        except pymysql.MySQLError as e:
            return {"execute_info": [f"数据库错误，错误信息：{e}"]}
    # 思考用户的问题和生成SQL语句执行的结果是否是对的
    def thinker(state:SqlState,config:RunnableConfig)->Command[Literal["generate_sql",END]]:
        question = state["question"]
        sql = state["sql"]
        execute_info = state["execute_info"]
        related_tables = state["related_tables"]
        llm = create_llm()
        print("====================判断sql结果能否满足用户需求=============================")
        parser = PydanticOutputParser(pydantic_object=JudgeResult)
        
        prompt = JUDGE_TEMPLATE.format(question=question,execute_info=execute_info[-1],related_tables=related_tables,json_format=parser.get_format_instructions())
        response = llm.invoke(prompt).content
        judege_result = parser.parse(response)
        if judege_result.match:
            return Command(goto=END)
        explain = judege_result.explain
        
        print("====================sql结果不能满足用户需求=============================")
        print(explain)
        print("====================思考中==========================")
        plan = state['plan']
        parser = PydanticOutputParser(pydantic_object=ThinkResult)
        prompt = THINK_TEMPLATE.format(question=question,sql=sql,execute_info=execute_info,
                                       related_tables=related_tables,plan=getattr(plan, "plan", None),
                                       explain=explain,
                                       json_format=parser.get_format_instructions())
        
        response = llm.invoke(prompt).content
        think_result = parser.parse(response)
        
        
        return Command(
            update={"plan": think_result},
            goto="generate_sql"
        )
    graph_builder  = StateGraph(SqlState)
    graph_builder.add_node("change_question",change_question)
    graph_builder.add_node("rag",rag)
    graph_builder.add_node("completetion_question",completetion_question)
    graph_builder.add_node("generate_sql",generate_sql)
    graph_builder.add_node("execute_sql",execute_sql)
    graph_builder.add_node("thinker",thinker)
    graph_builder.add_edge(START, "change_question")
    graph_builder.add_edge("change_question", "rag")
    graph_builder.add_edge("rag", "completetion_question")
    graph_builder.add_edge("completetion_question", "generate_sql")
    graph_builder.add_edge("generate_sql", "execute_sql")
    graph_builder.add_edge("execute_sql", "thinker")
    graph = graph_builder.compile()
    # # 获取图像二进制数据
    # png_data = graph.get_graph().draw_mermaid_png()

    # # 保存到本地文件
    # output_path = "graph_output.png"
    # with open(output_path, "wb") as f:
    #     f.write(png_data)

    # print(f"图像已保存到 {output_path}")
    return graph
if __name__ == '__main__':
    agent = create_agent()
    state = {"origin_question":"请比较2024年电子信息和装备制造两个产业的营收、利润和研发投入情况","sql":"", "execute_info":""}
    final_state = agent.invoke(state,recursion_limit=10)
    print(final_state)
    