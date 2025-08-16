from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
from pathlib import Path
from employment_flask_app.dash_app.filter_data_functions import (
    highest_m_year_disparity_percentage,
    highest_m_year_disparity_occupation,
    highest_m_year_disparity_region,
    highest_f_year_disparity_percentage,
    highest_f_year_disparity_occupation,
    highest_f_year_disparity_region,
    highest_overall_disparity_percentage,
    highest_overall_disparity_occupation,
    highest_overall_disparity_region,
    highest_overall_disparity_gender,
)


# Helper function to get metric style for statistics card
def get_metric_style(value):
    """
    Return color and icon based on value positivity.

    Parameters
    ----------
    value : int or float
        The value to evaluate.

    Returns
    -------
    dict
        A dictionary containing the color and icon. If the value is
        greater than or equal to 0, the color is "success" and the icon
        is "bi-arrow-up". Otherwise, the color is "danger" and the icon
        is "bi-arrow-down".
    """
    """Return color and icon based on value positivity"""
    if value >= 0:
        return {"color": "success", "icon": "bi-arrow-up"}
    return {"color": "danger", "icon": "bi-arrow-down"}


# Create dataframe
data_path = Path(__file__).parent.parent / "data" / "employment_prepared.xlsx"
df = pd.read_excel(data_path)

# Navigation bar
navigation_bar = dbc.NavbarSimple(
    children=[
        dbc.DropdownMenu(
            children=[],
            nav=True,
            in_navbar=True,
            label="Saved Analyses",
            id="saved-analyses-menu",
        ),
    ],
    brand="Comparative Employment Analysis Tool",
    brand_style={"font-weight": "bold"},
    color="#4292C3",
    dark=True,
    style={"margin-bottom": "20px"},
)

# ------ Components for the filters and buttons row ------
# Dataset button -----------------------------------------
#  Dataset button
dataset_button = dbc.Button(
    "Dataset", id="data-attribution-button",
    className="custom-button", n_clicks=0
)
#  Dataset button tooltip
dataset_tooltip = dbc.Tooltip(
    "View dataset attribution",
    id="dataset-tooltip",
    target="data-attribution-button",
    placement="bottom",
    className="custom-tooltip",
)
#  Dataset offcanvas
dataset_offcanvas = dbc.Offcanvas(
    children=[
        html.Div(
            [
                html.P(
                    "The data used in this analysis is sourced from "
                    "the Greater London Authority, under the "
                    "Open Government Licence v2.0."
                ),
                html.P(
                    [
                        "Please refer to ",
                        html.A(
                            "this website",
                            href=(
                                "https://data.london.gov.uk/dataset/"
                                "employment-occupation-type-and-gender-borough"
                            ),
                            target="_blank",
                        ),
                        " for more information.",
                    ]
                ),
            ]
        ),
    ],
    id="data-attribution-canvas",
    scrollable=True,
    title="Dataset Attribution",
    is_open=False,
)
#  Dataset attribution components
data_attribution = html.Div(
    [
        dataset_button,
        dataset_tooltip,
        dataset_offcanvas,
    ]
)

# Region dropdown ----------------------------------------
region_dropdown = dcc.Dropdown(
    options=["England", "Wales", "Scotland", "Northern Ireland"],
    value=None,
    id="region-dropdown",
    placeholder="Select a region",
    className="custom-dropdown",
)

# Year dropdown ------------------------------------------
year_dropdown = dcc.Dropdown(
    options=["2021", "2022", "2023"],
    value=None,
    id="year-dropdown",
    placeholder="Select a year",
    className="custom-dropdown",
)

# Occupation type slider ---------------------------------
#   Marks for the occupation type slider
occupation_marks = {i: str(i) for i in range(1, 10)}

