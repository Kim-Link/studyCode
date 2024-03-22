// 비동기 처리
async function sampleFunc(){
    // time start
    console.time('promise all example');

    // first promise
    const fetchNameList = async ()=> {
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                const result= ['Jack', 'Joe', 'Beck'];
                resolve(result);
            }, 300);
        });
    };

    // second promise
    const fetchFruits = async ()=> {
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                const result  = ['Apple', 'Orange', 'Banana'];
                resolve(result);
            }, 200);
        });
    };

    // third promise
    const fetchTechCompanies = async ()=> {
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                const result = ['Apple', 'Google', 'Amazon'];
                resolve(result);
            }, 400);
        });
    };


    // promise all
    const result = await Promise.all([
        fetchNameList(),
        fetchFruits(),
        fetchTechCompanies(),
    ]);

    // time end
    console.timeEnd('promise all example');

    console.log(result);
}

// execute
sampleFunc();