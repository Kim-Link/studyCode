import {MongoClient} from "mongodb";
import dotenv from "dotenv";
// opensearch 연결
import { Client } from '@opensearch-project/opensearch';

dotenv.config();

const MONGO_URI = process.env.MONGO_URI;

// OpenSearch 엔드포인트 및 인증 정보 설정
const openSearchEndpoint = process.env.AWS_OS_NODE;
const openSearchUser = process.env.AWS_OS_USERNAME;
const openSearchPass = process.env.AWS_OS_PASSWORD;

const mongoClient = new MongoClient(MONGO_URI);

const openSearchClient = new Client({
    node: openSearchEndpoint,
    auth: {
        username: openSearchUser,
        password: openSearchPass
    }
});

async function getMongoDocuments() {
    try {
        // MongoDB에 연결
        await mongoClient.connect();
        console.log('Connected to MongoDB');

        // 데이터베이스 및 컬렉션 선택
        const db_29CM = mongoClient.db('29CM_TEST');
        const db_MUSINSA = mongoClient.db('MUSINSA_TEST');
        const db_WCONCEPT = mongoClient.db('WCONCEPT_TEST');
        const collection_29CM = db_29CM.collection('product');
        const collection_MUSINSA = db_MUSINSA.collection('product');
        const collection_WCONCET = db_WCONCEPT.collection('product');

        const mongoDocuments = []

        // 데이터 조회
        const mongoDocuments_MUSINSA = await collection_MUSINSA.find({}).toArray();
        const mongoDocuments_29CM = await collection_29CM.find({}).toArray();
        const mongoDocuments_WCONCEPT = await collection_WCONCET.find({}).toArray();

        mongoDocuments.push(...mongoDocuments_MUSINSA, ...mongoDocuments_29CM, ...mongoDocuments_WCONCEPT)


        // mongoDocuments 에서 uuid, title, brand, modelName, category, subCategory, categoryPath, price, texture, sole, rawColors, color, optionStyle, style, tag, content, s3Url, cutType, originUrl, updatedAt, createdAt 추출
        const entries = mongoDocuments.map((doc) => {
            let index = 'shoes_brand';
            if (doc.luxury){
                index = 'luxury_shoes_brand';
            }

            const result = {
                uuid: doc.uuid,
                title: doc.goodsName,
                brand: doc.brand,
                modelName: doc.modelName,
                category: doc.category,
                subCategory: doc.subCategory,
                categoryPath: doc.categoryPath,
                price: doc.price,
                texture: doc.texture,
                sole: doc.sole,
                rawColors: doc.rawColors,
                color: doc.color,
                optionStyle: doc.optionStyle,
                style: doc.style,
                tag: doc.detail.category,
                content: doc.content,
                s3Url: doc.s3Url,
                cutType: doc.cutType,
                originUrl: doc.linkURL,
                updatedAt: doc.updatedAt,
                createdAt: doc.createdAt,
                index: index
            };

            return result;
        });

        return entries;
    } catch (e) {
        throw new Error(`MongoDB 조회 중 오류가 발생했습니다. 응답 코드: ${e.statusCode}`);
    }
}

async function jsonToBulkData(entries, version) {
    const bulkData = [];

    for (const entry of entries) {

        const upsertLine = {
            index: {
                _index: entry.index + version,
                _id: entry.uuid,
                // op_type: "upsert"
            }
        };
        const docLine = {
            uuid: entry.uuid,
            title: entry.title,
            brand: entry.brand,
            modelName: entry.modelName,
            category: entry.category,
            subCategory: entry.subCategory,
            categoryPath: entry.categoryPath,
            price: entry.price,
            texture: entry.texture,
            sole: entry.sole,
            rawColors: entry.rawColors,
            color: entry.color,
            optionStyle: entry.optionStyle,
            style: entry.style,
            tag: entry.tag,
            content: entry.content,
            s3Url: entry.s3Url,
            cutType: entry.cutType,
            originUrl: entry.originUrl,
            updatedAt: entry.updatedAt,
            createdAt: entry.createdAt
        };

        bulkData.push(upsertLine);
        bulkData.push(docLine);
    }

    return bulkData;
}

async function sendBulkUpsertRequest(bulkData) {
    try {
        console.log('Bulk insert start');
        const response = await openSearchClient.bulk({
            index: 'test_index_v3.1.2',
            body: bulkData
        });

        if (response.statusCode === 200 || response.statusCode === 201) {
            console.log("Bulk insert successful");
        }
    } catch (e) {
        throw new Error(`OpenSearch에 데이터를 업로드하는 중 오류가 발생했습니다. 응답 코드: ${e.statusCode}`);
    }
}

async function main() {
    try {
        console.log('Connect Start')

        const entries = await getMongoDocuments();

        const version = '_test';

        const bulkData = await jsonToBulkData(entries, version);

        const result = await sendBulkUpsertRequest(bulkData);

    } catch (e) {
        console.log(e);
        throw e;
    } finally {
        await mongoClient.close();
        console.log('MongoDB connection closed');
    }
}

main();