#   Full descriptions for occupation types
full_descriptions = {
    1: "Managers, directors and senior officials",
    2: "Professional occupations",
    3: "Associate prof & tech occupations",
    4: "Administrative and secretarial occupations",
    5: "Skilled trades occupations",
    6: "Caring, leisure and other service occupations",
    7: "Sales and customer service occupations",
    8: "Process, plant and machine operatives",
    9: "Elementary occupations",
}

#   Occupation type slider
occupation_type_slider = html.Div(
    [
        html.Div(
            [
                dbc.Label("Occupation Types", id="occupation-type-label"),
                dbc.Tooltip(
                    "Slide to select an occupation type",
                    target="occupation-type-label",
                    placement="top",
                ),
            ],
            style={
                "display": "flex",
                "justifyContent": "center",
                "marginBottom": "8px",
            },
        ),
        dcc.Slider(
            min=1,
            max=9,
            step=1,
            marks=occupation_marks,
            value=1,
            id="occupation-type-slider",
            tooltip={
                "placement": "bottom",
                "always_visible": True,
                "template": "{full_description}",
            },
            included=False,
        ),
    ],
    style={"display": "flex", "flexDirection": "column"},
)

# Analysis name input group -------------------------------
analysis_name_input = dbc.InputGroup(
    [
        dbc.InputGroupText("Save analysis as"),
        dbc.Input(placeholder="Enter name", id="analysis-name-input"),
    ],
    className="custom-input-group",
)

# Save filters button -------------------------------------
save_filters_button = html.Button(
    "Save", className="custom-button", id="save-filters-button", n_clicks=0
)
#  Save filters button tooltip
save_filters_tooltip = dbc.Tooltip(
    "Save the current filters",
    target="save-filters-button",
    placement="bottom",
    className="custom-tooltip",
)
#  Save filters alert message
save_filters_alert_message = dbc.Alert(
    id="save-alert",
    color="danger",
    dismissable=True,
    is_open=False,
)

# Clear button -------------------------------------------
clear_button = html.Button(
    "Clear", className="custom-button", id="clear-button", n_clicks=0
)
#  Clear button tooltip
clear_button_tooltip = dbc.Tooltip(
    "Clear all filters",
    target="clear-button",
    placement="bottom",
    className="custom-tooltip",
)

# ------ Components for the summary statistics row ------
#   Display summary statistics button
display_summary_button = html.Button(
    "Summary Statistics",
    className="custom-button",
    id="display-summary-button",
    n_clicks=0,
    style={"display": "none", "width": "100%"},
)
#  Display summary tooltip
display_summary_tooltip = dbc.Tooltip(
    "Summarise gender and occupation statistics",
    target="display-summary-button",
    placement="top",
    className="custom-tooltip",
    id="display-summary-tooltip",
)

#  Summmary gender disparity statistics card
#  1.  Header
main_gen_disp_header = dbc.CardHeader(
    html.H4(
                [
                    html.I(className="bi bi-gender-female me-2"),
                    html.I(className="bi bi-gender-male me-2"),
                    "Gender Disparity Analysis",
                ],
                className="text-center text-white",
            ), className="custom-stats-border"
        )

#  2.  Occupation type disparity
#      2.1 Header
disp_occ_type_header = dbc.CardHeader(
    html.H5(
                [
                    "Greatest Overall Disparity for ",
                    html.Span(
                        id="selected-occupation-type"
                    ),
                ],
                className="mb-0",
            ), className="bg-light"
        )

