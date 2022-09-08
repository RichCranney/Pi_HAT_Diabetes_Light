# Get Dexcom username and password (this should be stored in secret management)
Dexcom_username = 'richardcranney'
Dexcom_password = 'Wycombe!23'

bloodGlucose = [
    [0.0, 3.9, "red"],
    [4.0, 5.5, "orange"],
    [5.6, 10.0, "green"],
    [10.0, 13.9, "pink"],
    [14.0, 99.9, "purple"]
]

deltaRates = [
    [-5, -1, "red", "down"],
    [-0.9, -0.2, "orange", "down"],
    [-0.1, 0.1, "green", "steady"],
    [0.2, 0.9, "orange", "up"],
    [1.0, 5, "red", "up"]
]
