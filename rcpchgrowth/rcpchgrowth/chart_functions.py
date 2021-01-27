from .global_functions import sds_for_centile, rounded_sds_for_centile, generate_centile
from .uk_who import select_reference_data_for_uk_who_chart
from .trisomy_21 import select_reference_data_for_trisomy_21
from .turner import select_reference_data_for_turner
from .constants.parameter_constants import *

def create_chart(reference:str, centile_selection:str):
    if reference == "uk-who":
        return create_uk_who_chart(centile_selection=centile_selection)
    elif reference == "turner":
        return create_turner_chart(centile_selection=centile_selection)
    elif reference == "trisomy_21":
        return create_trisomy_21_chart(centile_selection=centile_selection)
    else:
        print("No reference data returned. Is there a spelling mistake in your reference?")


"""
private functions
"""

def create_uk_who_chart(centile_selection: str=COLE_TWO_THIRDS_SDS_NINE_CENTILES):

    ## user selects which centile collection they want
    ## If the Cole method is selected, conversion between centile and SDS
    ## is different as SDS is rounded to the nearest 2/3
    ## Cole method selection is stored in the cole_method flag.
    ## If no parameter is passed, default is the Cole method

    centile_collection = []

    if centile_selection == COLE_TWO_THIRDS_SDS_NINE_CENTILES:
        centile_collection = COLE_TWO_THIRDS_SDS_NINE_CENTILE_COLLECTION
        cole_method = True
    else:
        centile_collection = THREE_PERCENT_CENTILE_COLLECTION
        cole_method = False
    
    ##
    # iterate through the 4 references that make up UK-WHO
    # There will be a list for each one
    ##
    
    reference_data = [] # all data for a given reference are stored here: this is returned to the user

    for reference_index, reference in enumerate(UK_WHO_REFERENCES):
        sex_list: dict = {} # all the data for a given sex are stored here
        ## For each reference we have 2 sexes
        for sex_index, sex in enumerate(SEXES):
            ##For each sex we have 4 measurement_methods

            measurements: dict = {} # all the data for a given measurement_method are stored here

            for measurement_index, measurement_method in enumerate(MEASUREMENT_METHODS):
                ## for every measurement method we have as many centiles
                ## as have been requested

                centiles=[] # all generated centiles for a selected centile collection are stored here

                for centile_index, centile in enumerate(centile_collection):
                    ## we must create a z for each requested centile
                    ## if the Cole 9 centiles were selected, these are rounded,
                    ## so conversion to SDS is different
                    ## Otherwise standard conversation of centile to z is used
                    if cole_method:
                        z = rounded_sds_for_centile(centile)
                    else:
                        z = sds_for_centile(centile)
                    
                    ## Collect the LMS values from the correct reference
                    lms_array_for_measurement=select_reference_data_for_uk_who_chart(uk_who_reference=reference, measurement_method=measurement_method, sex=sex)
                    
                    ## Generate a centile. there will be nine of these if Cole method selected.
                    ## Some data does not exist at all ages, so any error reflects missing data.
                    ## If this happens, an empty list is returned.
                    try:
                        centile_data = generate_centile(z=z, centile=centile, measurement_method=measurement_method, sex=sex, lms_array_for_measurement=lms_array_for_measurement, reference="uk-who")
                    except:
                        print(f"There is no data for {measurement_method} at this age.")
                        centile_data = []

                    ## Store this centile for a given measurement
                    centiles.append({"sds": round(z*100)/100, "centile": centile, "data": centile_data})
                    
                ## this is the end of the centile_collection for loop
                ## All the centiles for this measurement, sex and reference are added to the measurements list
                measurements.update({measurement_method: centiles})
            
            ## this is the end of the measurement_methods loop
            ## All data for all measurement_methods for this sex are added to the sex_list list

            sex_list.update({sex: measurements})
                
        ## all data can now be tagged by reference_name and added to reference_data
        reference_data.append({reference: sex_list})
        
    ## returns a list of 4 references, each containing 2 lists for each sex, 
    ## each sex in turn containing 4 datasets for each measurement_method
    return reference_data

    """

    structure:

    UK_WHO generates 4 json objects, each structure as below

    uk90_preterm: {
        male: {
            height: [
                {
                    sds: -2.667,
                    centile: 0.4
                    data: [{l: , x: , y: }, ....]
                }
            ],
            weight: [...]
        },
        female {...}
    }

    uk_who_infant: {...}
    uk_who_child:{...}
    uk90_child: {...}


    """



