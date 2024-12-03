import AWS from 'aws-sdk';
import dotenv from 'dotenv';
import { Client } from '@opensearch-project/opensearch';

dotenv.config();

// AWS 계정 정보 설정
const awsAccessKey = process.env.AWS_ACCESS_KEY_ID;
const awsSecretKey = process.env.AWS_SECRET_ACCESS_KEY;
const regionName = process.env.AWS_REGION;
const bucketName = process.env.AWS_S3_BUCKET_NAME;
const jsonFileKey = process.env.AWS_S3_PATH;

// OpenSearch 엔드포인트 및 인증 정보 설정
const openSearchEndpoint = process.env.AWS_OS_NODE;
const openSearchUser = process.env.AWS_OS_USERNAME;
const openSearchPass = process.env.AWS_OS_PASSWORD;
const openSearchAlias = process.env.AWS_INDEX_ALIAS;

// S3 클라이언트 생성
const s3 = new AWS.S3({
    accessKeyId: awsAccessKey,
    secretAccessKey: awsSecretKey,
    region: regionName
});

// openSearch 클라이언트 생성
const openSearchClient = new Client({
    node: openSearchEndpoint,
    auth: {
        username: openSearchUser,
        password: openSearchPass
    }
});

async function getIndexNames() {
    const { body } = await openSearchClient.cat.aliases({
        name: openSearchAlias,
        format: 'json',
    });

    // body 에서 index 이름 추출 해서 shoes_brand, luxury_shoes_brand index 추출
    const indexNames = body.map((index) => {
        return index.index;
    });

    const setIndexNames = new Set(indexNames);
    const arrayIndexNames = Array.from(setIndexNames);

    const luxuryClothesBrandIndex = arrayIndexNames.findIndex((index) => index.includes('luxury_clothes_brand'));
    const luxuryShoesBrandIndex = arrayIndexNames.findIndex((index) => index.includes('luxury_shoes_brand'));
    const shoesBrandIndex = arrayIndexNames.findIndex((index) => !index.includes('luxury'));

    const result = {
        luxuryClothesBrandIndex: arrayIndexNames[luxuryClothesBrandIndex],
        luxuryShoesBrandIndex: arrayIndexNames[luxuryShoesBrandIndex],
        shoesBrandIndex: arrayIndexNames[shoesBrandIndex]
    };

    return result
}

// data 폼 생성
function jsonToBulkData(entries, indexName) {
    const bulkData = [];

    console.log("index name >> ", indexName);

    for (const entry of entries) {
        const upsertLine = {
            index: {
                _index: indexName,
                _id: entry.uuid,
                op_type: "upsert"  // Specify upsert operation
            }
        };
        const docLine = entry;  // Use the entry directly, as it will be the document for upsert
        bulkData.push(JSON.stringify(upsertLine));
        bulkData.push(JSON.stringify(docLine));
    }

    return bulkData.join("\n") + "\n";
}

// 인덱스 설정 : 파일 이름과 version을 가지고 index name 설정
async function extractIndexName(filename, indexNames) {
    // 정규표현식을 사용하여 'luxury_clothes_brand', 'luxury_shoes_brand', 'shoes_brand'를 추출
    const match = filename.match(/_(luxury_clothes|luxury_shoes|shoes)_brand(_[a-zA-Z0-9._ ]+)?\.json/);
    let result;

    if(match[1] === 'luxury_clothes') {
        result = indexNames.luxuryClothesBrandIndex;
    } else if (match[1] === 'luxury_shoes') {
        result = indexNames.luxuryShoesBrandIndex;
    } else if (match[1] === 'shoes') {
        result = indexNames.shoesBrandIndex;
    }

    // 매치가 존재하면 인덱스를 반환, 아니면 에러를 반환
    if (match) {
        return result;
    } else {
        throw new Error(`${filename}에서 인덱스를 찾을 수 없습니다.`);
    }
}

// POST _bulk 요청 : upsert 요청 코드
async function sendBulkUpsertRequest(bulkData) {
    try {
        console.log('Bulk insert start');
        const response = await openSearchClient.bulk({
            body: bulkData
        });

        if (response.statusCode === 200 || response.statusCode === 201) {
            console.log("Bulk insert successful");
        }
    } catch (e) {
        throw new Error(`OpenSearch에 데이터를 업로드하는 중 오류가 발생했습니다. 응답 코드: ${e.statusCode}`);
    }
}

// JSON을 Bulk API 데이터로 변환하여 OpenSearch에 삽입 또는 업데이트하는 메인 함수
async function main() {
    try {
        // S3에서 JSON 파일 읽기
        const response = await s3.listObjectsV2({ Bucket: bucketName }).promise();

        // 파일 목록 추출
        const fileList = [];
        if (response.Contents) {
            for (const obj of response.Contents) {
                if (obj.Key.startsWith('upsert/') && obj.Key !== 'upsert/') {
                    fileList.push(obj.Key);
                }
            }
        }

        console.log('File List:', fileList);

        const indexNames = await getIndexNames();

        for (const targetFileName of fileList) {
            console.log('File Name:', targetFileName);
            const fileResponse = await s3.getObject({ Bucket: bucketName, Key: targetFileName }).promise();
            console.log("check response");
            const jsonContent = fileResponse.Body.toString('utf-8');
            console.log("check json_content");
            const jsonData = JSON.parse(jsonContent);
            console.log("check json_data");

            // 배치 크기로 조정
            const batchSize = 1000;
            for (let i = 0; i < jsonData.length; i += batchSize) {
                const batchEntries = jsonData.slice(i, i + batchSize);

                const indexName = await extractIndexName(targetFileName, indexNames);
                // bulk data 형식으로 변환
                const bulkData = jsonToBulkData(batchEntries, indexName);

                await sendBulkUpsertRequest(bulkData);
                console.log(`Bulk insert response for batch ${i}:`);
            }
        }
    } catch (error) {
        console.error(`Error: ${error}`);
    }
}

main();
