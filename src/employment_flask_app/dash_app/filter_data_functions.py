import pandas as pd
from pathlib import Path

# Create dataframe
data_path = Path(__file__).parent.parent / 'data' / 'employment_prepared.xlsx'
df = pd.read_excel(data_path)


def filter_dataframe(region=None, year=None,
                     occupation_prefix=None, gender=None):
    """
    Filter the dataframe based on the provided region, year, occupation prefix,
    and gender.

    Parameters
    ----------
    region : str, optional
        The region to filter by.
    year : int, optional
        The year to filter by.
    occupation_prefix : str, optional
        The occupation prefix to filter by.
    gender : str, optional
        The gender to filter by.

    Returns
    -------
    pd.DataFrame
        The filtered dataframe.
    """
    # Create a copy of the dataframe to avoid modifying the original
    filtered_df = df.copy()

    # Filter by region if specified
    if region:
        filtered_df = filtered_df[filtered_df['Region'] == region]

    # Filter by year if specified
    if year:
        filtered_df = filtered_df[filtered_df['Year'] == int(year)]

    # Filter by occupation prefix if specified
    if occupation_prefix:
        filtered_df = filtered_df[
            filtered_df['Occupation Type'].str.startswith(occupation_prefix)
        ]

    # Filter by gender if specified
    if gender:
        filtered_df = filtered_df[filtered_df['Gender'] == gender]

    # Return the filtered dataframe
    return filtered_df


def prepare_year_pivot_df(disparity_df):
    """
    Prepare a pivot table of the disparity dataframe by year.

    Parameters
    ----------
    disparity_df : pd.DataFrame
        The disparity dataframe.

    Returns
    -------
    pd.DataFrame
        The pivot table with year disparity.
    """
    # Pivot the disparity dataframe to create a table with years as columns
    year_pivot_df = disparity_df.pivot_table(
        index=['Region', 'Occupation Type', 'Latitude', 'Longitude'],
        columns='Year',
        values='Total Employment',
        fill_value=0
    ).reset_index()

    # Calculate the disparity between the years 2023 and 2021
    year_pivot_df['Year Disparity'] = (
        year_pivot_df[2023] - year_pivot_df[2021]
    )

    # Return the pivot table with the year disparity
    return year_pivot_df


def prepare_disparity_df(filtered_df):
    """
    Prepare the disparity dataframe by pivoting and calculating total
    employment.

    Parameters
    ----------
    filtered_df : pd.DataFrame
        The filtered dataframe.

    Returns
    -------
    pd.DataFrame
        The prepared disparity dataframe.
    """
    perc_col = "Percentage Employed (Relative to Total Employment in the Year)"

    # Pivot the filtered dataframe to create a table with genders as columns
    disparity_df = filtered_df.pivot_table(
        index=['Region', 'Year', 'Occupation Type', 'Latitude', 'Longitude'],
        columns='Gender',
        values=perc_col,
        fill_value=0
    ).reset_index()

    # Calculate the total employment by summing male and female employment
    disparity_df['Total Employment'] = (
        disparity_df['Male'] + disparity_df['Female']
    )

    # Calculate the absolute disparity between male and female employment
    disparity_df['Disparity'] = (
        disparity_df['Male'] - disparity_df['Female']
    ).abs()

    # Return the prepared disparity dataframe
    return disparity_df


def find_highest_dis_by_gender(df, gender, region=None):
    """
    Find the highest year disparity percentage for a specific gender.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe to search.
    gender : str
        The gender to filter by.
    region : str, optional
        The region to filter by.

    Returns
    -------
    tuple
        The highest year disparity percentage, occupation, and region.
    """
    # Filter the dataframe by region if specified
    if region:
        df = df[df['Region'] == region]

    # Prepare the disparity dataframe
    prepared_df = prepare_disparity_df(df)

    # Prepare the year pivot dataframe
    pivot_df = prepare_year_pivot_df(prepared_df)

    # Merge the prepared dataframe with the year pivot dataframe
    merged_df = prepared_df.merge(
        pivot_df[
            ['Region', 'Occupation Type', 'Latitude',
             'Longitude', 'Year Disparity']
        ],
        on=['Region', 'Occupation Type', 'Latitude', 'Longitude'],
        how='left'
    )

    # Define the column name for the percentage value
    perc_col = "Percentage Employed (Relative to Total Employment in the Year)"

    # Melt the merged dataframe to have gender as a variable
    melted_df = merged_df.melt(
        id_vars=['Region', 'Year', 'Occupation Type', 'Latitude', 'Longitude',
                 'Total Employment', 'Disparity', 'Year Disparity'],
        value_vars=['Male', 'Female'],
        var_name='Gender',
        value_name=perc_col
    )

    # Filter the melted dataframe by the specified gender
    specific_gender_df = melted_df[melted_df["Gender"] == gender]

    # Find the highest absolute year disparity percentage
    highest_absolute_year_disparity_perc = specific_gender_df[
        'Year Disparity'].abs().max()

    # Find the index of the highest year disparity percentage
    highest_year_disparity_perc_idx = specific_gender_df[
        'Year Disparity'].abs().idxmax()

    # Determine the highest year disparity percentage with sign
    if specific_gender_df['Year Disparity'][
            highest_year_disparity_perc_idx] < 0:
        highest_year_disparity_percentage = (
            f"-{highest_absolute_year_disparity_perc:.2f}"
        )
    else:
        highest_year_disparity_percentage = (
            f"{highest_absolute_year_disparity_perc:.2f}"
        )

    # Get the occupation type with the highest year disparity percentage
    highest_year_disparity_occupation = specific_gender_df['Occupation Type'][
        highest_year_disparity_perc_idx]

    # Get the region with the highest year disparity percentage
    highest_disparity_region = specific_gender_df[
        'Region'][highest_year_disparity_perc_idx]

    # Return the highest year disparity percentage, occupation, and region
    return (highest_year_disparity_percentage,
            highest_year_disparity_occupation,
            highest_disparity_region)


def find_overall_highest_disparity(df, region=None):
    """
    Find the overall highest disparity between genders.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe to search.
    region : str, optional
        The region to filter by.

    Returns
    -------
    tuple
        The highest overall disparity percentage, occupation, region,
        and gender.
    """
    # Find the highest disparity for males
    highest_male_disparity = find_highest_dis_by_gender(df, "Male", region)

    # Find the highest disparity for females
    highest_female_disparity = find_highest_dis_by_gender(df, "Female", region)

    # Extract the highest disparity percentages
    highest_male_disparity_perc = highest_male_disparity[0]
    highest_female_disparity_perc = highest_female_disparity[0]

    # Compare the highest disparities and return the overall highest
    if float(highest_male_disparity_perc) > float(
            highest_female_disparity_perc):
        return highest_male_disparity + ("Male",)
    elif float(highest_male_disparity_perc) == float(
            highest_female_disparity_perc):
        return highest_male_disparity + ("Equal",)
    else:
        return highest_female_disparity + ("Female",)


# Find the highest year disparity for males
(highest_m_year_disparity_percentage,
 highest_m_year_disparity_occupation,
 highest_m_year_disparity_region) = find_highest_dis_by_gender(df, "Male")

# Find the highest year disparity for females
(highest_f_year_disparity_percentage,
 highest_f_year_disparity_occupation,
 highest_f_year_disparity_region) = find_highest_dis_by_gender(df, "Female")

# Find the overall highest disparity
(highest_overall_disparity_percentage,
 highest_overall_disparity_occupation,
 highest_overall_disparity_region,
 highest_overall_disparity_gender) = find_overall_highest_disparity(df)
