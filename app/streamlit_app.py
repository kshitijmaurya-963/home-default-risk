import streamlit as st
import requests
import math

BASE_URL = "http://127.0.0.1:8000"


# ---------------------------------
# Page Config
# ---------------------------------

st.set_page_config(
    page_title="Loan Default Risk Predictor",
    page_icon="🏦",
    layout="wide"
)


# ---------------------------------
# Session State
# ---------------------------------

if "features" not in st.session_state:
    st.session_state["features"] = {}

if "actual_target" not in st.session_state:
    st.session_state["actual_target"] = None

if "actual_label" not in st.session_state:
    st.session_state["actual_label"] = None

if "case_id" not in st.session_state:
    st.session_state["case_id"] = None

if "prediction" not in st.session_state:
    st.session_state["prediction"] = None


# ---------------------------------
# API Helpers
# ---------------------------------

def get_metrics():

    response = requests.get(
        f"{BASE_URL}/metrics"
    )

    response.raise_for_status()

    return response.json()


def get_sample():

    response = requests.get(
        f"{BASE_URL}/sample"
    )

    response.raise_for_status()

    return response.json()


def predict(data):

    response = requests.post(
        f"{BASE_URL}/predict",
        json=data
    )

    response.raise_for_status()

    return response.json()


# ---------------------------------
# Header
# ---------------------------------

st.title("🏦 Loan Default Risk Predictor")

metrics = get_metrics()

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Model",
        metrics["model"]
    )

with col2:

    st.metric(
        "AUC",
        metrics["auc"]
    )

with col3:

    st.metric(
        "Features",
        metrics["features"]
    )

with col4:

    st.metric(
        "Recall",
        metrics["recall"]
    )


st.divider()

# ---------------------------------
# Feature Groups
# ---------------------------------

feature_groups = {

    "Financial": [

        "amt_income_total",

        "amt_credit",

        "amt_annuity",

        "amt_goods_price"

    ],


    "Demographics": [

        "days_birth",

        "days_employed",

        "days_registration",

        "days_id_publish",

        "days_last_phone_change",

        "region_population_relative"

    ],


    "External Risk Scores": [

        "ext_source_1",

        "ext_source_2",

        "ext_source_3"

    ],


    "Bureau History": [

        "bureau_avg_credit",

        "bureau_recent_credit",

        "bureau_delinquency_count",

        "bureau_active_count",

        "bureau_record_count"

    ],


    "Previous Applications": [

        "prev_app_count",

        "prev_avg_credit",

        "prev_avg_annuity"

    ],


    "Engineered Features": [

        "debt_to_income",

        "credit_utilization",

        "days_employed_ratio",

        "approval_rate"

    ]

}

feature_labels = {

    "amt_income_total":"Income",

    "amt_credit":"Credit Amount",

    "amt_annuity":"Annuity",

    "amt_goods_price":"Goods Price",


    "days_birth":"Days Birth",

    "days_employed":"Days Employed",

    "days_registration":"Days Registration",

    "days_id_publish":"Days ID Publish",

    "days_last_phone_change":"Days Last Phone Change",

    "region_population_relative":"Region Population Relative",


    "ext_source_1":"External Risk Score 1",

    "ext_source_2":"External Risk Score 2",

    "ext_source_3":"External Risk Score 3",


    "bureau_avg_credit":"Bureau Avg Credit",

    "bureau_recent_credit":"Bureau Recent Credit",

    "bureau_delinquency_count":"Bureau Delinquencies",

    "bureau_active_count":"Bureau Active Accounts",

    "bureau_record_count":"Bureau Record Count",


    "prev_app_count":"Previous Applications",

    "prev_avg_credit":"Previous Avg Credit",

    "prev_avg_annuity":"Previous Avg Annuity",


    "debt_to_income":"Debt to Income",

    "credit_utilization":"Credit Utilization",

    "days_employed_ratio":"Employment Ratio",

    "approval_rate":"Approval Rate"

}

st.subheader("Sample Applicant")