#      2.2 Highest disparity card
#        2.2.1 Highest disparity region
high_disp_region = html.Div(
    [
        html.I(
            className=(
                "bi bi-geo-alt-fill text-muted me-2"
            )
        ),
        html.Span(
            "Region:",
            className="text-muted",
        ),
        html.Span(
            id="highest-disparity-region",
            className="h5 ms-2",
        ),
    ],
    className=(
        "d-flex align-items-center mb-3"
    ),
)
#        2.2.2 Highest disparity percentage
high_disp_perc = html.Div(
    [
        html.I(
            className=(
                "bi bi-bar-chart-line-fill me-2"
            )
        ),
        html.Span(
            "Disparity:",
            className="text-muted",
        ),
        html.Span(
            id=(
                "highest-disparity-percentage"
            ),
            className="h2 ms-2",
        ),
    ],
    className=(
        "d-flex align-items-center"
    ),
)
#        2.2.3 Highest disparity card
high_disp_card = dbc.Card(
    [
        disp_occ_type_header,
        dbc.CardBody(
            [
                high_disp_region,
                high_disp_perc,
            ],
            className=(
                "border-start border-danger border-4 p-3"
            ),
        ),
    ],
    className="shadow-lg h-100",
)

#    2.3 Occupation breakdown card
#      2.3.1 Header
occ_breakdown_header = dbc.CardHeader(
    html.H5(
        [
            "Occupation Breakdown for ",
            html.Span(
                id="gen-selected-region"
            ),
            " in ",
            html.Span(
                id="gen-selected-year"
            ),
        ],
        className="mb-0",
    ),
    className="bg-light",
)
#     2.3.2 Highest disparity occupation
high_disp_occ = html.Div(
    [
        html.I(
            className=(
                "bi bi-briefcase text-muted me-2"
            )
        ),
        html.Span(
            "Occupation:",
            className="text-muted",
        ),
        html.Span(
            id=(
                "highest-disparity-occupation"
            ),
            className="h5 ms-2",
        ),
    ],
    className=(
        "d-flex align-items-center mb-3"
    ),
)
#    2.3.3 Highest disparity occupation percentage
high_occ_perc = html.Div(
    [
        html.I(
            className=(
                "bi bi-percent text-muted me-2"
            )
        ),
        html.Span(
            "Disparity:",
            className="text-muted",
        ),
        html.Span(
            id=(
                "highest-disparity-occupation-percentage"
            ),
            className="h2 ms-2",
        ),
    ],
    className=(
        "d-flex align-items-center"
    ),
)
#   2.4 Final gender disparity statistics card
gender_disparity_stats = dbc.Card(
    [
        main_gen_disp_header,
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            high_disp_card,
                            md=6,
                        ),
                        dbc.Col(
                            dbc.Card(
                                [
                                    occ_breakdown_header,
                                    dbc.CardBody(
                                        [
                                            high_disp_occ,
                                            high_occ_perc
                                        ],
                                        className="custom-male-border",
                                    ),
                                ],
                                className="shadow-lg h-100",
                            ),
                            md=6,
                        ),
                    ],
                    className="g-4",
                )
            ],
            className="p-4",
        ),
    ],
    className="my-4 shadow-lg",
)

# 3. Occupation statistics card
#    3.1 Occupation statistics header
occ_stats_header = dbc.CardHeader(
    html.H4(
        [html.I(className="bi bi-briefcase me-2"), "Occupation Statistics"],
        className="text-center text-white",
    ),
    className="custom-stats-border",
)
#   3.2 Employment change section
#     3.2.1 Employment change header
emp_change_header = html.H5(
    [
        html.I(className="bi bi-activity me-2"),
        "Greatest % Change in Employment (2021-2023)",
    ],
    className="custom-header-style",
)

