// promise 없이 map으로 실행이 되요~~!!!
async function sampleFunc(){
    // time start
    console.time('map example');

    // 비동기 작업을 수행하는 함수 예시
    function asyncTask(item) {
        // 비동기 작업 수행 (여기서는 간단히 setTimeout으로 대체)
        setTimeout(() => {
            console.log('짜란~ : ',item)
        }, item * 1000);// 시간 대기
        return item * 2
    }

// 비동기 작업을 처리할 데이터 배열
    const data = [1, 2, 3, 4, 5];

// 각 항목에 대해 asyncTask 함수를 적용하여 비동기 작업을 수행하고 결과를 모읍니다.
    const result = data.map(asyncTask);

    // time end
    console.timeEnd('map example');

    console.log(result);
}

// execute
sampleFunc();