import datetime
from dotenv import load_dotenv
from entsoe import EntsoePandasClient
from entsoe import exceptions
from entsoe import mappings
from os import getenv
import pandas as pd
import streamlit as st
import xmltodict

QUERY_OPTIONS = {
    "query_activated_balancing_energy": ["date_range", "country", "business_type"],
    "query_aggregate_water_reservoirs_and_hydro_storage": ["date_range", "country"],
    "query_contracted_reserve_amount": ["date_range", "country", "psr_type", "type_marketagreement_type"],
    "query_contracted_reserve_prices": ["date_range", "country", "psr_type", "type_marketagreement_type"],
    "query_crossborder_flows": ["date_range", "countries"],
    "query_day_ahead_prices": ["date_range", "country"],
    "query_generation": ["date_range", "country", "psr_type"],
    "query_generation_forecast": ["date_range", "country"],
    "query_generation_import": ["date_range", "country"],
    "query_generation_per_plant": ["date_range", "country", "psr_type"],
    "query_imbalance_prices": ["date_range", "country"],
    "query_imbalance_volumes": ["date_range", "country"],
    "query_import": ["date_range", "country"],
    "query_installed_generation_capacity": ["date_range", "country", "psr_type"],
    "query_installed_generation_capacity_per_unit": ["date_range", "country", "psr_type"],
    "query_intraday_offered_capacity": ["date_range", "countries", "implicit"],
    "query_load": ["date_range", "country"],
    "query_load_and_forecast": ["date_range", "country"],
    "query_load_forecast": ["date_range", "country"],
    "query_net_position": ["date_range", "country"],
    "query_net_transfer_capacity_dayahead": ["date_range", "countries"],
    "query_net_transfer_capacity_monthahead": ["date_range", "countries", "dayahead"],
    "query_net_transfer_capacity_weekahead": ["date_range", "countries"],
    "query_net_transfer_capacity_yearahead": ["date_range", "countries"],
    "query_offered_capacity": ["date_range", "countries", "contract_marketagreement_type"],
    "query_procured_balancing_capacity": ["date_range", "countries"],
    "query_scheduled_exchanges": ["date_range", "countries", "dayahead"],
    "query_unavailability_of_generation_units": ["date_range", "countries"],
    "query_unavailability_of_production_units": ["date_range", "country"],
    "query_unavailability_transmission": ["date_range", "countries"],
    "query_wind_and_solar_forecast": ["date_range", "country", "psr_type"],
    "query_withdrawn_unavailability_of_generation_units": ["date_range", "country"],
}


def run():
    """
    Run the whole program
    """

    # Set the page config
    st.set_page_config(page_title="ENTSO-E Downloader", page_icon="⚡")

    # Initialize the ENTSOE Pandas client
    load_dotenv(".env")
    if not getenv("ENTSOE_KEY"):
        raise KeyError("ENTSOE_KEY variable has not been set")
    client = EntsoePandasClient(api_key=getenv("ENTSOE_KEY"))

    # Create the sidebar title
    st.sidebar.title("ENTSO-E Importer")

    # Select an ENTSO-E query
    entsoe_queries = [query for query in dir(client) if query.startswith("query_")]
    load_and_forecast_index = entsoe_queries.index("query_load_and_forecast")
    format_query_name = lambda query_name: query_name.replace("query_", "").replace("_", " ").capitalize()
    selected_query = st.sidebar.selectbox("Data type", entsoe_queries, index=load_and_forecast_index, format_func=format_query_name)

    # Create the header for the selected query
    st.header(format_query_name(selected_query))

    # Get the options of the selected query and show a warning message if the options are not defined
    selected_query_options = QUERY_OPTIONS.get(selected_query)
    if selected_query_options is None:
        st.warning("This query has not been implemented yet")
        return

    # Create the form
    form = st.sidebar.form("inputs")
    form.header("Options")

    # Add the relevant parameters
    args = []
    kwargs = {}
    if "date_range" in selected_query_options:
        today = datetime.datetime.now()
        yesterday = today - datetime.timedelta(days=1)
        start, end = pd.to_datetime(form.date_input("Date range", value=(yesterday, today)), utc=True)
        kwargs["start"] = start
        kwargs["end"] = end
    if "country" in selected_query_options:
        areas = [code for code in dir(mappings.Area) if not code.startswith("_")]
        country_code = form.selectbox("Country", areas, index=areas.index("NL"), format_func=lambda key: mappings.Area[key].meaning)
        args.append(country_code)
    if "countries" in selected_query_options:
        areas = [code for code in dir(mappings.Area) if not code.startswith("_")]
        col1, col2 = form.columns(2)
        country_code_from = col1.selectbox("From", areas, index=areas.index("NL"), format_func=lambda key: mappings.Area[key].meaning)
        args.append(country_code_from)
        areas = mappings.NEIGHBOURS[country_code_from]
        country_code_to = col2.selectbox("To", areas, index=0, format_func=lambda key: mappings.Area[key].meaning)
        args.append(country_code_to)
    if "business_type" in selected_query_options:
        kwargs["business_type"] = form.selectbox("Business type", mappings.BSNTYPE.keys(), format_func=lambda key: mappings.BSNTYPE[key])
    if "type_marketagreement_type" in selected_query_options:
        kwargs["type_marketagreement_type"] = form.selectbox("Market agreement type", mappings.MARKETAGREEMENTTYPE.keys(), format_func=lambda key: mappings.MARKETAGREEMENTTYPE[key])
    if "contract_marketagreement_type" in selected_query_options:
        kwargs["contract_marketagreement_type"] = form.selectbox("Contract market agreement type", mappings.MARKETAGREEMENTTYPE.keys(), format_func=lambda key: mappings.MARKETAGREEMENTTYPE[key])
    if "psr_type" in selected_query_options:
        kwargs["psr_type"] = form.selectbox("PSR-type", mappings.PSRTYPE_MAPPINGS.keys(), format_func=lambda key: mappings.PSRTYPE_MAPPINGS[key])
    if "implicit" in selected_query_options:
        kwargs["implicit"] = form.checkbox("Implicit")
    if "dayahead" in selected_query_options:
        kwargs["dayahead"] = form.checkbox("Dayahead")

    # Retrieve the data when the button is clicked
    if form.form_submit_button("Fetch data", type="primary"):
        try:
            with st.spinner("Fetching data from ENTSO-E"):
                # Retrieve the data
                data = getattr(client, selected_query)(*args, **kwargs)

                # Show a preview of the data as a line chart
                chart_data = data.copy()
                if isinstance(chart_data, pd.DataFrame) and isinstance(chart_data.columns, pd.MultiIndex):
                    chart_data.columns = chart_data.columns.map(" - ".join)
                try:
                    st.line_chart(data=chart_data)
                except:
                    st.warning("Could not generate the graph")

                # Show a download button
                st.download_button("Download as CSV", data.to_csv(), file_name=f"{selected_query.replace('query_', '')}.csv", mime="text/csv")
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
            if hasattr(e, "response") and hasattr(e.response, "text"):
                response = xmltodict.parse(e.response.text)
                st.error(response["Acknowledgement_MarketDocument"]["Reason"]["text"])
            elif hasattr(e, "response") and hasattr(e.response, "reason"):
                st.error(e.response.reason)
            else:
                st.write(e)


run()
