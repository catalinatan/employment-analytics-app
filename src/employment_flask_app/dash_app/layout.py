from dash import dcc
import dash_bootstrap_components as dbc
from employment_flask_app.dash_app.components import (
    navigation_bar,
    region_dropdown,
    year_dropdown,
    occupation_type_slider,
    clear_button,
    clear_button_tooltip,
    save_filters_button,
    save_filters_tooltip,
    save_filters_alert_message,
    analysis_name_input,
    data_attribution,
    summary_stats,
)

# Define the rows of the app
filters_buttons_row = dbc.Row(
    [
        # Data attribution column
        dbc.Col(data_attribution, width="1", className="ms-2"),
        dbc.Col(
            [
                # Dropdowns and input row
                dbc.Row(
                    [
                        # Region dropdown
                        dbc.Col(region_dropdown, width="3"),
                        # Year dropdown
                        dbc.Col(year_dropdown, width="3"),
                        # Analysis name input
                        dbc.Col(analysis_name_input, width="4"),
                        # Save filters button group
                        dbc.Col(
                            [
                                save_filters_button,
                                save_filters_tooltip,
                                save_filters_alert_message,
                            ],
                            width="auto",
                        ),
                    ],
                    justify="center",
                    align="items-center",
                    className="g-2",
                )
            ],
            width={"size": "8", "offset": 0.5},
        ),
        # Clear button group
        dbc.Col(
            [clear_button, clear_button_tooltip],
            width="auto",
            className="me-2",
        ),
    ],
    justify="between",
    align="items-center",
    className="g-0",
)

# Define the row for bar and pie charts
bar_pie_chart_row = dbc.Row(
    [
        # Bar chart card
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    dcc.Loading(id="bar-chart-card-content"),
                    id="bar-chart-card-body"
                ),
                className="chart-card top-chart-card",
                id="bar-chart-card",
            ),
            width=6,
        ),
        # Pie chart card
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    dcc.Loading(id="pie-chart-card-content"),
                    id="pie-chart-card-body"
                ),
                className="chart-card top-chart-card",
                id="pie-chart-card",
            ),
            width=6,
        ),
    ]
)

# Define the row for disparity map and area chart
disp_map_area_chart_row = dbc.Row(
    [
        # Disparity map card
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            dcc.Loading(id="disparity-map-card-content"),
                            occupation_type_slider,
                        ],
                        id="disparity-map-card-body",
                    )
                ],
                className="chart-card bottom-chart-card",
                id="disparity-map-card",
            ),
            width=6,
        ),
        # Stacked area chart card
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    dcc.Loading(id="stacked-area-chart-card-content"),
                    id="stacked-area-chart-card-body",
                ),
                className="chart-card bottom-chart-card",
                id="stacked-area-chart-card",
            ),
            width=6,
        ),
    ]
)

# Define the row for summary statistics
summary_stats_row = dbc.Row(
    [
        dbc.Col(summary_stats, id="summary-stats-column"),
    ],
    id="summary-stats-row",
)

# Define the layout of the app
app_layout = dbc.Container(
    [
        navigation_bar,
        filters_buttons_row,
        bar_pie_chart_row,
        disp_map_area_chart_row,
        summary_stats_row,
        dcc.Store(id="saved-analyses-store", data=[]),
    ]
)
