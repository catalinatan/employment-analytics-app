from dash import Output, Input, State, callback_context, html, dcc, no_update
from dash.dependencies import ALL
from dash.exceptions import PreventUpdate
from employment_flask_app.dash_app.components import full_descriptions
import dash_bootstrap_components as dbc
from employment_flask_app.dash_app.charts import (
    create_bar_chart,
    create_pie_chart,
    create_disparity_map,
    create_area_chart
)
from employment_flask_app.dash_app.filter_data_functions import filter_dataframe, prepare_disparity_df
import json


def toggle_data_attribution(n_clicks, is_open):
    """
    Toggle the display of data attribution based on the button click.

    Parameters
    ----------
    n_clicks : int
        Number of times the button has been clicked.
    is_open : bool
        Current state of the data attribution display.

    Returns
    -------
    bool
        New state of the data attribution display.
    """
    if n_clicks:
        # Toggle the state of the data attribution display when the button
        # is clicked
        return not is_open
    # Return the current state if the button has not been clicked
    return is_open


def clear_analysis_name(n_clicks):
    """
    Clear the analysis name input field when the save button is clicked.

    Parameters
    ----------
    n_clicks : int
        Number of times the save button has been clicked.

    Returns
    -------
    str or no_update
        An empty string to clear the input field or no_update if no clicks.
    """
    if n_clicks:
        # Return an empty string to clear the input field if the save button
        # has been clicked
        return ""
    # Return no_update if the save button has not been clicked
    return no_update


def save_filters(n_clicks, custom_analysis_name, region, year, occupation,
                 current_data, current_menu_items):
    """
    Save the current filters as a new analysis.

    Parameters
    ----------
    n_clicks : int
        Number of times the save button has been clicked.
    custom_analysis_name : str
        Custom name for the analysis.
    region : str
        Selected region.
    year : int
        Selected year.
    occupation : str
        Selected occupation.
    current_data : list
        List of current saved analyses.
    current_menu_items : list
        List of current menu items.

    Returns
    -------
    tuple
        Updated menu items, updated data, alert status, and alert message.
    """
    if not n_clicks:
        # Prevent update if the save button has not been clicked
        raise PreventUpdate

    if not region or not year:
        # Show alert if region or year is not selected
        return (
            no_update,
            no_update,
            True,
            "Please select a region and year before saving an analysis."
        )

    # Ensure the input has a valid name
    analysis_name = (
        custom_analysis_name.strip() if custom_analysis_name else
        f"Analysis {len(current_data) + 1}: {region}, {year}"
    )

    # Check if the analysis name already exists
    if any(analysis["name"] == analysis_name for analysis in current_data):
        # Show alert if the analysis name already exists
        return (
            no_update,
            no_update,
            True,
            f"An analysis named '{analysis_name}' already exists. "
            "Please choose a different name."
        )

    # Append new analysis
    new_analysis = {
        "name": analysis_name,
        "region": region,
        "year": year,
        "occupation": occupation
    }

    # Update the list of saved analyses
    updated_data = (
        current_data + [new_analysis] if current_data else [new_analysis]
    )

    # Create a new menu item for the saved analysis
    new_menu_item = dbc.DropdownMenuItem(
        analysis_name,
        id={"type": "saved-analysis", "index": len(updated_data) - 1},
        n_clicks=0
    )

    # Update the menu items with the new analysis
    updated_menu_items = (
        current_menu_items + [new_menu_item]
        if current_menu_items
        else [new_menu_item]
    )

    # Return the updated menu items, data, and alert status
    return updated_menu_items, updated_data, False, no_update


def update_tooltip(value):
    """
    Update the tooltip for the occupation type slider.

    Parameters
    ----------
    value : int
        Value of the occupation type slider.

    Returns
    -------
    dict
        Tooltip configuration.
    """
    # Return the tooltip configuration with the description of the selected
    # occupation type
    return {
        "placement": "bottom",  # Position the tooltip at the bottom
        "always_visible": True,  # Ensure the tooltip is always visible
        "template": f"{full_descriptions[value]}"  # Use the full description
    }


