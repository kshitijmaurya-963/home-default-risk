from pydantic import BaseModel


class PredictionRequest(BaseModel):

    # Financial

    amt_income_total: float | None = None

    amt_credit: float | None = None

    amt_annuity: float | None = None

    amt_goods_price: float | None = None


    # Demographic

    days_birth: float | None = None

    days_employed: float | None = None

    days_registration: float | None = None

    days_id_publish: float | None = None

    days_last_phone_change: float | None = None

    region_population_relative: float | None = None


    # External Scores

    ext_source_1: float | None = None

    ext_source_2: float | None = None

    ext_source_3: float | None = None


    # Bureau

    bureau_avg_credit: float | None = None

    bureau_recent_credit: float | None = None

    bureau_delinquency_count: float | None = None

    bureau_active_count: float | None = None

    bureau_record_count: float | None = None


    # Previous Applications

    prev_app_count: float | None = None

    prev_avg_credit: float | None = None

    prev_avg_annuity: float | None = None


    # Engineered

    debt_to_income: float | None = None

    credit_utilization: float | None = None

    days_employed_ratio: float | None = None

    approval_rate: float | None = None