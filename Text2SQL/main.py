from agent.graph import create_agent
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv()
if __name__ == "__main__":
    agent = create_agent()
    state = {"original_question":"比较2024年电子信息和装备制造两个产业的营收、利润和研发投入情况",
             "rewritten_question":[],
             "related_tables":"",
             "question":"",
             "sql":[],
             "execute_info":[],
             "plan":None}
    final_state = agent.invoke(state,recursion_limit=10)
    print("===========生成的SQL语句=============")
    print(final_state.get("sql")[-1])
    