#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Turkey Residential Electricity Demand Visualization (2025-2050)

This application visualizes residential electricity demand projections for Turkey
based on different Shared Socioeconomic Pathways (SSP) scenarios. It provides an
interactive map and charts showing both historical data and future projections
at national and provincial levels.

Original Author: Mounjur Mourshed (mourshedm@cardiff.ac.uk, monjur@mourshed.org)
Contributors: Oguzhan Gulaydin (GulaydinO@cardiff.ac.uk) - bug fixes and enhancements

License: MIT License

Copyright (c) 2025 Mounjur Mourshed

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import pandas as pd
import folium
import streamlit as st
import plotly.express as px
import json
import os
import unicodedata
from streamlit_folium import st_folium

# ============================================================================
# DATA LOADING AND PREPROCESSING
# ============================================================================

# Define base data directory
base_dir = os.path.join(os.path.dirname(__file__), 'data')
xlsx_dir = os.path.join(base_dir, 'xlsx')

# Load all SSP (Shared Socioeconomic Pathways) scenario files
# SSP1: Sustainability – Taking the Green Road
# SSP2: Middle of the Road
# SSP3: Regional Rivalry – A Rocky Road
# SSP4: Inequality – A Road Divided
# SSP5: Fossil-fueled Development – Taking the Highway
ssp_files = {
    'SSP1': pd.read_excel(os.path.join(xlsx_dir, 'SSP1.xlsx')),
    'SSP2': pd.read_excel(os.path.join(xlsx_dir, 'SSP2.xlsx')),
    'SSP3': pd.read_excel(os.path.join(xlsx_dir, 'SSP3.xlsx')),
    'SSP4': pd.read_excel(os.path.join(xlsx_dir, 'SSP4.xlsx')),
    'SSP5': pd.read_excel(os.path.join(xlsx_dir, 'SSP5.xlsx'))
}

def normalize_province(name):
    """
    Normalize Turkish province names to handle character encoding issues.

    This function was added by Oguzhan Gulaydin to fix matching issues between
    province names in different datasets that may use different Turkish character
    encodings (ç, ğ, ı, ö, ş, ü).

    Args:
        name (str): Province name to normalize

    Returns:
        str: Normalized province name with special characters replaced
    """
    name = name.strip().casefold()  # Unicode-aware lowercasing
    # Replace Turkish special characters with their ASCII equivalents
    name = name.replace('ç', 'c').replace('ğ', 'g')\
               .replace('ı', 'i').replace('ö', 'o')\
               .replace('ş', 's').replace('ü', 'u')\
               .replace('â', 'a')
    # Further normalization using Unicode decomposition
    name = unicodedata.normalize('NFKD', name)
    name = ''.join([c for c in name if not unicodedata.combining(c)])
    return name

# Clean all SSP dataframes
for ssp, df in ssp_files.items():
    df.columns = df.columns.astype(str)
    df['Provinces'] = df['Provinces'].str.strip()
    # Add normalized column for matching (enhancement by Oguzhan Gulaydin)
    df['Normalized'] = df['Provinces'].apply(normalize_province)
    ssp_files[ssp] = df.drop_duplicates(subset='Provinces').dropna()

# Load and clean historical electricity data (enhancement by Oguzhan Gulaydin)
# This addition provides context by showing actual historical consumption alongside projections
hist_path = os.path.join(xlsx_dir, 'historical_electricity.xlsx')
hist_df = pd.read_excel(hist_path)
# Ensure year columns are strings and normalize province names
hist_df.columns = hist_df.columns.astype(str)
hist_df['Province'] = hist_df['Province'].str.strip()
hist_df['Normalized'] = hist_df['Province'].apply(normalize_province)
hist_df = hist_df.drop_duplicates(subset='Province').dropna()

# Load GeoJSON file containing Turkey province boundaries
with open(os.path.join(base_dir, 'geoBoundaries-TUR-ADM1_simplified.geojson'), 'r', encoding='utf-8') as f:
    turkey_geo = json.load(f)

# ============================================================================
# STREAMLIT APPLICATION LAYOUT
# ============================================================================

# Configure Streamlit page settings
st.set_page_config(layout="wide", page_title="Turkey Electricity Demand")

