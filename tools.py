import pandas as pd

def load_data():
    df = pd.read_csv('data/listings_detailed.csv') # retrieve raw data
    print("Columns: ",len(df.columns))

    # Drop unnecessary columns
    redundant_cols = ['id', 'name', 'listing_url', 'scrape_id', 
        'last_scraped', 'neighborhood_overview', 'picture_url', 'host_id', 'host_url', 
        'host_name', 'host_location','host_about', 'host_response_time', 'host_thumbnail_url', 
        'host_picture_url', 'host_total_listings_count', 'neighbourhood', 'calendar_updated', 
        'neighbourhood_group_cleansed', 'minimum_minimum_nights', 'maximum_minimum_nights', 
        'minimum_maximum_nights', 'maximum_maximum_nights', 'minimum_nights_avg_ntm', 
        'maximum_nights_avg_ntm', 'has_availability', 'number_of_reviews_l30d', 'license', 
        'bathrooms_text', 'host_neighbourhood', 'first_review', 'last_review']
    df.drop(columns=redundant_cols, inplace=True)

    # Convert date columns to datetime
    df.host_since = pd.to_datetime(df.host_since, format='%Y-%m-%d')
    df.calendar_last_scraped = pd.to_datetime(df.calendar_last_scraped, format='%Y-%m-%d')

    # Convert 't' to 1 and 'f' to 0
    df.host_is_superhost = df.host_is_superhost.apply(lambda x: 1 if x=='t' else 0)
    df.host_has_profile_pic = df.host_has_profile_pic.apply(lambda x: 1 if x=='t' else 0)
    df.host_identity_verified = df.host_identity_verified.apply(lambda x: 1 if x=='t' else 0)
    df.instant_bookable = df.instant_bookable.apply(lambda x: 1 if x=='t' else 0)

    # Change amenities to total count of amenities
    df.amenities_count = df.amenities.str[1:-1].apply(lambda x: len(x.split(',')))
    df.drop('amenities', axis=1, inplace=True)

    # Change verifications to total count of verifications
    df.host_verifications_count = df.host_verifications.str[1:-1].apply(lambda x: len(x.split(',')))
    df.drop('host_verifications', axis=1, inplace=True)

    # Convert price to int (kr)
    df['price'] = df['price'].str[1:]  # remove $-sign
    df['price'] = df['price'].str.replace(',', '').astype(float)  # remove commas

    # Add binary column for missing response rate and set missing values to 0
    df.response_rate_missing = df.host_response_rate.notnull().astype(int)
    df.host_response_rate.fillna('0%', inplace=True)
    df.host_response_rate = df.host_response_rate.str[:-1].astype(float)/100

    # Add binary column for missing acceptance rate and set missing values to 0
    df.acceptance_rate_missing = df.host_acceptance_rate.notnull().astype(int)
    df.host_acceptance_rate.fillna('0%', inplace=True)
    df.host_acceptance_rate = df.host_acceptance_rate.str[:-1].astype(float)/100

    # Set missing values for reviews to mean
    df.review_scores_rating.fillna(df.review_scores_rating.mean(), inplace=True)
    df.review_scores_accuracy.fillna(df.review_scores_accuracy.mean(), inplace=True)
    df.review_scores_cleanliness.fillna(df.review_scores_cleanliness.mean(), inplace=True)
    df.review_scores_checkin.fillna(df.review_scores_checkin.mean(), inplace=True)
    df.review_scores_communication.fillna(df.review_scores_communication.mean(), inplace=True)
    df.review_scores_location.fillna(df.review_scores_location.mean(), inplace=True)
    df.review_scores_value.fillna(df.review_scores_value.mean(), inplace=True)

    # Set missing values for reviews per month to 0 (never gotten reviews)
    df.reviews_per_month.fillna(0, inplace=True)

    # Fill missing roomspecifications with mode and set type to integer
    df.bathrooms = df.bathrooms.fillna(df.bathrooms.mode()[0]).astype(int)
    df.bedrooms = df.bedrooms.fillna(df.bedrooms.mode()[0]).astype(int)
    df.beds = df.beds.fillna(df.beds.mode()[0]).astype(int)

    # Drop remaining NA-values
    df.dropna(inplace=True)

    return df