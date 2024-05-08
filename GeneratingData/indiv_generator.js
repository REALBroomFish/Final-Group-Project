// indiv_generator.js
// USES NODE.JS!!!!!
// Connor Jones, C22046695, 01/02/24 (DD/MM/YY)
const fs = require("fs");
const {spawn} = require("child_process");
const {performance} = require("perf_hooks");
const path = require("path");
const list_of_valid_words = ["phone", "smartphone", "mobile phone", "iphone", "samsung phone", 
                             "apple phone", "iphone15", "huawei", "huawei phone", "samsung galaxy",
                             "huawaiP", "huawei mate"]
const locationGenerator = require("./locationGenerator.js");
const MastodonData = require("./MastodonAPILIB.js");

//#region generating details on an individual.
//NOTE: Details are not related to any specific individual, and are randomly generated on a case by case basis

async function person_generator(num_people) {
    return new Promise((resolve, reject) => {
        const pythonProcess = spawn("python", ["UpdatedFaker.py", JSON.stringify(num_people)]);

        let result = "";
        pythonProcess.stdout.on("data", (data) => {
            result += data.toString();
        });

        pythonProcess.stderr.on("data", (data) => {
            console.error(`Python stderr: ${data}`);
        });

        pythonProcess.on('close', (code) => {
            if (code !== 0) {
                reject(new Error(`Python process exited with code ${code}`));
            } else {
                resolve(result);
            }
        });
    });
}

//#endregion

//#region sentiment analysis python integration into the js environment
async function analyseSentiment(posts) {
    return new Promise((resolve, reject) => {
        const pythonProcess = spawn("python", ["SentimentAnalysis.py"]);

        let result = "";
        pythonProcess.stdout.on("data", (data) => {
            result += data.toString();
        });

        pythonProcess.stderr.on("data", (data) => {
            console.error(`Python stderr: ${data}`);
        });

        pythonProcess.on('error', (error) => {
            console.error('Error spawning Python process:', error);
            process.exit()
        });

        pythonProcess.on('close', (code) => {
            if (code !== 0) {
                console.error(`Python process exited with code ${code}`);
                process.exit()
            } else {
                resolve(JSON.parse(result)); 
            }
        });

        try {
            const inputJSON = JSON.stringify({ posts: posts });
            pythonProcess.stdin.write(inputJSON);
            pythonProcess.stdin.end();
        } catch (error) {
            console.error('Error writing to stdin of the Python process:', error);
            process.exit();
        }
    });
}


async function createSetOfRandomPeople(numberofpeople, queries) {
    let posts = [];
    let people = [];

    for (let query in queries) {
        if (!(list_of_valid_words.includes(query.replace(/_/g, " ").toLowerCase()))) {
            console.log(`Query not permitted: ${query}`);
            process.exit();
        }
    }

    let remainingPeople = numberofpeople;
    let iterations = Math.min(remainingPeople, Math.ceil(remainingPeople/40));
    for (let i = 0; i < iterations; i++) {
        let batchSize = Math.min(remainingPeople, 40);
        let set_of_posts = await MastodonData(queries, batchSize);
        posts.push(...set_of_posts.map(post => post.content));
        remainingPeople -= batchSize;
    }

    let sentiments = await analyseSentiment(posts);

    let people_data = JSON.parse(await person_generator(numberofpeople));

    for (let i = 0; i < numberofpeople; i++) {
        let person = [locationGenerator(), ...people_data[i], sentiments[i]];
        people.push(person);
    }
    return people;
}


function main() {
    console.log("Running as the main module");

    //#region bits to change if more queries are wanted
    const numberofpeople = 250000; 
    const queries = {"samsung phone": 0.33, "iphone": 0.33, "huawei": 0.34};
    //#endregion


    // Execute a function from your module
    createSetOfRandomPeople(numberofpeople, queries).then(people => {
        const filename = 'output_people_more.csv';  
        const header = "latitude,longitude,brand,sentiment,date,country,interests\n";
        let data = people.map(person => {
            const latitude = person[0].latitude;
            const longitude = person[0].longitude;
            const country = person[0].name;
            try{
                person[4].compound;
            } catch {
                console.log(person[4]);
            }
            const sentiment = person[4].compound;
            const interests = `"[${person[3].join(', ')}]"`;
            const brands = ["samsung", "apple", "huawei"];
            const brand = brands[Math.floor(Math.random() * brands.length)];
            const date = `${Math.floor(Math.random() * 24 + 2000)}`; 
            return `${latitude},${longitude},${brand},${sentiment},${date},${country},${interests}`;
        }).join("\n");
    
        // Write the data to a file
        fs.writeFile(filename, header + data, 'utf8', (err) => {
            if (err) {
                console.error('An error occurred while writing CSV to File.', err);
            } else {
                console.log('CSV file has been saved.');
                console.log(__dirname + "/output_people.csv")
            }
        });
    }).catch(err => {
        console.error("Error occurred:", err);
    });
    
}

// Check if this module is the main module being run
if (require.main === module) {
    main();
}