#    3.2.2 Highest overall disparity card
#    3.2.2.1 Highest overall disparity header
high_overall_disp_header = dbc.CardHeader(
    html.H6(
        [
            html.I(className="bi bi-globe me-2"),
            "Overall",
        ],
        className="mb-0 text-white",
    ),
    className="bg-warning",
)
#    3.2.2.2 Highest overall disparity occupation
high_overall_disp_occ = html.Div(
    [
        html.I(
            className="bi bi-briefcase me-2 text-muted"
        ),
        html.Span(
            f"Occupation: {highest_overall_disparity_occupation}",
            className="text-muted",
        ),
    ],
    className="d-flex align-items-center mb-2",
)
#    3.2.2.3 Highest overall disparity gender
high_overall_disp_gender = html.Div(
    [
        html.I(
            className="bi bi-gender-ambiguous me-2 text-muted"
        ),
        html.Span(
            f"Gender: {highest_overall_disparity_gender}"
        ),
    ],
    className="d-flex align-items-center mb-2",
)
#    3.2.2.4 Highest overall disparity region
high_overall_disp_region = html.Div(
    [
        html.I(
            className="bi bi-geo me-2 text-muted"
        ),
        html.Span(
            f"Region: {highest_overall_disparity_region}"
        ),
    ],
    className="d-flex align-items-center",
)
#    3.2.2.5 Highest overall disparity percentage
high_overall_disp_perc = html.Div(
    [
        html.I(
            className=f"bi {
                get_metric_style(float(highest_overall_disparity_percentage)
                                 )['icon']} me-2"
        ),
        html.Span(
            f"{highest_overall_disparity_percentage}%",
            className=f"h4 text-{
                get_metric_style(float(highest_overall_disparity_percentage)
                                 )['color']}",
        ),
    ],
    className="d-flex align-items-center mb-2",
)
#    3.2.2.6 Highest overall change card
high_overall_change_card = dbc.Col(
    dbc.Card(
        [
            high_overall_disp_header,
            dbc.CardBody(
                [
                    high_overall_disp_occ,
                    high_overall_disp_gender,
                    high_overall_disp_region,
                    high_overall_disp_perc,
                ],
                className="border-start border-purple border-4 p-3",
            ),
        ],
        className="shadow-lg h-100",
    ),
    md=4,
)

#    3.2.3 Highest male change card
#    3.2.3.1 Highest male change card header
high_male_change_header = dbc.CardHeader(
    html.H6(
        [
            html.I(
                className="bi bi-gender-male me-2"
            ),
            "Male",
        ],
        className="mb-0 text-white",
    ),
    style={"backgroundColor": "#4291C3"},
)
#    3.2.3.2 Highest male change disparity occupation
high_m_year_disp_occ = html.Div(
    [
        html.I(
            className="bi bi-briefcase me-2 text-muted"
        ),
        html.Span(
            f"Occupation: {highest_m_year_disparity_occupation}",
            className="text-muted",
        ),
    ],
    className="d-flex align-items-center mb-2",
)
#    3.2.3.3 Highest male change disparity region
high_m_year_disp_region = html.Div(
    [
        html.I(
            className="bi bi-geo me-2 text-muted"
        ),
        html.Span(
            f"Region: {highest_m_year_disparity_region}",
            className="text-muted",
        ),
    ],
    className="d-flex align-items-center mb-2",
)
#    3.2.3.4 Highest male change disparity percentage
high_m_year_disp_perc = html.Div(
    [
        html.I(
            className=(
                f"bi {get_metric_style(float(
                    highest_m_year_disparity_percentage))['icon']} me-2"
            )
        ),
        html.Span(
            f"{highest_m_year_disparity_percentage}%",
            className=(
                f"h4 text-{get_metric_style(float(
                    highest_m_year_disparity_percentage))['color']}"
            ),
        ),
    ],
    className="d-flex align-items-center",
)
#    3.2.3.5 Highest male change card
highest_male_change_card = dbc.Col(
    dbc.Card(
        [
            high_male_change_header,
            dbc.CardBody(
                [
                    high_m_year_disp_occ,
                    high_m_year_disp_region,
                    high_m_year_disp_perc,
                ],
                className="custom-male-border",
            ),
        ],
        className="shadow-lg h-100",
        style={"marginBottom": "15px"},
    ),
    md=4,
)

