import os
import json
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from model import enterprise_annual_finance,enterprise_basic_info,enterprise_quarterly_finance,industry_development,tb_policies
load_dotenv()
def save_table_schema():
    tables = [enterprise_annual_finance,enterprise_basic_info,enterprise_quarterly_finance,industry_development,tb_policies]
    # 创建数据库用来存储所有数据表的规范
    
    embedding = OpenAIEmbeddings(
        model=os.getenv("EMBEDDING_MODEL"),
        openai_api_key=os.getenv("API_KEY"),
        base_url=os.getenv("BASE_URL"),
    )
    vector_store = Chroma(
    collection_name="table_schemas",
    embedding_function=embedding,
    persist_directory="table_schemas_db",
    )
    docs = [Document(page_content = json.dumps(table.model_json_schema(),ensure_ascii=False),metadata={"table_name":table.__name__},id=i) for i,table in enumerate(tables)]
    vector_store.add_documents(documents = docs)
    print("=============所有数据库表规范保存完毕==============")
def get_table_schema_store(persist_directory:str="table_schemas_db")->Chroma:
    embedding = OpenAIEmbeddings(
        model=os.getenv("EMBEDDING_MODEL"),
        openai_api_key=os.getenv("API_KEY"),
        base_url=os.getenv("BASE_URL"),
    )
    vector_store = Chroma(embedding_function=embedding,
    persist_directory=persist_directory,
    collection_name="table_schemas",
    )
    return vector_store


if __name__ == "__main__":
    save_table_schema()