def show_summary_button(selected_region, selected_year, selected_occupation):
    """
    Show or hide the summary button based on the selected filters.

    Parameters
    ----------
    selected_region : str
        Selected region.
    selected_year : int
        Selected year.
    selected_occupation : str
        Selected occupation.

    Returns
    -------
    dict
        CSS style to show or hide the button.
    """
    # Check if any of the filters (region, year, occupation) are not selected
    if not selected_region or not selected_year or not selected_occupation:
        # Hide the summary button if any filter is not selected
        return {'display': 'none', "width": "100%"}

    # Show the summary button if all filters are selected
    return {'display': 'block', "width": "100%"}


def update_selected_filters_for_gender_stats(selected_region, selected_year):
    """
    Update the selected region and year for gender statistics.

    Parameters
    ----------
    selected_region : str
        Selected region.
    selected_year : int
        Selected year.

    Returns
    -------
    tuple
        Selected region and year.
    """
    if not selected_region or not selected_year:
        raise PreventUpdate

    return selected_region, selected_year


def update_selected_filters_for_occ_stats(
    selected_region, selected_year, selected_occupation
):
    """
    Update the selected region, year, and occupation for occupation statistics.

    Parameters
    ----------
    selected_region : str
        Selected region.
    selected_year : int
        Selected year.
    selected_occupation : str
        Selected occupation.

    Returns
    -------
    tuple
        Selected region, year, and occupation description.
    """
    # Prevent update if region, year, or occupation is not selected
    if not selected_region or not selected_year or not selected_occupation:
        raise PreventUpdate

    # Return the selected region, year, and occupation description
    return (
        selected_region,
        selected_year,
        full_descriptions[selected_occupation]
    )


def update_highest_disparity_region(selected_occupation, selected_year):
    """
    Update the highest disparity region based on the selected occupation
    and year.

    Parameters
    ----------
    selected_occupation : str
        Selected occupation.
    selected_year : int
        Selected year.

    Returns
    -------
    tuple
        Highest disparity region and percentage.
    """
    if not selected_occupation or not selected_year:
        # Prevent update if occupation or year is not selected
        raise PreventUpdate

    # Prepare the occupation prefix for filtering
    occupation_prefix = f"{selected_occupation}:"

    # Filter the dataframe based on the selected year and occupation prefix
    filtered_df = filter_dataframe(
        year=selected_year, occupation_prefix=occupation_prefix
    )

    # Prepare the disparity dataframe
    disparity_df = prepare_disparity_df(filtered_df)

    # Find the highest disparity percentage and its index
    highest_disparity_percentage = disparity_df['Disparity'].max()
    highest_disparity_perc_idx = disparity_df['Disparity'].idxmax()

    # Get the region with the highest disparity
    highest_disparity_region = disparity_df['Region'][
        highest_disparity_perc_idx]

    # Return the highest disparity region and percentage
    return highest_disparity_region, f"{highest_disparity_percentage:.2f}%"


def update_highest_disparity_occupation_for_selected_region(
    selected_region, selected_year
):
    """
    Update the highest disparity occupation based on the selected region
    and year.

    Parameters
    ----------
    selected_region : str
        Selected region.
    selected_year : int
        Selected year.

    Returns
    -------
    tuple
        Highest disparity occupation and percentage.
    """
    if not selected_region or not selected_year:
        # Prevent update if region or year is not selected
        raise PreventUpdate

    # Filter the dataframe based on the selected region and year
    filtered_df = filter_dataframe(region=selected_region, year=selected_year)

    # Prepare the disparity dataframe
    disparity_df = prepare_disparity_df(filtered_df)

    # Find the highest disparity percentage and its index
    highest_disparity_percentage = disparity_df['Disparity'].max()
    highest_disparity_perc_idx = disparity_df['Disparity'].idxmax()

    # Get the occupation with the highest disparity
    highest_disparity_occupation = disparity_df['Occupation Type'][
        highest_disparity_perc_idx]

    # Return the highest disparity occupation and percentage
    return highest_disparity_occupation, f"{highest_disparity_percentage:.2f}%"