if st.button("🎲 Load Sample Applicant"):

    sample = get_sample()

    st.session_state["features"] = sample["features"]

    st.session_state["actual_target"] = sample["actual_target"]

    st.session_state["actual_label"] = sample["actual_label"]

    st.session_state["case_id"] = sample["case_id"]


if st.session_state["case_id"] is not None:

    st.success(

        f"Loaded Case #{st.session_state['case_id']}"

    )

    st.write(

        f"Actual Outcome: "

        f"{st.session_state['actual_label']}"

    )


st.divider()

st.subheader("Applicant Information")

user_input = {}

left_groups = [

    "Financial",

    "Demographics",

    "External Risk Scores"

]

right_groups = [

    "Bureau History",

    "Previous Applications",

    "Engineered Features"

]


col1, col2 = st.columns(2)


# -----------------------------
# Left Column
# -----------------------------

with col1:

    for group in left_groups:

        st.markdown(f"### {group}")

        for feature in feature_groups[group]:

            value = (
                st.session_state["features"]
                .get(feature, 0)
            )

            if value is None:

                value = 0


            # Age

            if feature == "days_birth":

                age_years = max(
                    18,
                    int(
                        abs(value) / 365
                    )
                )

                age_years = st.number_input(

                    "Age (Years)",

                    min_value=18,

                    max_value=100,

                    value=age_years,

                    key=feature

                )

                user_input[feature] = -age_years * 365


            # Employment

            elif feature == "days_employed":

                employment_years = max(
                    0.0,
                    round(
                        abs(value) / 365,
                        1
                    )
                )

                employment_years = st.number_input(

                    "Employment Duration (Years)",

                    min_value=0.0,

                    max_value=50.0,

                    value=employment_years,

                    key=feature

                )

                user_input[feature] = (
                    -employment_years * 365
                )


            else:

                help_text = None

                if feature in [

                    "ext_source_1",

                    "ext_source_2",

                    "ext_source_3"

                ]:

                    help_text = """

                External creditworthiness score.

                Usually obtained from:

                • Credit bureaus

                • Fraud systems

                • Internal risk engines

                """


                user_input[feature] = st.number_input(

                    label=feature_labels[feature],

                    value=float(value),

                    help=help_text,

                    key=feature

                )


# -----------------------------
# Right Column
# -----------------------------

with col2:

    for group in right_groups:

        st.markdown(f"### {group}")

        for feature in feature_groups[group]:

            value = (

                st.session_state["features"]

                .get(feature, 0)

            )

            

            if value is None:

                value = 0

            elif isinstance(value, float):

                if math.isnan(value):

                    value = 0


            user_input[feature] = st.number_input(

                label=feature_labels[feature],

                value=float(value),

                key=feature

            )

st.divider()


if st.button(

    "🔍 Predict Default Risk",

    type="primary",

    use_container_width=True

):

    result = predict(

        user_input

    )

    st.session_state["prediction"] = result


if st.session_state["prediction"]:

    result = st.session_state["prediction"]


    st.divider()

    st.subheader("Prediction Results")


    c1, c2, c3 = st.columns(3)


    with c1:

        st.metric(

            "Risk Score",

            f"{result['risk_score']}%"

        )

    st.progress(

        result["risk_score"] / 100

    )

    with c2:

        band = result["risk_band"]


        if band == "Low":

            st.success(

                "🟢 LOW"

            )


        elif band == "Medium":

            st.warning(

                "🟡 MEDIUM"

            )


        else:

            st.error(

                "🔴 HIGH"

            )


    with c3:

        st.metric(

            "Prediction",

            result["risk_label"]

        )


    # Compare with actual

    actual_target = st.session_state["actual_target"]


    if actual_target is not None:

        st.write("### Actual Outcome")

        c1, c2 = st.columns(2)

        with c1:

            st.metric(

                "Actual Outcome",

                st.session_state["actual_label"]

            )


        with c2:

            st.metric(

                "Predicted",

                result["risk_label"]

            )


        correct = (

            actual_target

            == result["prediction"]

        )


        if correct:

            st.success(

                "✅ Prediction Correct"

            )

        else:

            st.error(

                "❌ Prediction Incorrect"

            )