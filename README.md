# mindat-location

This small scripts queries the [Mindat.org](https://www.mindat.org/) database for the location of a mineral.
It uses a csv file as input, where it will retrieve the location from and query the mindat API to search for the location.

## Running the script
The script has been written as a Command Line Tool which can be triggered from the command line.
Another way to run the script is to run it from an IDE like [PyCharm](https://www.jetbrains.com/pycharm/).
In the run configuration of PyCharm, you can specify the arguments to pass to the script.
Please let us know if require you have any additional run options.

## Command line arguments
There are several argument for the script, which can be found by running the script with the `--help` argument.
The required arguments are:
- `--input` or `-i`: The path to the input file
- `--location_column' or `-l`: The index of the column in the input file which contains the location (index starts at 0)
- `--token` or `-t`: The token to use for the Mindat API. This token can be found on your [Mindat.org](https://www.mindat.org/) profile page (My Home Page). 
Then go to `Edit My Page` and scroll all the way to the bottom. The API Key should be there, otherwise you need to request one, see [here](https://www.mindat.org/a/how_to_get_my_mindat_api_key).

The optional arguments are:
- `--output` or `-o`: The path to the output file. If not specified, the output will be called `result.csv`.
- `--country_column` or `-c`: The index of the column in the input file which contains the country (index starts at 0). If not specified, the country will not be used in the API call.
- `--id_column` or `-id`: The index of the column in the input file which contains the id of the record (index starts at 0). If not specified, we will assume that the first column (0) in the input file contains the id.

## Input file
There are few requirements for the input file:
- The id column, this is necessary so that we can connect the record in the result to the record in the input file.
- The location column, this is the column which contains the location of the record. This column will be used to query the Mindat API.

## The output file
The output file will be a csv file, which contains:
- `id` From the input file
- `location` From the input file, this is the location string that is used for the API call
- `mindat_id` The id of the location in the Mindat database
- `mindat_text` The text of the location in the Mindat database
- `mindat_longitude` The longitude of the location in the Mindat database
- `mindat_latitude` The latitude of the location in the Mindat database

## Log file
Logs are both written to the console and to a log file (`log.log`).
The log file contains the same information as the console.
It can be helpful when running larger runs.

## Example
In this directory there is an example input file called `example_input.csv`. 
This contains an example of how the input file can look like.
The result of this example is the file `result.csv` which contains the results.
The result can be reproduced by running the following command:
```python main.py -i example_input.csv -l 1 -t <your token>```

## Limitations
### Not all information of the location is indexed
Compared to the Mindat frontend the API contains less information and might not be able to find your location.
For example:
- The API will not find searches on name which match to Other/historical names or Names in local languages.
- The API will not find searches on names which can only be found in "Other Places Search".

To be able to find the name, the name or part of the name needs to be in the "txt" part of the location.
For example:
A search on `Fassatal` will not result in a match through the API as it is not part of the txt of the location: `Fassa Valley, Trento Province (Trentino), Trentino-Alto Adige (Trentino-South Tyrol), Italy`.
However, if a user uses the frontend `Fassatal` will result in a match as it is part of the "Other/historical names" of the location.

### No confidence score in API
There is no confidence score in the API, so we cannot determine if the location is correct or not.
In the script we always use the first result of the API call, which might not be the correct one.

### No uncertainty in the location
The Mindat data doesn't include the uncertainty of the location.
This means that based on the coordinate it is unclear if the certainty is 1 meter or 1000 meters (or more).
When making distribution maps this might be important to know, as centroids (of countries/regions) will be over-represented.

## Help Mindat
The limitations described above can not be solved by this script but require changes in Mindat.
Mindat relies almost entirely on donations, so if you want to help Mindat, please consider donating to them.
This can be done through this site [https://www.mindat.org/donate.php](https://www.mindat.org/donate.php).
This will give them the opportunity to improve their API and website.

## Issues / Improvements /Feature requests
If you have any issues, improvements or feature requests, please create an issue on this repository.
This repository is a site project and we can therefore not make commitments on when we will implement your request.
However, we will try to implement as many requests as possible and respond to any questions.
