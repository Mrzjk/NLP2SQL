from pydantic import BaseModel, Field
from typing import Annotated, Optional,Any
from datetime import date, datetime

# 企业年度财务数据表
class enterprise_annual_finance(BaseModel):
    """
    企业年度财务数据表:enterprise_annual_finance
    """
    finance_id: Annotated[str, Field(title="财务记录唯一标识", description="财务记录唯一标识")]
    enterprise_id: Annotated[str, Field(title="企业唯一标识", description="企业唯一标识")]
    year: Annotated[int, Field(title="年份", description="年份")]
    revenue: Annotated[float, Field(title="营业收入", description="营业收入（单位：万元）")]
    profit: Annotated[float, Field(title="利润", description="利润（单位：万元）")]
    tax_payment: Annotated[float, Field(title="纳税额", description="纳税额（单位：万元）")]
    rd_investment: Annotated[float, Field(title="研发投入", description="研发投入（单位：万元）")]
    export_amount: Annotated[float, Field(title="出口额", description="出口额（单位：万元）")]

# 企业基本信息表
class enterprise_basic_info(BaseModel):
    """
    企业基本信息表:enterprise_basic_info
    """
    enterprise_id: Annotated[str, Field(title="企业唯一标识", description="企业唯一标识")]
    enterprise_name: Annotated[str, Field(title="企业名称", description="企业名称")]
    industry_type: Annotated[str, Field(title="行业类型", description="行业类型")]
    establishment_year: Annotated[int, Field(title="成立年份", description="成立年份")]
    registered_capital: Annotated[float, Field(title="注册资本", description="注册资本（单位：万元）")]
    employee_count: Annotated[int, Field(title="员工人数", description="员工人数（单位：人）")]

# 企业季度财务数据表
class enterprise_quarterly_finance(BaseModel):
    """
    企业季度财务数据表:enterprise_quarterly_finance
    """
    id: Annotated[str, Field(title="季度记录唯一标识", description="季度记录唯一标识")]
    enterprise_id: Annotated[str, Field(title="企业唯一标识", description="企业唯一标识")]
    year: Annotated[int, Field(title="年份", description="年份")]
    quarter: Annotated[str, Field(title="季度", description="季度（1-4）")]
    revenue: Annotated[float, Field(title="营业收入", description="营业收入（单位：万元）")]
    profit: Annotated[float, Field(title="利润", description="利润（单位：万元）")]
    tax_payment: Annotated[float, Field(title="纳税额", description="纳税额（单位：万元）")]
    export_amount: Annotated[float, Field(title="出口额", description="出口额（单位：万元）")]

# 产业发展情况表
class industry_development(BaseModel):
    """
    产业发展情况表:industry_development
    """
    id: Annotated[int, Field(title="行业记录唯一标识", description="行业记录唯一标识")]
    industry_type: Annotated[str, Field(title="行业类型", description="行业类型")]
    year: Annotated[int, Field(title="年份", description="年份")]
    enterprise_count: Annotated[int, Field(title="企业数量", description="企业数量（单位：家）")]
    total_revenue: Annotated[float, Field(title="行业总收入", description="行业总收入（单位：万元）")]
    total_profit: Annotated[float, Field(title="行业总利润", description="行业总利润（单位：万元）")]
    total_employees: Annotated[int, Field(title="行业总员工数", description="行业总员工数（单位：人）")]
    total_tax: Annotated[float, Field(title="行业总纳税额", description="行业总纳税额（单位：万元）")]
    rd_percentage: Annotated[float, Field(title="研发投入占比", description="研发投入占比（单位：%）")]

# 政策表
class tb_policies(BaseModel):
    """
    政策表:tb_policies
    """
    id: Annotated[int, Field(title="id", description="自增ID")]
    policy_id: Annotated[Optional[str], Field(title="政策ID", description="政策ID")]
    policy_title: Annotated[str, Field(title="政策标题", description="政策标题，不能为空")]
    issuing_number: Annotated[Optional[str], Field(title="发文字号", description="发文字号")]
    policy_type: Annotated[Optional[str], Field(title="政策类型", description="政策类型，例如“规划类”、“支持类”")]
    issuing_authority: Annotated[Optional[str], Field(title="发布机构", description="发布机构")]
    administrative_level: Annotated[Optional[str], Field(title="行政级别", description="行政级别，例如“区/县级”")]
    publication_date: Annotated[Optional[date], Field(title="发布日期", description="发布日期")]
    implementation_date: Annotated[Optional[date], Field(title="实施日期", description="实施日期")]
    expiry_date: Annotated[Optional[date], Field(title="失效日期", description="失效日期")]
    policy_summary: Annotated[Optional[str], Field(title="政策摘要", description="政策摘要")]
    main_objectives: Annotated[Optional[str], Field(title="主要目标", description="主要目标")]
    keywords: Annotated[Optional[str], Field(title="关键词标签", description="关键词标签，多个关键词可以用逗号分隔")]
    applicable_objects: Annotated[Optional[str], Field(title="适用对象", description="适用对象")]
    industry_sectors: Annotated[Optional[str], Field(title="行业领域", description="行业领域")]
    company_size_requirement: Annotated[Optional[str], Field(title="企业规模要求", description="企业规模要求")]
    regional_restriction: Annotated[Optional[str], Field(title="区域限制", description="区域限制")]
    application_conditions: Annotated[Optional[str], Field(title="申报条件", description="申报条件")]
    application_time: Annotated[Optional[str], Field(title="申报时间", description="申报时间，例如“常态化申报”、“每年3月、9月”")]
    review_period: Annotated[Optional[str], Field(title="评审周期", description="评审周期")]
    support_type: Annotated[Optional[str], Field(title="支持类型", description="支持类型，例如“资金补贴、税收减免”、“资金补贴、设备补贴”")]
    funding_amount: Annotated[Optional[str], Field(title="资金额度", description="资金额度")]
    funding_disbursement_method: Annotated[Optional[str], Field(title="资金拨付方式", description="资金拨付方式")]
    assessment_indicators: Annotated[Optional[str], Field(title="考核指标", description="考核指标")]
    entry_time: Annotated[Optional[datetime], Field(title="入库时间", description="入库时间")]
    updated_time: Annotated[Optional[datetime], Field(title="最后更新时间", description="最后更新时间")]
    policy_json: Annotated[Optional[dict], Field(title="政策原文", description="政策原文")]

if __name__ == '__main__':
    info = tb_policies.model_json_schema()
    print(info.get('description'))
    print(info)
    print(tb_policies.__name__)