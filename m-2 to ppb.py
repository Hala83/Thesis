from scipy.constants import g as gravity
from scipy.constants import Avogadro as avogadro

###########################Comparing Two Criteria for Unit Conversion###################################################

if __name__ == '__main__':
    av = avogadro # 6.02214 * pow(10, 3)
    grav = gravity # 9.8 Newton
    surface_pressure = 101197.336  # in Pa
    multiplication_factor_to_convert_to_molecules_percm2 = 6.022141E19  # Value from Netcdf file
    column_value = 0.0305  * multiplication_factor_to_convert_to_molecules_percm2 # in (molecule/m2)
    air_mass_gram = 28.9647 # constant from : (https://en.wikipedia.org/wiki/Density_of_air)
    air_mass_kg = 0.0289654 # constant from : (https://en.wikipedia.org/wiki/Density_of_air)
    print(av)
    print(grav)
    ##### Unit Conversion of Data from mol/m2 to ppb following TOBIAS criteria ########
    ############ Link (https://search.proquest.com/docview/2117060744 #################
    air_column =  (surface_pressure * avogadro)/(gravity * air_mass_gram)
    new_value = 6.022141E19 * column_value/air_column/1E9
    print("Tobias_Number gram= "+ str(new_value))
    air_column = (surface_pressure * avogadro) / (gravity * air_mass_kg)
    new_value = (6.022141E19 * column_value) / air_column/1E9
    print("Tobias_Number kg = " + str(new_value))
    ##### Unit Conversion of Data from mol/m2 to ppb following Marios criteria #########################
    ############# Link (http://ikee.lib.auth.gr/record/308538/files/GRI-2019-25816.pdf)#################
    value_mario = column_value * 6.022141E19/2.45
    print("Marios_Number = " + str(value_mario))

    value_wrt_correlation = column_value * 0.198516
    print("Value with wrt Correlation = " + str(value_wrt_correlation))
    print("Column Value = " + str(column_value))

    print("Correlation SP5 and SCK  is r = 0.198516")
    print("Correlation SP5 and EPA is r =  0.19744")
    print("Correlation EPA and SCK is r = 0.687883")