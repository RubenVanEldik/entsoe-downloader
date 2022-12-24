from dotenv import load_dotenv
from entsoe import EntsoePandasClient
from entsoe import exceptions
from os import getenv
import pandas as pd
import streamlit as st

import interface

# Set the page config
st.set_page_config(page_title="ENTSO-E Downloader", page_icon="⚡")

# Initialize the ENTSOE Pandas client
load_dotenv(".env")
if not getenv("ENTSOE_KEY"):
    raise KeyError("ENTSOE_KEY variable has not been set")
client = EntsoePandasClient(api_key=getenv("ENTSOE_KEY"))

# Create the sidebar title
st.sidebar.title("ENTSO-E Importer")

# Select a ENTSO-E method
entsoe_methods = [method for method in dir(client) if method.startswith("query_")]
load_and_forecast_index = entsoe_methods.index("query_load_and_forecast")
format_method_name = lambda method_name: method_name.replace("query_", "").replace("_", " ").capitalize()
selected_method = st.sidebar.selectbox("Data type", entsoe_methods, index=load_and_forecast_index, format_func=format_method_name)

# Create the header for the selected method
st.header(format_method_name(selected_method))


def retrieve(method, *args, **kwargs):
    """
    Fetch the data from the ENTSO-E API
    """
    if form.form_submit_button("Fetch data", type="primary"):
        try:
            with st.spinner("Fetching data from ENTSO-E"):
                # Retrieve the data
                data = getattr(client, method)(*args, **kwargs)

                # Show a preview of the data as a line chart
                chart_data = data.copy()
                if isinstance(chart_data, pd.DataFrame) and isinstance(chart_data.columns, pd.MultiIndex):
                    chart_data.columns = chart_data.columns.map(" - ".join)
                st.line_chart(data=chart_data)

                # Show a download button
                st.download_button("Download as CSV", data.to_csv(), file_name=f"{method.replace('query_', '')}.csv", mime="text/csv")
        except exceptions.NoMatchingDataError:
            st.error("There is no data available for this country in this time period")
            return
        except exceptions.InvalidBusinessParameterError:
            st.error("Invalid business parameter")
            return
        except exceptions.InvalidPSRTypeError:
            st.error("Invalid PSR type")
            return
        except exceptions.PaginationError:
            st.error("Invalid page")
            return
        except Exception as e:
            if hasattr(e, "response") and hasattr(e.response, "reason"):
                st.error(e.response.reason)
            else:
                st.error("Something went wrong...")
            return


if selected_method == "query_activated_balancing_energy":
    form = interface.form()
    country = interface.country(form)
    start, end = interface.date_range(form)
    business_type = interface.business_type(form)
    retrieve("query_activated_balancing_energy", country, start=start, end=end, business_type=business_type)

elif selected_method == "query_contracted_reserve_amount":
    form = interface.form()
    start, end = interface.date_range(form)
    country = interface.country(form)
    psr_type = interface.psr_type(form)
    type_marketagreement_type = interface.market_agreement_type(form)
    retrieve("query_contracted_reserve_amount", country, start=start, end=end, type_marketagreement_type=type_marketagreement_type, psr_type=psr_type)

elif selected_method == "query_day_ahead_prices":
    form = interface.form()
    start, end = interface.date_range(form)
    country = interface.country(form)
    retrieve("query_day_ahead_prices", country, start=start, end=end)

elif selected_method == "query_net_position_dayahead":
    form = interface.form()
    start, end = interface.date_range(form)
    country = interface.country(form)
    retrieve("query_net_position_dayahead", country, start=start, end=end)

elif selected_method == "query_crossborder_flows":
    form = interface.form()
    start, end = interface.date_range(form)
    col1, col2 = form.columns(2)
    country_from = interface.country(col1, label="From")
    country_to = interface.country(col2, label="To", neighbouring_area=country_from)
    retrieve("query_crossborder_flows", country_from, country_to, start=start, end=end)

elif selected_method == "query_scheduled_exchanges":
    form = interface.form()
    start, end = interface.date_range(form)
    col1, col2 = form.columns(2)
    country_from = interface.country(col1, label="From")
    country_to = interface.country(col2, label="To", neighbouring_area=country_from)
    dayahead = form.checkbox("Dayahead")
    retrieve("query_scheduled_exchanges", country_from, country_to, start=start, end=end, dayahead=dayahead)

elif selected_method == "query_net_transfer_capacity_dayahead":
    form = interface.form()
    start, end = interface.date_range(form)
    col1, col2 = form.columns(2)
    country_from = interface.country(col1, label="From")
    country_to = interface.country(col2, label="To", neighbouring_area=country_from)
    retrieve("query_net_transfer_capacity_dayahead", country_from, country_to, start=start, end=end)

elif selected_method == "query_net_transfer_capacity_weekahead":
    form = interface.form()
    start, end = interface.date_range(form)
    col1, col2 = form.columns(2)
    country_from = interface.country(col1, label="From")
    country_to = interface.country(col2, label="To", neighbouring_area=country_from)
    retrieve("query_net_transfer_capacity_weekahead", country_from, country_to, start=start, end=end)