# Custom CSS for better layout
st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem;
        padding-right: 1rem;
        padding-left: 1rem;
        padding-bottom: 1rem;
    }
    /* Remove any borders or lines below the map */
    iframe {
        border: none !important;
    }
    div[data-testid="stIFrame"] {
        border: none !important;
        border-bottom: none !important;
    }
    /* Remove horizontal rules/dividers */
    hr {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# Application title
st.title("Projected Residential Electricity Demand in Turkey (2025–2050)")

# Usage instructions
with st.expander("📖 How to use this dashboard", expanded=False):
    st.markdown("""
    **Interactive Features:**

    1. **Select SSP scenario:** Choose from five Shared Socioeconomic Pathways (SSP1-SSP5) using the radio buttons below the map
       - SSP1: Sustainability – Sustainable development pathway with low challenges to mitigation and adaptation.
       - SSP2: Middle of the road - Moderate challanges.
       - SSP3: Regional rivalry – A fragmented world with high socio-political barriers to both mitigation and adaptation.
       - SSP4: Inequality – An unequal world where adaptation remains difficult despite relatively low mitigation barriers.
       - SSP5: Fossil-fuel-based development – Fossil-fuel-driven economic growth with high mitigation challenges but fewer adaptation difficulties.

    2. **Explore provincial data:** Click on any province on the map to view its specific electricity demand projections

    3. **View trends:** The charts on the left show:
       - **Top chart:** Total national residential electricity demand (historical and projected)
       - **Bottom chart:** Selected province's electricity demand (updates when you click a province)

    4. **Compare scenarios:** Different colored lines represent different SSP scenarios, with the selected scenario highlighted

    5. **Historical context:** White lines show historical data (2020-2023) for comparison with projections
    """)

# Create two-column layout: charts on left, map on right
col_charts, col_map = st.columns([0.3, 0.7])

# ============================================================================
# MAP VISUALIZATION
# ============================================================================

with col_map:
    # Initialize session state for selected province if not exists
    if 'selected_province' not in st.session_state:
        st.session_state.selected_province = "Ankara"
    # Store normalized version for matching (enhancement by Oguzhan Gulaydin)
    if 'selected_province_normalized' not in st.session_state:
        st.session_state.selected_province_normalized = normalize_province(st.session_state.selected_province)

    # Initialize selected SSP if not in session state
    if 'selected_ssp' not in st.session_state:
        st.session_state.selected_ssp = 'SSP1'

    # Get the selected SSP dataframe
    selected_ssp = st.session_state.selected_ssp
    df = ssp_files[selected_ssp]

    # Fixed year for map visualization
    selected_year = '2050'
    df['Demand'] = df[selected_year]

    # Create Folium map centered on Turkey
    m = folium.Map(location=[39.0, 35.0], zoom_start=6, tiles='CartoDB positron')

    # Add choropleth layer showing demand by province
    choropleth = folium.Choropleth(
        geo_data=turkey_geo,
        name='choropleth',
        data=df,
        columns=['Provinces', 'Demand'],
        key_on='feature.properties.shapeName',
        fill_color='OrRd',  # Orange-Red color scheme
        fill_opacity=0.7,
        line_opacity=0.4,
        line_color='black',
        nan_fill_color='white',
        # Updated legend title (fix by Oguzhan Gulaydin)
        legend_name=f'Residential electricity demand (GWh) in {selected_year} ({selected_ssp})'
    )
    choropleth.add_to(m)

    def style_function(feature):
        """Style function for province borders - highlights selected province."""
        name = feature['properties']['shapeName']
        return {
            'fillOpacity': 0,
            'color': 'black',
            'weight': 2 if name == st.session_state.selected_province else 0.6
        }

    def highlight_function(feature):
        """Highlight function for mouse hover effect."""
        return {
            'fillColor': 'lightblue',
            'fillOpacity': 0.5,
            'color': 'black',
            'weight': 2
        }

    # Add interactive province layer
    geojson = folium.GeoJson(
        turkey_geo,
        name='borders',
        style_function=style_function,
        highlight_function=highlight_function,
        # Fixed tooltip import (bug fix by Oguzhan Gulaydin)
        tooltip=folium.GeoJsonTooltip(fields=['shapeName'], aliases=['Province:'])
    )
    geojson.add_to(m)

    # Render the map using streamlit-folium
    selected = st_folium(m, height=550, use_container_width=True)

    # Handle province selection from map click
    if selected and selected.get("last_active_drawing"):
        selected_name_raw = selected['last_active_drawing']['properties']['shapeName']
        # Store normalized version for data lookup (enhancement by Oguzhan Gulaydin)
        selected_name_normalized = normalize_province(selected_name_raw)

        # Update session state if a new province is selected
        if selected_name_raw != st.session_state.selected_province:
            st.session_state.selected_province = selected_name_raw
            st.session_state.selected_province_normalized = selected_name_normalized
            st.rerun()

    # SSP scenario selector - centered below the map
    # Center the selector using columns as specified
    col_left, col_center, col_right = st.columns([0.1, 0.8, 0.1])
    with col_center:
        # Put label and radio buttons on same line
        label_col, radio_col = st.columns([0.3, 0.7])
        with label_col:
            st.markdown("<p style='text-align: right; margin-top: 0.25rem; color: #E0E0E0; font-size: 1rem;'>Select SSP scenario:</p>", unsafe_allow_html=True)
        with radio_col:
            selected_ssp_new = st.radio(
                " ",
                list(ssp_files.keys()),
                horizontal=True,
                index=list(ssp_files.keys()).index(selected_ssp),
                key="ssp_selector",
                label_visibility="collapsed"
            )

    # Update session state if SSP changed
    if selected_ssp_new != selected_ssp:
        st.session_state.selected_ssp = selected_ssp_new
        st.rerun()

# Add horizontal line and citation section at the bottom
st.markdown("<hr style='margin-top: 50px; margin-bottom: 20px; border: 1px solid #31333F;'>", unsafe_allow_html=True)

# Paper description and publication details
st.markdown("""
<div style='background-color: #1E1E1E; padding: 15px; border-radius: 5px; margin-bottom: 20px;'>
    <p style='color: #E0E0E0; margin: 0 0 10px 0; font-size: 0.95rem;'>This interactive dashboard accompanies the research article "<em>Machine learning for subnational residential electricity demand forecasting to 2050 under shared socioeconomic pathways: Comparing tree-based, neural and kernel methods</em>" published in <strong>Energy</strong> journal (Elsevier).</p>
    <p style='color: #B0B0B0; margin: 0 0 10px 0; font-size: 0.9rem;'>This study developed a novel ML approach integrating shared socioeconomic pathways (SSPs) for subnational electricity demand forecasting to 2050 using Turkey as a case study. The research also compared various machine learning algorithms for forecasting: Random Forest, XGBoost, FFNN, LSTM, SVR, and GPR. The projections presented in this dashboard are based on the <strong>Random Forest</strong> model, which demonstrated the best overall performance.</p>
</div>
""", unsafe_allow_html=True)

# Citation section
st.markdown("""
<div style='background-color: #0E1117; padding: 20px; text-align: left;'>
    <p style='color: #E0E0E0; margin: 0 0 10px 0; font-size: 1rem; '>Cite this work as: Gulaydin, O., Mourshed, M. (2025). Machine learning for subnational residential electricity demand forecasting to 2050 under shared socioeconomic pathways: Comparing tree-based, neural and kernel methods. <em>Energy</em>, 133837. DOI: <a href='https://doi.org/10.1016/j.energy.2024.133837' target='_blank' style='color: #4CAF50;'>10.1016/j.energy.2024.133837</a></p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# CHART VISUALIZATIONS
# ============================================================================

with col_charts:

    # --- National Total Demand Chart ---

    # Calculate national totals for all SSP scenarios (in TWh)
    national = pd.DataFrame({
        ssp: (
            ssp_files[ssp]
            .drop(['Provinces','Normalized','Demand'], axis=1, errors='ignore')
            .sum() / 1000  # Convert GWh to TWh
        )
        for ssp in ssp_files.keys()
    })

    # Calculate historical national totals (enhancement by Oguzhan Gulaydin)
    hist_national = (
        hist_df
        .drop(['Province','Normalized'], axis=1)
        .sum() / 1000  # Convert GWh to TWh
    ).drop('2024', errors='ignore')

    # Filter to show only 2020 onwards for cleaner visualization
    hist_national = hist_national[hist_national.index.astype(int) >= 2020]

    # Create national demand line chart
    fig_nat = px.line(
        title="Total residential demand in Turkey",
        labels={'index': 'Year', 'value': 'Demand (TWh)', 'variable': 'Scenario'}
    )

    # Define hover template for all traces with consistent alignment
    hover_template = '<b>%{fullData.name}</b><br>' + \
                     'Year = %{x}<br>' + \
                     'Demand = %{y:.2f} TWh' + \
                     '<extra></extra>'

    # Add historical data trace (enhancement by Oguzhan Gulaydin)
    fig_nat.add_scatter(
        x=hist_national.index.astype(int),
        y=hist_national.values,
        mode='lines',
        name='Historical',
        line=dict(color='white', dash='solid', width=2),  # White color for visibility
        opacity=1.0,
        hovertemplate=hover_template
    )

    # Add selected SSP scenario (highlighted in red)
    fig_nat.add_scatter(
        x=national.index.astype(int),
        y=national[selected_ssp],
        mode='lines',
        name=selected_ssp,
        line=dict(color='red', dash='solid'),
        opacity=1.0,
        hovertemplate=hover_template
    )

    # Add other SSP scenarios (in muted colors with dotted lines)
    colors = ['gray','blue','green','orange','purple']
    for i, ssp in enumerate([s for s in national.columns if s != selected_ssp]):
        fig_nat.add_scatter(
            x=national.index.astype(int),
            y=national[ssp],
            mode='lines',
            name=ssp,
            line=dict(color=colors[i], dash='dot'),
            opacity=0.6,
            hovertemplate=hover_template
        )

    # Ensure consistent hover label alignment for all traces
    fig_nat.update_traces(hoverlabel=dict(align='left'))

    # Update layout with improved styling (enhancements by Oguzhan Gulaydin)
    fig_nat.update_layout(
        height=300,
        margin=dict(t=30),
        # Horizontal legend below chart with more spacing
        legend=dict(
            orientation="h",
            x=0.5,
            y=-0.35,  # Moved up to create more space from x-axis
            xanchor="center",
            yanchor="top",  # Changed anchor point
            title_text="",
            entrywidthmode="fraction",
            entrywidth=0.3,
            font=dict(color='#E0E0E0')  # Light gray legend text
        ),
        title=dict(font=dict(color='#E0E0E0')),  # Light title
        xaxis_title='Year',
        yaxis_title='Electricity (TWh)',  # Corrected unit label
        plot_bgcolor='#0E1117',  # Dark background matching Streamlit theme
        paper_bgcolor='#0E1117',  # Dark background matching Streamlit theme
        # Enhanced axis styling with grid and ticks (by Oguzhan Gulaydin)
        xaxis=dict(
            title=dict(text='Year', font=dict(color='#E0E0E0')),  # Light gray text
            tickfont=dict(color='#E0E0E0'),  # Light gray tick labels
            showline=True, linecolor='#31333F', linewidth=1,  # Subtle line
            showgrid=True, gridcolor='#31333F', gridwidth=0.5,  # Subtle grid
            ticks='outside', tickcolor='#31333F', ticklen=5, tickwidth=1,
            zeroline=True, zerolinecolor='#31333F', zerolinewidth=1
        ),
        yaxis=dict(
            title=dict(text='Electricity (TWh)', font=dict(color='#E0E0E0')),  # Light gray text
            tickfont=dict(color='#E0E0E0'),  # Light gray tick labels
            showline=True, linecolor='#31333F', linewidth=1,  # Subtle line
            showgrid=True, gridcolor='#31333F', gridwidth=0.5,  # Subtle grid
            ticks='outside', tickcolor='#31333F', ticklen=5, tickwidth=1,
            zeroline=True, zerolinecolor='#31333F', zerolinewidth=1
        )
    )
    fig_nat.update_xaxes(tickmode='linear', tick0=2020, dtick=5)
    st.plotly_chart(fig_nat, use_container_width=True)

    # --- Province-Level Demand Chart ---

    # Use normalized name for data lookup (bug fix by Oguzhan Gulaydin)
    norm_name = st.session_state.selected_province_normalized

    # Get historical data for selected province (2020-2023)
    prov_hist = (
        hist_df
        .set_index('Normalized')
        .loc[norm_name]
        .drop(['Province'], errors='ignore')
        .drop('2024', errors='ignore')
        .astype(float)
    )
    # Convert index to integer years and filter
    prov_hist.index = prov_hist.index.astype(int)
    prov_hist = prov_hist[prov_hist.index >= 2020]

    # Get SSP projections for selected province (2025-2050)
    ssp_list = []
    for ssp in ssp_files:
        s = (
            ssp_files[ssp]
            .set_index('Normalized')
            .loc[norm_name]
            .drop(['Provinces','Normalized','Demand'], errors='ignore')
            .astype(float)
        )
        s.index = s.index.astype(int)
        s = s[s.index >= 2025]
        s.name = ssp
        ssp_list.append(s)

    # Combine historical and projected data
    prov_hist.name = 'Historical'
    prov_df = pd.concat([prov_hist] + ssp_list, axis=1)

    # Determine appropriate unit based on demand magnitude
    # If minimum demand exceeds 1000 GWh, convert to TWh for readability
    min_demand = prov_df.min().min()

    if min_demand > 1000:  # Threshold for switching to TWh
        # Convert to TWh
        prov_df_display = prov_df / 1000
        y_unit = 'TWh'
        y_label = 'Electricity (TWh)'
        demand_label = 'Demand (TWh)'
    else:
        # Keep in GWh
        prov_df_display = prov_df
        y_unit = 'GWh'
        y_label = 'Electricity (GWh)'
        demand_label = 'Demand (GWh)'

    # Define consistent color scheme
    color_map = {
        'Historical': 'white',  # White for visibility on dark background
        'SSP1': 'red',
        'SSP2': 'blue',
        'SSP3': 'green',
        'SSP4': 'orange',
        'SSP5': 'purple',
    }

    # Create province-level demand chart with dynamic units
    fig_prov = px.line(
        prov_df_display,
        title=f"Demand in {st.session_state.selected_province}",
        color_discrete_map=color_map,
        labels={'index': 'Year', 'value': demand_label, 'variable': 'Scenario'}
    )

    # Customize hover template with spacing and ensure consistent alignment
    fig_prov.update_traces(
        hovertemplate='<b>%{fullData.name}</b><br>' +
                      'Year = %{x}<br>' +
                      f'Demand = %{{y:.2f}} {y_unit}' +
                      '<extra></extra>',
        hoverlabel=dict(align='left')
    )

    # Make historical trace more prominent
    # Update the first trace (Historical) to have a solid white line
    fig_prov.update_traces(
        line=dict(color='white', width=2),
        selector=dict(name='Historical')
    )

    # Apply consistent styling with national chart
    fig_prov.update_layout(
        height=300,
        margin=dict(t=30),
        # Horizontal legend below chart with more spacing
        legend=dict(
            orientation="h",
            x=0.5,
            y=-0.35,  # Moved up to create more space from x-axis
            xanchor="center",
            yanchor="top",  # Changed anchor point
            title_text="",
            entrywidthmode="fraction",
            entrywidth=0.3,
            font=dict(color='#E0E0E0')  # Light gray legend text
        ),
        title=dict(font=dict(color='#E0E0E0')),  # Light title
        xaxis_title='Year',
        yaxis_title=y_label,  # Dynamic unit based on demand magnitude
        plot_bgcolor='#0E1117',  # Dark background matching Streamlit theme
        paper_bgcolor='#0E1117',  # Dark background matching Streamlit theme
        # Enhanced axis styling (by Oguzhan Gulaydin)
        xaxis=dict(
            showline=True, linecolor='#31333F', linewidth=1,  # Subtle line
            title=dict(text='Year', font=dict(color='#E0E0E0')),  # Light gray text
            tickfont=dict(color='#E0E0E0'),  # Light gray tick labels
            showgrid=True, gridcolor='#31333F', gridwidth=0.5,  # Subtle grid
            ticks='outside', tickcolor='#31333F', ticklen=5, tickwidth=1,
            zeroline=True, zerolinecolor='#31333F', zerolinewidth=1
        ),
        yaxis=dict(
            title=dict(text=y_label, font=dict(color='#E0E0E0')),  # Dynamic unit with light gray text
            tickfont=dict(color='#E0E0E0'),  # Light gray tick labels
            showline=True, linecolor='#31333F', linewidth=1,  # Subtle line
            showgrid=True, gridcolor='#31333F', gridwidth=0.5,  # Subtle grid
            ticks='outside', tickcolor='#31333F', ticklen=5, tickwidth=1,
            zeroline=True, zerolinecolor='#31333F', zerolinewidth=1
        )
    )
    fig_prov.update_xaxes(tickmode='linear', tick0=2025, dtick=5)
    st.plotly_chart(fig_prov, use_container_width=True)