def create_turner_chart(centile_selection: str):
   ## user selects which centile collection they want
    ## If the Cole method is selected, conversion between centile and SDS
    ## is different as SDS is rounded to the nearest 2/3
    ## Cole method selection is stored in the cole_method flag.
    ## If no parameter is passed, default is the Cole method

    centile_collection = []

    if centile_selection == COLE_TWO_THIRDS_SDS_NINE_CENTILES:
        centile_collection = COLE_TWO_THIRDS_SDS_NINE_CENTILE_COLLECTION
        cole_method = True
    else:
        centile_collection = THREE_PERCENT_CENTILE_COLLECTION
        cole_method = False
    
    reference_data = {} # all data for a the reference are stored here: this is returned to the user 
    sex_list: dict = {}

    for sex_index, sex in enumerate(SEXES):
            ##For each sex we have 4 measurement_methods
            ## Turner is female only, but we will generate empty arrays for male
            ## data to keep all objects the same

        measurements: dict = {} # all the data for a given measurement_method are stored here

        for measurement_index, measurement_method in enumerate(MEASUREMENT_METHODS):
            ## for every measurement method we have as many centiles
            ## as have been requested

            centiles=[] # all generated centiles for a selected centile collection are stored here

            for centile_index, centile in enumerate(centile_collection):
                ## we must create a z for each requested centile
                ## if the Cole 9 centiles were selected, these are rounded,
                ## so conversion to SDS is different
                ## Otherwise standard conversation of centile to z is used
                if cole_method:
                    z = rounded_sds_for_centile(centile)
                else:
                    z = sds_for_centile(centile)
                
                ## Collect the LMS values from the correct reference
                try:
                    lms_array_for_measurement=select_reference_data_for_turners(measurement_method=measurement_method, sex=sex)
                except LookupError:
                    # there is no data in the reference
                    lms_array_for_measurement=[]
                
                ## Generate a centile. there will be nine of these if Cole method selected.
                ## Some data does not exist at all ages, so any error reflects missing data.
                ## If this happens, an empty list is returned.
                try:
                    centile_data = generate_centile(z=z, centile=centile, measurement_method=measurement_method, sex=sex, lms_array_for_measurement=lms_array_for_measurement, reference=TRISOMY_21)
                except:
                    print(f"There is no Turner data for {measurement_method} at this age.")
                    centile_data = []

                ## Store this centile for a given measurement
                centiles.append({"sds": round(z*100)/100, "centile": centile, "data": centile_data})
                
            ## this is the end of the centile_collection for loop
            ## All the centiles for this measurement, sex and reference are added to the measurements list
            measurements.update({measurement_method: centiles})
            
            ## this is the end of the measurement_methods loop
            ## All data for all measurement_methods for this sex are added to the sex_list list

            sex_list.update({sex: measurements})
                
    ## all data can now be tagged by reference_name and added to reference_data
    reference_data={TURNERS: sex_list}
    return reference_data

    """
    Return object structure

    trisomy_21: {
        male: {
            height: [
                {
                    sds: -2.667,
                    centile: 0.4
                    data: [{l: , x: , y: }, ....]
                }
            ],
            weight: [...]
        },
        female {...}
    }
    """

def create_trisomy_21_chart(centile_selection: str):
   ## user selects which centile collection they want
    ## If the Cole method is selected, conversion between centile and SDS
    ## is different as SDS is rounded to the nearest 2/3
    ## Cole method selection is stored in the cole_method flag.
    ## If no parameter is passed, default is the Cole method

    centile_collection = [] 

    if centile_selection == COLE_TWO_THIRDS_SDS_NINE_CENTILES:
        centile_collection = COLE_TWO_THIRDS_SDS_NINE_CENTILE_COLLECTION
        cole_method = True
    else:
        centile_collection = THREE_PERCENT_CENTILE_COLLECTION
        cole_method = False
    
    reference_data = {} # all data for a the reference are stored here: this is returned to the user 
    sex_list: dict = {}

    for sex_index, sex in enumerate(SEXES):
            ##For each sex we have 4 measurement_methods

        measurements: dict = {} # all the data for a given measurement_method are stored here

        for measurement_index, measurement_method in enumerate(MEASUREMENT_METHODS):
            ## for every measurement method we have as many centiles
            ## as have been requested

            centiles=[] # all generated centiles for a selected centile collection are stored here

            for centile_index, centile in enumerate(centile_collection):
                ## we must create a z for each requested centile
                ## if the Cole 9 centiles were selected, these are rounded,
                ## so conversion to SDS is different
                ## Otherwise standard conversation of centile to z is used
                if cole_method:
                    z = rounded_sds_for_centile(centile)
                else:
                    z = sds_for_centile(centile)
                
                ## Collect the LMS values from the correct reference
                lms_array_for_measurement=select_reference_data_for_trisomy_21(measurement_method=measurement_method, sex=sex)
                ## Generate a centile. there will be nine of these if Cole method selected.
                ## Some data does not exist at all ages, so any error reflects missing data.
                ## If this happens, an empty list is returned.
                try:
                    centile_data = generate_centile(z=z, centile=centile, measurement_method=measurement_method, sex=sex, lms_array_for_measurement=lms_array_for_measurement, reference=TRISOMY_21)
                except:
                    print(f"There is no Trisomu 21 data in for {measurement_method} at this age.")
                    centile_data = []

                ## Store this centile for a given measurement
                centiles.append({"sds": round(z*100)/100, "centile": centile, "data": centile_data})
                
            ## this is the end of the centile_collection for loop
            ## All the centiles for this measurement, sex and reference are added to the measurements list
            measurements.update({measurement_method: centiles})
            
            ## this is the end of the measurement_methods loop
            ## All data for all measurement_methods for this sex are added to the sex_list list

            sex_list.update({sex: measurements})
                
    ## all data can now be tagged by reference_name and added to reference_data
    reference_data={TRISOMY_21: sex_list}
    return reference_data

    """
    # return object structure

    trisomy_21: {
        male: {
            height: [
                {
                    sds: -2.667,
                    centile: 0.4
                    data: [{l: , x: , y: }, ....]
                }
            ],
            weight: [...]
        },
        female {...}
    }
    """
