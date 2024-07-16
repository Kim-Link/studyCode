import dotenv from 'dotenv';
import jwt from 'jsonwebtoken';
import axios from 'axios';

dotenv.config();

function createJwt(clientId, serviceAccount, privateKey) {
    const currentTime = Math.floor(Date.now() / 1000);
    const payload = {
        iss: clientId,
        sub: serviceAccount,
        iat: currentTime,
        exp: currentTime + 3600
    };
    const headers = {
        alg: "RS256",
        typ: "JWT"
    };

    const token = jwt.sign(
        payload,
        privateKey,
        { algorithm: 'RS256', header: headers }
    );
    console.log("token", token);
    return token;
}

async function requestToken(jwtToken, clientId, clientSecret, scope) {
    const url = 'https://auth.worksmobile.com/oauth2/v2.0/token';
    const headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    };
    const data = new URLSearchParams({
        'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
        'client_id': clientId,
        'client_secret': clientSecret,
        'assertion': jwtToken,
        'scope': scope
    });

    try {
        const response = await axios.post(url, data, { headers });
        return response.data;
    } catch (error) {
        console.error("Error requesting token:", error);
        return null;
    }
}

async function getPostList(tokenResponse, boardId) {
    const accessToken = tokenResponse.access_token;
    const url = `https://www.worksapis.com/v1.0/boards/${boardId}/posts`;

    const headers = {
        'Authorization': `Bearer ${accessToken}`
    };

    try {
        const response = await axios.get(url, { headers });
        if (response.status === 200) {
            const postsData = response.data;
            const posts = postsData.posts;
            console.log(posts);
            return posts;
        } else {
            console.error(`Failed to retrieve posts from board ${boardId}. Status code: ${response.status}`);
            console.error(response.data);
        }
    } catch (error) {
        console.error("Error getting post list:", error);
    }
}

async function getPost(tokenResponse, boardId, postId) {
    const accessToken = tokenResponse.access_token;
    const url = `https://www.worksapis.com/v1.0/boards/${boardId}/posts/${postId}`;

    const headers = {
        'Authorization': `Bearer ${accessToken}`
    };

    try {
        const response = await axios.get(url, { headers });
        if (response.status === 200) {
            const postDetails = response.data;
            return postDetails;
        } else {
            console.error(`Failed to retrieve post. Status code: ${response.status}`);
            console.error(response.data);
            return null;
        }
    } catch (error) {
        console.error("Error getting post:", error);
        return error;
    }
}

export async function handler(event) {
    console.log("Handler event:", event);

    let eventBody = event;
    try {
        if(event.body){
            eventBody = JSON.parse(event.body);
        }
    } catch (error) {
        console.error("Error parsing event body:", error);
        return {
            statusCode: 400,
            body: JSON.stringify({ message: "Invalid JSON in request body" })
        };
    }
    const { board, funcType, postId } = eventBody;

    console.log("Handler event > board, funcType, postId:", board, funcType, postId);
    console.log(typeof(postId));

    const clientId = process.env.CLIENT_ID;
    const clientSecret = process.env.CLIENT_SECRET;
    const serviceAccount = process.env.SERVICE_ACCOUNT;
    const privateKey = `-----BEGIN PRIVATE KEY-----\n${process.env.PRIVATE_KEY}\n-----END PRIVATE KEY-----`;
    const scope = process.env.SCOPE;

    let boardId = process.env.NEWS_BOARD_ID;
    if (board === 'recruit') {
        boardId = process.env.EMPLOY_BOARD_ID;
    }

    const jwtToken = createJwt(clientId, serviceAccount, privateKey);
    const tokenResponse = await requestToken(jwtToken, clientId, clientSecret, scope);
    console.log("tokenResponse:", tokenResponse);

    if (funcType === 'list') {
        console.log("Fetching post list for boardId:", boardId);
        const result = await getPostList(tokenResponse, boardId);
        return {
            statusCode: 200,
            body: JSON.stringify({message :"Lambda function executed successfully", result })
        };
    } else if (funcType === 'post') {
        console.log("Fetching post for postId:", postId);
        const result = await getPost(tokenResponse, boardId, postId);
        return {
            statusCode: 200,
            body: JSON.stringify({message :"Lambda function executed successfully", result })
        };
    } else {
        console.error("Unknown funcType:", funcType);
        return {
            statusCode: 400,
            body: JSON.stringify({message: "Invalid function type"})
        };
    }
}