#    3.2.4 Highest female change card
#    3.2.4.1 Highest female change card header
high_female_change_header = dbc.CardHeader(
    html.H6(
        [
            html.I(
                className="bi bi-gender-female me-2"
            ),
            "Female",
        ],
        className="mb-0 text-white",
    ),
    style={"backgroundColor": "#D6604D"},
)
#    3.2.4.2 Highest female change disparity occupation
high_f_year_disp_occ = html.Div(
    [
        html.I(
            className="bi bi-briefcase me-2 text-muted"
        ),
        html.Span(
            f"Occupation: {highest_f_year_disparity_occupation}",
            className="text-muted",
        ),
    ],
    className="d-flex align-items-center mb-2",
)
#    3.2.4.3 Highest female change disparity region
high_f_year_disp_region = html.Div(
    [
        html.I(
            className="bi bi-geo me-2 text-muted"
        ),
        html.Span(
            f"Region: {highest_f_year_disparity_region}",
            className="text-muted",
        ),
    ],
    className="d-flex align-items-center mb-2",
)
#    3.2.4.4 Highest female change disparity percentage
high_f_year_disp_perc = html.Div(
    [
        html.I(
            className=(
                f"bi {get_metric_style(float(
                    highest_f_year_disparity_percentage))['icon']} me-2"
            )
        ),
        html.Span(
            f"{highest_f_year_disparity_percentage}%",
            className=f"h4 text-{get_metric_style(float(
                highest_f_year_disparity_percentage))['color']}",
        ),
    ],
    className="d-flex align-items-center",
)
#    3.2.4.5 Highest female change card
highest_female_change_card = dbc.Col(
    dbc.Card(
        [
            high_female_change_header,
            dbc.CardBody(
                [
                    high_f_year_disp_occ,
                    high_f_year_disp_region,
                    high_f_year_disp_perc,
                ],
                className="custom-female-border",
            ),
        ],
        className="shadow-lg h-100",
    ),
    md=4,
)

#  3.3 Occupation location divider
occ_loc_divider = html.Div(
    [
        html.I(className="bi bi-geo-alt me-2"),
        html.P(
            [
                "For ",
                html.Span(
                    id="occ-selected-region", className="fw-bold"
                ),
                " in ",
                html.Span(id="occ-selected-year", className="fw-bold"),
            ]
        ),
    ],
    className="custom-location-header-style",
    id="occ-location-header",
)

#  3.4 Highest employment section
#    3.4.1 Highest employment header
high_emp_header = html.H5(
    [
        html.I(className="bi bi-trophy me-2"),
        "Highest Employment Percentage (%)",
    ],
    className="custom-header-style",
)
#    3.4.2 Highest employment header
high_emp_overall_header = dbc.CardHeader(
    html.H6(
        [
            html.I(
                className="bi bi-star-fill me-2"
            ),
            "Overall",
        ],
        className="mb-0 text-white",
    ),
    className="bg-warning",
)
#    3.4.3 Highest employment occupation
high_emp_occ = html.Div(
    [
        html.I(
            className="bi bi-briefcase me-2 text-muted"
        ),
        html.Span(
            id="highest-employment-occupation",
            className="h6",
        ),
    ],
    className="d-flex align-items-center mb-3",
)
#    3.4.3 Highest employment occupation percentage
high_emp_occ_perc = html.Div(
    [
        html.I(
            className=(
                "bi bi-percent me-2 text-warning"
            )
        ),
        html.Span(
            id="highest-employment-percentage",
            className="h2 fw-bold",
        ),
    ],
    className="d-flex align-items-center",
)

