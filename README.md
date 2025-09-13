# Turkey Residential Electricity Demand Dashboard (2025-2050)

An interactive Streamlit dashboard visualizing residential electricity demand projections for Turkey based on Shared Socioeconomic Pathways (SSP) scenarios using machine learning predictions.

## About

This dashboard accompanies the research article "*Machine learning for subnational residential electricity demand forecasting to 2050 under shared socioeconomic pathways: Comparing tree-based, neural and kernel methods*" published in **Energy** journal (Elsevier).

The study compared various machine learning algorithms (Random Forest, XGBoost, FFNN, LSTM, SVR, GPR) for forecasting residential electricity demand. The projections presented in this dashboard are based on the **Random Forest** model, which demonstrated the best overall performance.

**📖 Paper:** https://doi.org/10.1016/j.energy.2024.133837

## Features

- **Interactive Map**: Click on any Turkish province to view specific projections
- **Scenario Comparison**: Compare 5 different SSP scenarios (SSP1-SSP5)
- **Historical Context**: View historical data (2020-2023) alongside projections
- **Dynamic Units**: Automatically switches between GWh and TWh based on demand magnitude
- **Responsive Charts**: National and provincial-level demand visualization

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/turkey-electricity-demand-dashboard.git
   cd turkey-electricity-demand-dashboard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the dashboard**
   ```bash
   streamlit run app.py
   ```

4. **Open in browser**
   - The dashboard will automatically open at `http://localhost:8501`
   - If it doesn't open automatically, navigate to the URL shown in the terminal

## How to Use

1. **Select SSP Scenario**: Choose from five Shared Socioeconomic Pathways using the radio buttons below the map
2. **Explore Provincial Data**: Click on any province on the map to view its specific projections
3. **Compare Scenarios**: View different colored lines representing different SSP scenarios
4. **Historical Context**: White lines show historical data (2020-2023) for comparison

### SSP Scenarios Explained

- **SSP1**: Sustainability – Sustainable development pathway with low challenges to mitigation and adaptation
- **SSP2**: Middle of the road – Moderate challenges
- **SSP3**: Regional rivalry – A fragmented world with high socio-political barriers
- **SSP4**: Inequality – An unequal world where adaptation remains difficult
- **SSP5**: Fossil-fuel-based development – Fossil-fuel-driven economic growth

## 📁 Project Structure

```
turkey-electricity-demand-dashboard/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                      # This file
├── .gitignore                     # Git ignore rules
└── data/                          # Data files
    ├── geoBoundaries-TUR-ADM1_simplified.geojson  # Province boundaries
    └── xlsx/                      # Excel data files
        ├── SSP1.xlsx              # SSP1 scenario projections
        ├── SSP2.xlsx              # SSP2 scenario projections
        ├── SSP3.xlsx              # SSP3 scenario projections
        ├── SSP4.xlsx              # SSP4 scenario projections
        ├── SSP5.xlsx              # SSP5 scenario projections
        └── historical_electricity.xlsx  # Historical data (2020-2023)
```

## Technical Details

- **Frontend**: Streamlit
- **Mapping**: Folium with streamlit-folium
- **Visualization**: Plotly Express
- **Data Processing**: Pandas
- **Geospatial**: GeoJSON for province boundaries

## Data Sources

- **Projections**: Machine learning models trained on historical data and SSP scenarios
- **Historical Data**: Turkish residential electricity consumption (2020-2023)
- **Geographic Data**: Turkish province boundaries (simplified)

## Dashboard author

- **Mounjur Mourshed** (mourshedm@cardiff.ac.uk, monjur@mourshed.org) - Original Framework
- **Oguzhan Gulaydin** (GulaydinO@cardiff.ac.uk) - Bug fixes, feature enhancements

## Citation

If you use this dashboard or the associated research in your work, please cite:

```bibtex
@article{gulaydin2025machine,
  title={Machine learning for subnational residential electricity demand forecasting to 2050 under shared socioeconomic pathways: Comparing tree-based, neural and kernel methods},
  author={Gulaydin, Oguzhan and Mourshed, Mounjur},
  journal={Energy},
  pages={133837},
  year={2025},
  publisher={Elsevier},
  doi={10.1016/j.energy.2024.133837}
}
```

## License

This project is licensed under the MIT License - see the paper for full academic license details.

## Issues

If you encounter any problems:

1. Ensure all dependencies are installed correctly
2. Check that the `data/` folder contains all required files
3. Verify Python version compatibility (3.8+)
4. Contact the authors if issues persist

## Links

- **Paper**: https://doi.org/10.1016/j.energy.2024.133837
- **Journal**: Energy (Elsevier)
- **Institution**: Cardiff University

---

*This dashboard provides supplementary material for the research article published in Energy journal. The projections are based on the Random Forest machine learning model and should be interpreted within the context of the study's methodology and limitations.*
