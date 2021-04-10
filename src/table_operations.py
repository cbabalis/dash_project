""" Module to make some table operations (joins, meges, etc).
"""

import pandas as pd
import pdb


DATA = 'data/'


def join_tables(t1, t2, join_key):
    table = pd.merge(t1, t2, on=join_key, how='left')
    return table


def unzip_range(df, column=''):
    if not df[column]:
        print("No valid column")
        return -1
    


def get_period(df, column='', period_range=()):
    if not df[column]:
        print("No valid column!")
        return -1
    min_val, max_val = period_range
    table = df[column].between(min_val, max_val)
    return table


def process_seasonality(df, seasonality_titles=[], column_to_split='', delim=','):
    if not seasonality_titles:
        print("No seasonality titles have been given!")
    # split the seasonality to columns
    df[seasonality_titles] = df[column_to_split].str.split(delim,1,expand=True)
    df = find_min_max_seasonal_values(df,seasonality_titles)
    # now delete the seasonality (temp) titles
    for title in seasonality_titles:
        del df[title]
    return df


def find_min_max_seasonal_values(df, seasonality_titles):
    """ Method to find the minimum and maximum week numbers of seasonality availability.
    
    :param df
    :param seasonality_titles (list)
    
    Algorithm:
    for each column:
        create min and max column names
        populate by splitting the previous column to dash (-)
    """
    for title in seasonality_titles:
        min_title = str(title) + '_start'
        max_title = str(title) + '_end'
        df[[min_title, max_title]] = df[title].str.split('-',1,expand=True)
    return df


def main():
    pro_table_elstat = pd.read_csv('data/ProTABLE_1_elstat_NUTS3_2018.csv', delimiter='\t')
    seasonal_prod = pd.read_csv('data/Εποχικότητα_ΔΙΣΤΗΛΟ.csv', delimiter='\t')
    data_table = join_tables(pro_table_elstat, seasonal_prod, 'Αγροτικά Προϊόντα')
    print(data_table)
    df = process_seasonality(data_table, ['Εποχικότητα', 'Εξτρα Εποχικότητα'], 'Εποχικότητα_εβδομάδες')
    df.to_csv('matrices_to_show/Εξαγωγές Αγροτικών Προϊόντων_Εποχικότητα.csv', sep='\t')
    pdb.set_trace()
    #pass


if __name__ == '__main__':
    main()