#    3.4.4 Highest employment occupation card
high_emp_occ_card = dbc.Card(
    [
        high_emp_overall_header,
        dbc.CardBody(
            [
                high_emp_occ,
                high_emp_occ_perc,
            ],
            className="border-start border-warning border-4",
        ),
    ],
    className="shadow-lg h-100",
)
#    3.4.5 Highest male employment header
high_emp_male_header = dbc.CardHeader(
    html.H6(
        [
            html.I(
                className="bi bi-gender-male me-2"
            ),
            "Male",
        ],
        className="mb-0 text-white",
    ),
    style={"backgroundColor": "#4291C3"},
)
#    3.4.6 Highest male employment occupation
high_emp_male_occ = html.P(
    [
        html.I(
            className="bi bi-briefcase me-2 text-muted"
        ),
        html.Span(
            id="highest-male-employment-occupation"
        ),
    ],
    className="text-truncate mb-2",
)
#    3.4.7 Highest male employment occupation percentage
high_emp_male_occ_perc = html.Div(
    [
        html.I(
            className="bi bi-percent text-success"
        ),
        html.Span(
            id="highest-male-employment-percentage",
            className="h4 text-success ms-2",
        ),
    ],
    className="d-flex align-items-center",
)
#    3.4.8 Highest male employment card
high_emp_male_card = dbc.Card(
    [
        high_emp_male_header,
        dbc.CardBody(
            [
                high_emp_male_occ,
                high_emp_male_occ_perc,
            ],
            className="custom-male-border",
        ),
    ],
    className="shadow-sm h-100",
)

#    3.4.9 Highest female employment header
high_emp_female_header = dbc.CardHeader(
    html.H6(
        [
            html.I(
                className="bi bi-gender-female me-2"
            ),
            "Female",
        ],
        className="mb-0 text-white",
    ),
    style={"backgroundColor": "#D6604D"},
)
#    3.4.10 Highest female employment occupation
high_emp_female_occ = html.P(
    [
        html.I(
            className="bi bi-briefcase me-2 text-muted"
        ),
        html.Span(
            id="highest-female-employment-occupation"
        ),
    ],
    className="text-truncate mb-2",
)
#    3.4.11 Highest female employment occupation percentage
high_emp_female_occ_perc = html.Div(
    [
        html.I(
            className="bi bi-percent text-success"
        ),
        html.Span(
            id="highest-female-employment-percentage",
            className="h4 text-success ms-2",
        ),
    ],
    className="d-flex align-items-center",
)
#    3.4.12 Highest female employment card
high_emp_female_card = dbc.Card(
    [
        high_emp_female_header,
        dbc.CardBody(
            [
                high_emp_female_occ,
                high_emp_female_occ_perc
            ],
            className="custom-female-border",
        ),
    ],
    className="shadow-sm h-100",
)

occupation_stats = dbc.Card(
    [
        occ_stats_header,
        dbc.CardBody(
            [
                emp_change_header,
                dbc.Row(
                    [
                        high_overall_change_card,
                        highest_male_change_card,
                        highest_female_change_card,
                    ],
                    className="g-4",
                    style={"marginBottom": "15px"},
                ),
                occ_loc_divider,
                high_emp_header,
                dbc.Row(
                    [
                        dbc.Col(
                            high_emp_occ_card,
                            md=4,
                        ),
                        dbc.Col(
                            high_emp_male_card,
                            md=4,
                        ),
                        dbc.Col(
                            high_emp_female_card,
                            md=4,
                        ),
                    ],
                    className="g-4 mb-5",
                ),
            ],
            className="p-4",
        ),
    ],
    className="my-4 shadow-lg",
)

#  Summary statistics collapse
summary_stats_collapse = dbc.Collapse(
    dcc.Tabs(
        children=[
            dcc.Tab(
                label="Gender Disparity Statistics",
                children=[gender_disparity_stats],
                id="gender-disparity-tab",
            ),
            dcc.Tab(
                label="Occupation Statistics",
                children=[occupation_stats],
                id="occupation-stats-tab",
            ),
        ],
        className="tab-container",
        parent_className="custom-tabs",
        parent_style={"margin": "0"},
    ),
    id="summary-stats",
    is_open=False,
)

#  Summary statistics container
summary_stats = html.Div(
    [
        display_summary_button,
        display_summary_tooltip,
        summary_stats_collapse,
    ],
    className="shadow tab-content",
    id="summary-stats-container",
)
