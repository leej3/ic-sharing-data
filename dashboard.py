import streamlit as st
import pandas as pd
import plotly.express as px

# Function to load data with the new caching mechanism
@st.cache_data
def load_data():
    return pd.read_parquet('data/all_ics.parquet')

def optimize_dtype(column):
    """Optimize the dtype of a pandas Series.

    Apply the optimization function to each column:
    data = data.apply(optimize_dtype)
    """
    if column.dtype == 'object':
        # Check if the object column can be converted to category
        unique_values = column.nunique()
        total_values = len(column)
        if unique_values / total_values < 0.5:
            return column.astype('category')
        else:
            return column
    elif column.dtype == 'float64':
        # Fill NaNs with a placeholder and convert to int if possible
        column = column.fillna(999999)
        if (column % 1 == 0).all():  # Check if all values are integers
            return column.astype('int32')
        else:
            return column.astype('float32')
    elif column.dtype == 'int64':
        # Convert int64 to int32 if possible
        return column.astype('int32')
    elif column.dtype == 'bool':
        return column.astype('bool')
    else:
        return column



# Function to plot bar chart
def plot_bar_chart(data, x, y, hover_data, title):
    fig = px.bar(
        data,
        x=x,
        y=y,
        hover_data=hover_data,
        labels={y: title, x: ''}
    )
    fig.update_traces(marker_color='blue')
    fig.update_layout(xaxis={'categoryorder':'total descending'}, xaxis_showticklabels=False)
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# Load data
data = load_data()

# Page selection
page = st.sidebar.selectbox('Select a Page:', ['PI Data', 'IC Data'])

if page == 'PI Data':
    # Filters for PI Data page
    years = data['journal_year'].unique().tolist()
    ics = data['organization_name'].unique().tolist()
    year_choice = st.sidebar.multiselect('Year', years, default=years)
    ic_choice = st.sidebar.multiselect('IC (Organization)', ics, default=ics)
    
    # Filtering data for PI Data page
    filtered_data = data[(data['journal_year'].isin(year_choice)) & (data['organization_name'].isin(ic_choice))]

    # Grouping data for PI Data page
    grouped_data = filtered_data.groupby('contact_pi_project_leader').agg(
        num_pmids=('pmid', 'size'),
        num_unique_pmids=('pmid', pd.Series.nunique),
        proportion_pmids_open=('pmid', lambda x: x[filtered_data['open_data']].nunique() / x.nunique() if x.nunique() > 0 else 0)
    ).reset_index()

    # Sorting the grouped data for better visualization for PI Data page
    grouped_data = grouped_data.sort_values('num_unique_pmids', ascending=False)

    # Display the table for PI Data page
    st.write('Filtered Data', grouped_data)

    # Plotting for PI Data page
    plot_bar_chart(grouped_data, 'contact_pi_project_leader', 'num_unique_pmids', ['contact_pi_project_leader', 'num_unique_pmids'], 'Number of Unique PMIDs')
    plot_bar_chart(grouped_data, 'contact_pi_project_leader', 'proportion_pmids_open', ['contact_pi_project_leader', 'proportion_pmids_open'], 'Proportion of Open Data PMIDs')

elif page == 'IC Data':
    # Filters for IC Data page
    years = data['journal_year'].unique().tolist()
    year_choice = st.sidebar.multiselect('Year', years, default=years)
    
    # Filtering data for IC Data page
    filtered_data = data[(data['journal_year'].isin(year_choice))]

    # Grouping data for IC Data page
    grouped_data_ic = filtered_data.groupby('organization_name').agg(
        num_pmids=('pmid', 'size'),
        num_unique_pmids=('pmid', pd.Series.nunique),
        proportion_pmids_open=('pmid', lambda x: x[filtered_data['open_data']].nunique() / x.nunique() if x.nunique() > 0 else 0)
    ).reset_index()

    # Sorting the grouped data for better visualization for IC Data page
    grouped_data_ic = grouped_data_ic.sort_values('num_unique_pmids', ascending=False)

    # Display the table for IC Data page
    st.write('Filtered Data by IC', grouped_data_ic)

    # Plotting for IC Data page
    plot_bar_chart(grouped_data_ic, 'organization_name', 'num_unique_pmids', ['organization_name', 'num_unique_pmids'], 'Number of Unique PMIDs')
    plot_bar_chart(grouped_data_ic, 'organization_name', 'proportion_pmids_open', ['organization_name', 'proportion_pmids_open'], 'Proportion of Open Data PMIDs')