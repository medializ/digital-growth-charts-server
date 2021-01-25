from datetime import date, datetime
from datetime import timedelta
from dateutil import relativedelta
import math
from .constants import TERM_PREGNANCY_LENGTH_DAYS, TERM_LOWER_THRESHOLD_LENGTH_DAYS, EXTREME_PREMATURITY_THRESHOLD_LENGTH_DAYS

"""
5 functions to calculate age related parameters
 - decimal_age: returns a decimal age from 2 dates (birth_date and observation_date) and gestational age at delivery (gestation_weeks and gestation_days), based on 40 weeks as 0. Days/Weeks before 40 weeks are negative.
 - chronological_decimal_age: returns a decimal age from 2 dates (takes birth_date and observation_date)
 - corrected_decimal_age: returns a corrected decimal age accounting for prematurity (takes birth_date: date, observation_date: date, gestation_weeks: int, gestation_days: int, pregnancy_length_day [optional])
 - chronological_calendar_age: returns a calendar age as a string (takes birth_date or estimated_date_delivery and observation_date)
 - estimated_date_delivery: returns estimated date of delivery in a known premature infant (takes birth_date, gestation_weeks, gestation_days, pregnancy_length_days[optional])
"""

def decimal_age(birth_date: date, observation_date: date, gestation_weeks: int, gestation_days: int):
    """
    returns decimal age relative to forty weeks expressed as 0 y
    THIS FUNCTION IS DEPRECATED
    """
    days_born_from_forty_weeks = ((gestation_weeks * 7) + gestation_days) - TERM_PREGNANCY_LENGTH_DAYS
    days_of_life_in_years = chronological_decimal_age(birth_date, observation_date)
    return  (days_born_from_forty_weeks / 365.25) + days_of_life_in_years


def chronological_decimal_age(birth_date: date, observation_date: date) -> float:

    """
    Calculates a decimal age from two dates supplied as raw dates without times.
    Returns value floating point
    :param birth_date: date of birth
    :param observation_date: date observation made
    """

    dates_interval = observation_date - birth_date
    chronological_decimal_age = dates_interval.days / 365.25
    return chronological_decimal_age
    

def corrected_decimal_age(birth_date: date, observation_date: date, gestation_weeks: int, gestation_days: int)->float: 
    """
    Corrects for gestational age. 
    Corrects for 1 year corrected age, if gestation at birth >= 32 weeks and < 37 weeks
    Corrects for 2 years corrected age, if gestation at birth <32 weeks
    Otherwise returns decimal age without correction
    Any baby 37-42 weeks returns decimal age of 0.0
    Depends on chronological_decimal_age
    :param birth_date: date of birth
    :param observation_date: date observation made
    :param gestation_weeks: weeks of gestation up to 40
    :param gestation_days: days in excess of weeks
    """
    
    correction_days = 0
    pregnancy_length_days = TERM_PREGNANCY_LENGTH_DAYS

    if gestation_weeks > 0 and gestation_weeks < 37:
        pregnancy_length_days = (gestation_weeks * 7) + gestation_days

    try:
        uncorrected_age = chronological_decimal_age(birth_date, observation_date)
    except ValueError as err:
        return err


    ## age correction
    prematurity = TERM_PREGNANCY_LENGTH_DAYS - pregnancy_length_days
    correction_days = prematurity
    edd = birth_date + timedelta(days=correction_days)
    corrected_age =  chronological_decimal_age(edd, observation_date)

    if pregnancy_length_days < EXTREME_PREMATURITY_THRESHOLD_LENGTH_DAYS and corrected_age <= 2:
        #correct age for 2 years
        return corrected_age
    elif (pregnancy_length_days >= EXTREME_PREMATURITY_THRESHOLD_LENGTH_DAYS) and (pregnancy_length_days < TERM_LOWER_THRESHOLD_LENGTH_DAYS) and corrected_age <=1:
        #correct age for 1 year
        return corrected_age
    else:
        return uncorrected_age
    


def chronological_calendar_age(birth_date: date, observation_date: date) -> str:
    """
    returns age in years, months, weeks and days: to return a corrected calendar age use passes EDD instead of birth date
    """
    difference = relativedelta.relativedelta(observation_date, birth_date)
    years = difference.years
    months = difference.months
    weeks = difference.weeks
    days = difference.days

    date_string = []

    if years == 1:
        date_string.append(str(years) + " year")
    if years > 1:
        date_string.append(str(years) + " years")
    if months > 1:
        date_string.append(str(months) + " months")
    if months == 1:
        date_string.append(str(months) + " month")
    if days == 1:
        date_string.append(str(days) + " day")
    if days > 1:
        if weeks > 0:
            remainingdays = days - (weeks*7)
            if weeks == 1:
                date_string.append(str(weeks) + " week")
            elif weeks > 1:
                date_string.append(str(weeks) + " weeks")
            if remainingdays == 1:
                date_string.append(str(remainingdays) + " day")
            if remainingdays > 1:
                date_string.append(str(remainingdays) + " days")
    if len(date_string) > 1:
        return (', '.join(date_string[:-1])) + ' and ' + date_string[-1]
    elif len(date_string) == 1:
        return date_string[0]
    elif birth_date == observation_date:
        return 'Happy Birthday'
    else:
        return ''


def estimated_date_delivery(birth_date: date, gestation_weeks: int, gestation_days: int) -> date:
    """
    Returns estimated date of delivery from gestational age and birthdate
    Will still calculate an estimated date of delivery if already term (>37 weeks)
    """
    pregnancy_length_days = TERM_PREGNANCY_LENGTH_DAYS

    if gestation_weeks > 0:
        pregnancy_length_days = (gestation_weeks * 7) + gestation_days
    
    prematurity = TERM_PREGNANCY_LENGTH_DAYS - pregnancy_length_days

    edd = birth_date + timedelta(days=prematurity)
    return edd


def corrected_gestational_age(birth_date: date, observation_date: date, gestation_weeks: int, gestation_days: int)->str:
    """
    Returns a corrected gestational age
    """
    edd = estimated_date_delivery(birth_date, gestation_weeks, gestation_days)
    forty_two_weeks_gestation_date = edd + timedelta(days=14)

    if observation_date >= forty_two_weeks_gestation_date:
        #beyond 2 weeks post term - chronological age measured in days / weeks / months years
        #no correction
        return {
            "corrected_gestation_weeks": None,
            "corrected_gestation_days": None
        }
    
    pregnancy_length_days = (gestation_weeks * 7) + gestation_days
    time_alive = observation_date - birth_date
    days_of_life = time_alive.days
    days_since_conception = days_of_life + pregnancy_length_days

    corrected_weeks = math.floor(days_since_conception / 7)
    corrected_supplementary_days = days_since_conception - (corrected_weeks * 7)

    return {
        'corrected_gestation_weeks': corrected_weeks,
        'corrected_gestation_days': corrected_supplementary_days
    }