def update_highest_male_employment_occupation(selected_region, selected_year):
    """
    Update the highest male employment occupation based on the selected region
    and year.

    Parameters
    ----------
    selected_region : str
        Selected region.
    selected_year : int
        Selected year.

    Returns
    -------
    tuple
        Highest male employment occupation and percentage.
    """
    if not selected_region or not selected_year:
        # Prevent update if region or year is not selected
        raise PreventUpdate

    # Filter the dataframe based on the selected region, year, and
    # gender (Male)
    male_df = filter_dataframe(
        region=selected_region, year=selected_year, gender='Male'
    )

    # Find the highest male employment percentage and its index
    highest_male_employment_percentage = male_df[
        'Percentage Employed (Relative to Total Employment in the Year)'
    ].max()
    highest_male_employ_perc_idx = male_df[
        'Percentage Employed (Relative to Total Employment in the Year)'
    ].idxmax()

    # Get the occupation with the highest male employment
    highest_male_employment_occupation = male_df['Occupation Type'][
        highest_male_employ_perc_idx]

    # Return the highest male employment occupation and percentage
    return highest_male_employment_occupation, \
        f"{highest_male_employment_percentage:.2f}%"


def update_highest_female_employment_occupation(
    selected_region, selected_year
):
    """
    Update the highest female employment occupation based on the selected
    region and year.

    Parameters
    ----------
    selected_region : str
        Selected region.
    selected_year : int
        Selected year.

    Returns
    -------
    tuple
        Highest female employment occupation and percentage.
    """
    if not selected_region or not selected_year:
        # Prevent update if region or year is not selected
        raise PreventUpdate

    # Filter the dataframe based on the selected region, year, and
    # gender (Female)
    female_df = filter_dataframe(region=selected_region,
                                 year=selected_year,
                                 gender='Female')

    # Find the highest female employment percentage and its index
    highest_female_employment_percentage = female_df[
        'Percentage Employed (Relative to Total Employment in the Year)'
    ].max()
    highest_female_employ_perc_idx = female_df[
        'Percentage Employed (Relative to Total Employment in the Year)'
    ].idxmax()

    # Get the occupation with the highest female employment
    highest_female_employment_occupation = female_df[
        'Occupation Type'
    ][highest_female_employ_perc_idx]

    # Return the highest female employment occupation and percentage
    return highest_female_employment_occupation, \
        f"{highest_female_employment_percentage:.2f}%"


def update_highest_overall_employment_occupation(
    selected_region, selected_year
):
    """
    Update the highest overall employment occupation based on the selected
    region and year.

    Parameters
    ----------
    selected_region : str
        Selected region.
    selected_year : int
        Selected year.

    Returns
    -------
    tuple
        Highest overall employment occupation and percentage.
    """
    if not selected_region or not selected_year:
        # Prevent update if region or year is not selected
        raise PreventUpdate

    # Filter the dataframe based on the selected region and year
    filtered_df = filter_dataframe(region=selected_region, year=selected_year)

    # Prepare the disparity dataframe
    disparity_df = prepare_disparity_df(filtered_df)

    # Find the highest overall employment percentage and its index
    highest_employment_percentage = disparity_df['Total Employment'].max()
    highest_employ_perc_idx = disparity_df['Total Employment'].idxmax()

    # Get the occupation with the highest overall employment
    highest_employment_occupation = disparity_df['Occupation Type'][
        highest_employ_perc_idx]

    # Return the highest overall employment occupation and percentage
    return (
        highest_employment_occupation,
        f"{highest_employment_percentage:.2f}%"
    )


