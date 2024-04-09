// map + promise.all 을 사용했을때
async function sampleFunc(){
    // time start
    console.time('map example');

    // 비동기 작업을 수행하는 함수 예시
    function asyncTask(item) {
        return new Promise((resolve, reject) => {
            // 비동기 작업 수행 (여기서는 간단히 setTimeout으로 대체)
            setTimeout(() => {
                resolve(item * 2); // 작업 완료 후 결과 반환
            }, item * 100); // 시간 대기
        });
    }

// 비동기 작업을 처리할 데이터 배열
    const data = [1, 2, 3, 4, 5];

// 각 항목에 대해 asyncTask 함수를 적용하여 비동기 작업을 수행하고 결과를 모읍니다.
    const promises = data.map(asyncTask);

    const result =await Promise.all(promises)


    // time end
    console.timeEnd('map example');

    console.log(result);
}

// execute
sampleFunc();