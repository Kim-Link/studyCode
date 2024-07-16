const jsonString = `{
  "posts":[
    {
      "boardId": "4000000001203670002",
      "postId": "4070000000142597171",
      "title": "[전자신문_2024.6.26] 크리스틴컴퍼니 스케일업 팁스 선정",
      "readCount": 40,
      "commentCount": 1,
      "fileCount": 0,
      "createdTime": "2024-06-26T16:33:52+09:00",
      "modifiedTime": "2024-06-26T16:33:52+09:00",
      "userId": "bb9fa9d3-5ca7-420b-1cc9-0333e9becf09",
      "userName": "이정섭",
      "mustReadPeriod": {
        "startDate": null,
        "endDate": null
      },
      "isMustRead": false,
      "resourceLocation": null,
      "isUnread": true
    }
  ],
  "responseMetaData": {
    "nextCursor": "H4sIAAAAAAAAAKtWKkpNzywucUksSVWyMjSzsLQwNDI0NzIxtagFACDintYcAAAA"
  }
}`;

const parsedData = JSON.parse(jsonString, (key, value) => {
    if (typeof value === 'string' && /^[0-9]+$/.test(value)) {
        return value;
    }
    return value;
});

// 이제 정확한 값으로 접근 가능
const boardId = parsedData.posts[0].boardId;
const postId = parsedData.posts[0].postId;

console.log('boardId:', boardId); // "4000000001203670002"
console.log('postId:', postId);   // "4070000000142597171"
console.log(parsedData);
