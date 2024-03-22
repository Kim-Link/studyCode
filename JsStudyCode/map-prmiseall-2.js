// 동기 처리
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
    const names = await fetchNameList();
    const fruits = await fetchFruits();
    const companies = await fetchTechCompanies();
    const result = [ names, fruits, companies]

    // time end
    console.timeEnd('promise all example');

    console.log(result);
}

// execute
sampleFunc();