const Mastodon = require("mastodon-api");
let globaloffset = 0;
const M = new Mastodon({
    // kept blank for obvious reasons
    client_key: "",
    client_secret: "",
    access_token: "",
    timeout_ms: 60 * 1000,
    api_url: 'https://mastodon.social/api/v2/'
});

async function APIget(query, num_operations) {
    let collectedData = [];
    while (num_operations > 0) {
        // either the ""current total number of operations"" or 40
        let currentLimit = Math.min(num_operations, 40); 
        const params = {
            limit: currentLimit.toString(),
            q: query,
            offset: globaloffset.toString()
        };
        try {
            const data = await mastodonGet("search", params);
            if (data && data.statuses) {
                collectedData.push(...data.statuses);
                // break if fewer items are returned than requested
                if (data.statuses.length < currentLimit) {
                    break; 
                }
            } else {
                console.log("No posts found or data is in unexpected format.");
                break;
            }
            globaloffset += currentLimit;
        } catch (error) {
            console.error("Error fetching data:", error);
            break;
        }
        num_operations -= currentLimit;
    };

    return collectedData;
};

function mastodonGet(path, params) {
    return new Promise((resolve, reject) => {
        M.get(path, params, (error, data) => {
            if (error) {
                reject(error);
            } else {
                resolve(data);
            }
        });
    });
};

module.exports = APIget;
