// locationGenerator.js
// USES NODE.JS!!!!!
// Connor Jones, C22046695, 07/01/24 - 22/02/24 (DD/MM/YY)
const turf = require("@turf/turf");
const fs = require("fs");
const path = require("path");
const {parse} = require("csv-parse/sync");

/* -=-=-= STRUCTURE OF GEOJSON =-=-=-
"features": [
    {
        "type": "Feature",
        "properties": {
                "ADMIN": "Aruba",
                "ISO_A3": "ABW",
                "population": 105845
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                    [                       #NOTE These are lines that construct the geometry of the country (extremely accurate, therefore lengthy)
                        -69.99693762899992,
                        12.577582098000036
                    ], 
                    [...                    
            ]
        }
    },...
additional Features(countries)...]

/ Helpful for checking structure, not much else.
/ don"t bother with actually trying to manually construct the geometrical objects, search for functions
/ that innately can construct them, and or just check them, such as Turf.
*/
const countryLocationData = JSON.parse(fs.readFileSync("./CountriesGeoJSONFile.json", "utf8"));

/* -=-=-= STRUCTURE OF GEOJSON =-=-=-
{"features" :[
    {
        "type": "Feature",
        "geometry": {
        "type": "Point",
        "coordinates":  [ 139.6922,35.6897 ]
    },
    "properties": {
        "city":"Tokyo",
        "city_ascii":"Tokyo",
        "country":"Japan",
        "iso2":"JP",
        "iso3":"JPN",
        "admin_name":"Tōkyō",
        "capital":"primary",
        "population":37732000,
        "id":1392685764
    }
    }, ...
]}

/ Helpful for checking structure, not much else.
/ Contains a list of "Features", which contains data such as "city_ascii", "population" etc.
/ ONLY USE city_ascii, SINCE OTHER FEATURES (admin_name, city etc) CONTAIN UNICODE CHARACTERS NOT JUST ASCII.
*/
const cityLocationData = JSON.parse(fs.readFileSync("./worldcities.geojson", "utf8"));

// get location data from here
const cityGeoJsonLocationData = JSON.parse(fs.readFileSync("./cities.geojson", "utf8"));
const countryWeights = readCountriesCSV("./countries_weights.csv");
const cityWeights = readCitiesCSV("./cities_weights.csv");
function readCitiesCSV(csvFileName) {
    const fileContent = fs.readFileSync(csvFileName, "utf8");
    const records = parse(fileContent, {
        columns: ["city", "population", "weight"],
        skip_empty_lines: true
    });
    return records;
}
function readCountriesCSV(csvFileName) {
    const fileContent = fs.readFileSync(csvFileName, "utf8");
    const records = parse(fileContent, {
        columns: ["country", "population", "weight"],
        skip_empty_lines: true
    });
    return records;
}


// function to generate a weighted random location
function getWeightedRandomLocation() {
    // ~50% of the global population lives in cities
    // if, randomly, "the post is from a city"
    // create a dict of cities:population
    if (Math.random() >= 0.5) {
        let totalWeight = cityWeights.reduce((total, city) => total + Number(city.weight), 0);
        let randomNum = Math.random() * totalWeight;

        // initialising/resetting
        let selectedCity;
        let cityLocation;
        let cityname;

        // do (generate random position) while there is no city location chosen
        do {
            for (const city of cityWeights) {
                randomNum -= Number(city.weight);
                if (randomNum <= 0) {
                    selectedCity = city;
                    break;
                }
            }
            // formatting
            cityname = selectedCity.city.toUpperCase();

            //search for the city from the geoJSON file
            //cityLocation = cityLocationData.features.find(feature => feature.properties.city_ascii.toUpperCase() === cityname);
            cityLocation = cityGeoJsonLocationData.features.find(feature => feature.properties.NAME === cityname);
        } while(!cityLocation || cityLocation === undefined);
        
        // using turf to create the city using the coordinates from the geojson file, then choosing a point in said city
        let turfPolygon = turf.polygon(cityLocation.geometry.coordinates);
        let randomPoint = turf.randomPoint(1, {bbox: turf.bbox(turfPolygon)});
        // these might be backwards lmfao -=-=-=-= LOOK HERE IF PROBLEMS WITH COORDINATES NOT EXISTING =-=-=-=-=-
        let variedLatitude = randomPoint.features[0].geometry.coordinates[0];
        let variedLongitude = randomPoint.features[0].geometry.coordinates[1];

        let countryName = cityLocationData.features.find(feature => feature.properties.city_ascii.toUpperCase() === cityname);

        return {
            name: countryName.properties.country,
            latitude: variedLatitude,
            longitude: variedLongitude
        };
        
    } else {
        let totalWeight = countryWeights.reduce((total, country) => total + Number(country.weight), 0);
        let randomNum = Math.random() * totalWeight;

        // initialising
        let selectedCountry;
        let countryLocation;
        let countryname;

        // do (generate random position) while there is no country location chosen
        do{
            for (const country of countryWeights) {
                randomNum -= Number(country.weight);
                if (randomNum <= 0) {
                    selectedCountry = country;
                    break;
                }
            }

            countryname = selectedCountry.country;
            countryLocation = countryLocationData.features.find(feature => feature.properties.ADMIN === countryname);    
        } while(!countryLocation || countryLocation === undefined);

        let variedLatitude;
        let variedLongitude;

        // handling cases where the object is not polygon, or a multipolygon
        if (countryLocation.geometry.type === 'Polygon') {
            // generates the polygon and gets a random position within that polygon (using turf)
            let turfPolygon = turf.polygon(countryLocation.geometry.coordinates);
            let randomPoint = turf.randomPoint(1, {bbox: turf.bbox(turfPolygon)});
            [variedLongitude, variedLatitude] = randomPoint.features[0].geometry.coordinates;
        } else if (countryLocation.geometry.type === 'MultiPolygon') { 
            // choose a random polygon from the MultiPolygon (set of polygons)
            let polygons = countryLocation.geometry.coordinates;
            let randomPolygonIndex = Math.floor(Math.random() * polygons.length); //generates a random index for all polygons based on the length of the polygon """list"""
            // generate randomly chosen polygon, get a random point (using turf)
            let randomPolygon = turf.polygon(polygons[randomPolygonIndex]);
            let randomPoint = turf.randomPoint(1, {bbox: turf.bbox(randomPolygon)});
            [variedLongitude, variedLatitude] = randomPoint.features[0].geometry.coordinates;
        }

        return {
            name: countryname,
            latitude: variedLatitude,
            longitude: variedLongitude,
        };
    }
}


// in case this program is being used as a module, it would perform the getWeightedRandomLocation
module.exports = getWeightedRandomLocation;
    

// Uncomment the following lines to test the getWeightedRandomLocation function (ctrl + /)
// starttime = performance.now();

// no_tests = 10;
// //let outputarr = new Array(no_tests).fill(0);

// for(let i=0; i < no_tests; i++){
//     indiv_addition = getWeightedRandomLocation();
//     //outputarr[i] = indiv_addition;
//     console.log(indiv_addition);
// };

// endtime = performance.now();
// console.log(no_tests + " runs of getWeightedRandomLocation took " + (endtime-starttime)/1000 + " seconds");