elif selected_method == "query_net_transfer_capacity_monthahead":
    form = interface.form()
    start, end = interface.date_range(form)
    col1, col2 = form.columns(2)
    country_from = interface.country(col1, label="From")
    country_to = interface.country(col2, label="To", neighbouring_area=country_from)
    dayahead = form.checkbox("Dayahead")
    retrieve("query_net_transfer_capacity_monthahead", country_from, country_to, start=start, end=end)

elif selected_method == "query_net_transfer_capacity_yearahead":
    form = interface.form()
    start, end = interface.date_range(form)
    col1, col2 = form.columns(2)
    country_from = interface.country(col1, label="From")
    country_to = interface.country(col2, label="To", neighbouring_area=country_from)
    retrieve("query_net_transfer_capacity_yearahead", country_from, country_to, start=start, end=end)

elif selected_method == "query_intraday_offered_capacity":
    form = interface.form()
    start, end = interface.date_range(form)
    col1, col2 = form.columns(2)
    country_from = interface.country(col1, label="From")
    country_to = interface.country(col2, label="To", neighbouring_area=country_from)
    implicit = st.checkbox("Implicit")
    retrieve("query_intraday_offered_capacity", country_from, country_to, start=start, end=end, implicit=implicit)

elif selected_method == "query_load":
    form = interface.form()
    start, end = interface.date_range(form)
    country = interface.country(form)
    retrieve("query_load", country, start=start, end=end)

elif selected_method == "query_load_forecast":
    form = interface.form()
    start, end = interface.date_range(form)
    country = interface.country(form)
    retrieve("query_load_forecast", country, start=start, end=end)

elif selected_method == "query_load_and_forecast":
    form = interface.form()
    start, end = interface.date_range(form)
    country = interface.country(form)
    retrieve("query_load_and_forecast", country, start=start, end=end)

elif selected_method == "query_generation_forecast":
    form = interface.form()
    start, end = interface.date_range(form)
    country = interface.country(form)
    retrieve("query_generation_forecast", country, start=start, end=end)

elif selected_method == "query_wind_and_solar_forecast":
    form = interface.form()
    start, end = interface.date_range(form)
    country = interface.country(form)
    psr_type = interface.psr_type(form)
    retrieve("query_wind_and_solar_forecast", country, start=start, end=end, psr_type=psr_type)

elif selected_method == "query_generation":
    form = interface.form()
    start, end = interface.date_range(form)
    country = interface.country(form)
    psr_type = interface.psr_type(form)
    retrieve("query_generation", country, start=start, end=end, psr_type=psr_type)

elif selected_method == "query_generation_per_plant":
    form = interface.form()
    start, end = interface.date_range(form)
    country = interface.country(form)
    psr_type = interface.psr_type(form)
    retrieve("query_generation_per_plant", country, start=start, end=end, psr_type=psr_type)

elif selected_method == "query_installed_generation_capacity":
    form = interface.form()
    start, end = interface.date_range(form)
    country = interface.country(form)
    psr_type = interface.psr_type(form)
    retrieve("query_installed_generation_capacity", country, start=start, end=end, psr_type=psr_type)

elif selected_method == "query_installed_generation_capacity_per_unit":
    form = interface.form()
    start, end = interface.date_range(form)
    country = interface.country(form)
    psr_type = interface.psr_type(form)
    retrieve("query_installed_generation_capacity_per_unit", country, start=start, end=end, psr_type=psr_type)

elif selected_method == "query_imbalance_prices":
    form = interface.form()
    start, end = interface.date_range(form)
    country = interface.country(form)
    psr_type = interface.psr_type(form)
    retrieve("query_imbalance_prices", country, start=start, end=end, psr_type=psr_type)

elif selected_method == "query_contracted_reserve_prices":
    form = interface.form()
    start, end = interface.date_range(form)
    country = interface.country(form)
    psr_type = interface.psr_type(form)
    type_marketagreement_type = interface.market_agreement_type(form)
    retrieve("query_contracted_reserve_prices", country, start=start, end=end, type_marketagreement_type=type_marketagreement_type, psr_type=psr_type)

elif selected_method == "query_withdrawn_unavailability_of_generation_units":
    form = interface.form()
    start, end = interface.date_range(form)
    country = interface.country(form)
    retrieve("query_withdrawn_unavailability_of_generation_units", country, start=start, end=end)

elif selected_method == "query_import":
    form = interface.form()
    start, end = interface.date_range(form)
    country = interface.country(form)
    retrieve("query_import", country, start=start, end=end)

elif selected_method == "query_generation_import":
    form = interface.form()
    start, end = interface.date_range(form)
    country = interface.country(form)
    retrieve("query_generation_import", country, start=start, end=end)

else:
    st.warning("This method has not been implemented yet")
