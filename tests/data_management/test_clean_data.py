import pytest
from crime_patterns.data_management import clean_data


def test_clean_monthly_crime_data(raw_data_info):
    cleaned_sample = clean_data.clean_monthly_crime_data(
        crime_incidence_filepath=pytest.sample_raw_data_path,
        year=raw_data_info["year"],
        month=raw_data_info["month"],
        crime_type=raw_data_info["crime_type"],
        columns_to_drop=raw_data_info["columns_to_drop"],
    )

    assert not set(raw_data_info["columns_to_drop"]).intersection(
        set(cleaned_sample.columns),
    )
    assert (
        cleaned_sample[raw_data_info["outcome_column"]].unique()[0]
        == raw_data_info["crime_type"]
    )
