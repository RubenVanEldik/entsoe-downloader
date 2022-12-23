import datetime
from entsoe import mappings
import pandas as pd
import streamlit as st


def form():
    form = st.sidebar.form("inputs")
    form.header("Options")
    return form


def country(form, label="Country", neighbouring_area=None):
    if neighbouring_area is None:
        areas = [code for code in dir(mappings.Area) if not code.startswith("_")]
        index = areas.index("NL")
    else:
        areas = mappings.NEIGHBOURS[neighbouring_area]
        index = 0
    return form.selectbox(label, areas, index=index, format_func=lambda key: mappings.Area[key].meaning)


def date_range(form):
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)
    return pd.to_datetime(form.date_input("Date range", value=(yesterday, today)), utc=True)


def psr_type(form, *, type="intermittent_renewable"):
    return form.selectbox("PSR-type", mappings.PSRTYPE_MAPPINGS.keys(), format_func=lambda key: mappings.PSRTYPE_MAPPINGS[key])


def doc_status(form):
    return form.selectbox("Document status", mappings.DOCSTATUS.keys(), format_func=lambda key: mappings.DOCSTATUS[key])


def business_type(form):
    return form.selectbox("Business type", mappings.BSNTYPE.keys(), format_func=lambda key: mappings.BSNTYPE[key])


def market_agreement_type(form):
    return form.selectbox("Market agreement type", mappings.MARKETAGREEMENTTYPE.keys(), format_func=lambda key: mappings.MARKETAGREEMENTTYPE[key])


def document_type(form):
    return form.selectbox("Document type", mappings.DOCUMENTTYPE.keys(), format_func=lambda key: mappings.DOCUMENTTYPE[key])


def process_type(form):
    return form.selectbox("Process type", mappings.PROCESSTYPE.keys(), format_func=lambda key: mappings.PROCESSTYPE[key])