def register_callbacks(app):
    """
    Register all callbacks for the Dash app.

    Parameters
    ----------
    app : Dash
        The Dash app instance.
    """
    # Data attribution callback to toggle the data attribution display
    @app.callback(
        Output("data-attribution-canvas", "is_open"),
        Input("data-attribution-button", "n_clicks"),
        State("data-attribution-canvas", "is_open"),
        prevent_initial_call=True
    )
    def wrapped_toggle_data_attribution(n_clicks, is_open):
        return toggle_data_attribution(n_clicks, is_open)

    # Clear analysis name callback to clear the analysis name input field
    @app.callback(
        Output("analysis-name-input", "value"),
        Input("save-filters-button", "n_clicks"),
    )
    def wrapped_clear_analysis_name(n_clicks):
        return clear_analysis_name(n_clicks)

    # Save filters callback to save the current filters as a new analysis
    @app.callback(
        Output("saved-analyses-menu", "children"),
        Output("saved-analyses-store", "data"),
        Output("save-alert", "is_open"),
        Output("save-alert", "children"),
        Input("save-filters-button", "n_clicks"),
        State("analysis-name-input", "value"),
        State("region-dropdown", "value"),
        State("year-dropdown", "value"),
        State("occupation-type-slider", "value"),
        State("saved-analyses-store", "data"),
        State("saved-analyses-menu", "children"),
        prevent_initial_call=True
    )
    def wrapped_save_filters(n_clicks, custom_analysis_name, region, year,
                             occupation, current_data, current_menu_items):
        return save_filters(n_clicks, custom_analysis_name, region, year,
                            occupation, current_data, current_menu_items)

    # Manage dropdowns callback to handle dropdown interactions
    @app.callback(
        [
            Output("region-dropdown", "value"),
            Output("year-dropdown", "value"),
            Output("occupation-type-slider", "value"),
            Output("summary-stats", "is_open")
        ],
        [
            Input({"type": "saved-analysis", "index": ALL}, "n_clicks"),
            Input('clear-button', 'n_clicks'),
            Input('display-summary-button', 'n_clicks')
        ],
        [
            State("saved-analyses-store", "data"),
            State('region-dropdown', 'value'),
            State('year-dropdown', 'value'),
            State('occupation-type-slider', 'value'),
            State('summary-stats', 'is_open')
        ],
        prevent_initial_call=True,
    )
    def manage_dropdowns(saved_n_clicks, clear_n_clicks, summary_n_clicks,
                         data, region_value, year_value, occupation_value,
                         summary_status):
        """
        Manage the dropdowns and summary button based on user interactions.

        Parameters
        ----------
        saved_n_clicks : list
            List of clicks on saved analyses.
        clear_n_clicks : int
            Number of times the clear button has been clicked.
        summary_n_clicks : int
            Number of times the summary button has been clicked.
        data : list
            List of saved analyses.
        region_value : str
            Current region value.
        year_value : int
            Current year value.
        occupation_value : int
            Current occupation value.
        summary_status : bool
            Current summary status.

        Returns
        -------
        tuple
            Updated region, year, occupation, and summary status.
        """
        # Get the callback context to determine which input triggered
        # the callback
        ctx = callback_context
        if not ctx.triggered:
            # Prevent update if no input triggered the callback
            raise PreventUpdate

        # Get the ID of the triggered input
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if triggered_id == 'clear-button':
            # Clear all dropdowns and close the summary if the clear button
            # is clicked
            return None, None, 1, False

        if triggered_id == 'display-summary-button':
            # Toggle the summary status if the summary button is clicked
            return (
                region_value,
                year_value,
                occupation_value,
                not summary_status
            )

        try:
            # Try to parse the triggered ID as JSON to check if it is a
            # saved analysis
            triggered_id = json.loads(triggered_id)
            if triggered_id.get("type") == "saved-analysis":
                # Get the index of the saved analysis
                analysis_index = triggered_id["index"]
                if 0 <= analysis_index < len(data):
                    # Return the saved analysis data if the index is valid
                    analysis_data = data[analysis_index]
                    return (
                        analysis_data["region"],
                        analysis_data["year"],
                        analysis_data["occupation"],
                        summary_status
                    )
        except json.JSONDecodeError:
            # Handle JSON decode error
            pass

        # Return the current values if no specific action is triggered
        return region_value, year_value, occupation_value, summary_status

    # Show summary button callback to show or hide the summary button
    @app.callback(
        Output('display-summary-button', 'style'),
        Input('region-dropdown', 'value'),
        Input('year-dropdown', 'value'),
        Input('occupation-type-slider', 'value')
    )
    def wrapped_show_summary_button(selected_region, selected_year,
                                    selected_occupation):
        return show_summary_button(selected_region, selected_year,
                                   selected_occupation)

    # Update the tooltip for the occupation type slider
    @app.callback(
        Output('occupation-type-slider', 'tooltip'),
        Input('occupation-type-slider', 'value')
    )
    def wrapped_update_tooltip(value):
        return update_tooltip(value)

    # Update bar chart
    @app.callback(
        Output('bar-chart-card-content', 'children'),
        Input('region-dropdown', 'value'),
        Input('year-dropdown', 'value'),
    )
    def update_bar_chart(selected_region, selected_year):
        """
        Update the stacked bar chart based on the selected region and year.

        Parameters
        ----------
        selected_region : str
            Selected region.
        selected_year : int
            Selected year.

        Returns
        -------
        html.Div or dcc.Graph
            Updated bar chart or placeholder image.
        """
        if not selected_region or not selected_year:
            # Return a placeholder image if no region or year is selected
            return html.Div([
                html.I(className="custom-icon bi bi-lock"),
                html.Img(
                    src=app.get_asset_url('stacked_bar_chart.png'),
                    className='custom-placeholder'
                )
            ])
        else:
            # Filter the dataframe based on the selected region and year
            filtered_df = filter_dataframe(
                region=selected_region, year=selected_year
            )
            # Extract the short occupation type for the bar chart
            filtered_df['Short Occupation Type'] = filtered_df[
                'Occupation Type'
            ].str.split(':').str[0]
            # Create the bar chart figure
            bar_chart_figure = create_bar_chart(
                filtered_df, selected_region, selected_year
            )
            # Return the bar chart as a dcc.Graph component
            return dcc.Graph(id="bar-chart", figure=bar_chart_figure)

    # Update pie chart
    @app.callback(
        Output('pie-chart-card-content', 'children'),
        Input('region-dropdown', 'value'),
        Input('year-dropdown', 'value'),
    )
    def update_pie_chart(selected_region, selected_year):
        """
        Update the pie chart based on the selected region and year.

        Parameters
        ----------
        selected_region : str
            Selected region.
        selected_year : int
            Selected year.

        Returns
        -------
        html.Div or dcc.Graph
            Updated pie chart or placeholder image.
        """
        if not selected_region or not selected_year:
            # Return a placeholder image if no region or year is selected
            return html.Div([
                html.I(className="custom-icon bi bi-lock"),
                html.Img(
                    src=app.get_asset_url('pie_chart_placeholder.png'),
                    className='custom-placeholder'
                )
            ])
        else:
            # Filter the dataframe based on the selected region and year
            filtered_df = filter_dataframe(
                region=selected_region, year=selected_year
            )
            # Prepare the disparity dataframe
            disparity_df = prepare_disparity_df(filtered_df)
            # Create the pie chart figure
            pie_chart_figure = create_pie_chart(
                disparity_df, selected_region, selected_year
            )
            # Return the pie chart as a dcc.Graph component
            return dcc.Graph(id="pie-chart", figure=pie_chart_figure)

    # Update disparity map
    @app.callback(
        Output("disparity-map-card-content", "children"),
        Input("year-dropdown", "value"),
        Input("occupation-type-slider", "value"),
    )
    def update_map(selected_year, selected_occupation):
        """
        Update the disparity map based on the selected year and occupation
        type.

        Parameters
        ----------
        selected_year : int
            Selected year.
        selected_occupation : str
            Selected occupation.

        Returns
        -------
        html.Div or dcc.Graph
            Updated disparity map or placeholder image.
        """
        if not selected_year or not selected_occupation:
            # Return a placeholder image if no year or occupation is selected
            return html.Div([
                html.I(className="custom-icon bi bi-lock"),
                html.Img(
                    src=app.get_asset_url('disparity_map_placeholder.png'),
                    className='custom-placeholder'
                )
            ])
        else:
            # Prepare the occupation prefix for filtering
            occupation_prefix = f"{selected_occupation}:"
            # Filter the dataframe based on the selected year and occupation
            # prefix
            filtered_df = filter_dataframe(
                year=selected_year, occupation_prefix=occupation_prefix
            )
            # Prepare the disparity dataframe
            disparity_df = prepare_disparity_df(filtered_df)
            # Create the disparity map figure
            disparity_map_figure = create_disparity_map(
                disparity_df, selected_year
            )
            # Return the disparity map as a dcc.Graph component
            return dcc.Graph(id="disparity-map", figure=disparity_map_figure)

    # Update stacked area chart
    @app.callback(
        Output("stacked-area-chart-card-content", 'children'),
        Input("region-dropdown", 'value'),
    )
    def update_area_chart(selected_region):
        """
        Update the stacked area chart based on the selected region.

        Parameters
        ----------
        selected_region : str
            Selected region.

        Returns
        -------
        html.Div or dcc.Graph
            Updated area chart or placeholder image.
        """
        if not selected_region:
            # Return a placeholder image if no region is selected
            return html.Div([
                html.I(className="custom-icon bi bi-lock"),
                html.Img(
                    src=app.get_asset_url(
                        'stacked_area_chart_placeholder.png'
                    ),
                    className='custom-placeholder'
                )
            ])
        else:
            # Filter the dataframe based on the selected region
            filtered_df = filter_dataframe(region=selected_region)
            # Prepare the disparity dataframe
            disparity_df = prepare_disparity_df(filtered_df)
            # Create the area chart figure
            area_chart_figure = create_area_chart(
                disparity_df, selected_region
            )
            # Return the area chart as a dcc.Graph component
            return dcc.Graph(id="stacked-area-chart", figure=area_chart_figure)

    # Update selected region and year for gender occupation statistics card
    @app.callback(
        Output("gen-selected-region", "children"),
        Output("gen-selected-year", "children"),
        Input("region-dropdown", "value"),
        Input("year-dropdown", "value"),
    )
    def wrapped_update_selected_filters_for_gender_stats(
        selected_region, selected_year
    ):
        return update_selected_filters_for_gender_stats(
            selected_region, selected_year
        )

    # Update selected region and year for occupation type statistics card
    @app.callback(
        Output("occ-selected-region", "children"),
        Output("occ-selected-year", "children"),
        Output('selected-occupation-type', 'children'),
        Input("region-dropdown", "value"),
        Input("year-dropdown", "value"),
        Input('occupation-type-slider', 'value')
    )
    def wrapped_update_selected_filters_for_occ_stats(
        selected_region, selected_year, selected_occupation
    ):
        return update_selected_filters_for_occ_stats(
            selected_region, selected_year, selected_occupation
        )

    # Update highest disparity region and percentage
    @app.callback(
        Output("highest-disparity-region", "children"),
        Output("highest-disparity-percentage", "children"),
        Input("occupation-type-slider", "value"),
        Input("year-dropdown", "value"),
    )
    def wrapped_update_highest_disparity_region(
        selected_occupation, selected_year
    ):
        return update_highest_disparity_region(
            selected_occupation, selected_year
        )

    # Update highest disparity occupation and percentage
    @app.callback(
        Output("highest-disparity-occupation", "children"),
        Output("highest-disparity-occupation-percentage", "children"),
        Input("region-dropdown", "value"),
        Input("year-dropdown", "value"),
        allow_duplicate=True
    )
    def wrapped_update_highest_disparity_occupation_for_selected_region(
        selected_region, selected_year
    ):
        return update_highest_disparity_occupation_for_selected_region(
            selected_region, selected_year
        )

    # Update highest overall employment occupation and percentage
    @app.callback(
        Output("highest-employment-occupation", "children"),
        Output("highest-employment-percentage", "children"),
        Input("region-dropdown", "value"),
        Input("year-dropdown", "value")
    )
    def wrapped_update_highest_overall_employment_occupation(
        selected_region, selected_year
    ):
        return update_highest_overall_employment_occupation(
            selected_region, selected_year
        )

    # Update highest male employment occupation and percentage
    @app.callback(
        Output("highest-male-employment-occupation", "children"),
        Output("highest-male-employment-percentage", "children"),
        Input("region-dropdown", "value"),
        Input("year-dropdown", "value")
    )
    def wrapped_update_highest_male_employment_occupation(
        selected_region, selected_year
    ):
        return update_highest_male_employment_occupation(
            selected_region, selected_year
        )

    # Update highest female employment occupation and percentage
    @app.callback(
        Output("highest-female-employment-occupation", "children"),
        Output("highest-female-employment-percentage", "children"),
        Input("region-dropdown", "value"),
        Input("year-dropdown", "value")
    )
    def wrapped_update_highest_female_employment_occupation(
        selected_region, selected_year
    ):
        return update_highest_female_employment_occupation(
            selected_region, selected_year
        )
