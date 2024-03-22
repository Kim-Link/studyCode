function test1() {
    let arr = [2, 3, 5, 7]

    const result = arr.map(function(element, index, array){
        console.log('====시작====');
        console.log(element);
        console.log(index);
        console.log(array);
        console.log(this + 2);
        console.log('==== 끝 ====');
        return element+1;
    }, 80);

    console.log('input arr: ', arr)
    console.log('output arr: ', result)
}

function test2() {
    let arr = [2, 3, 5, 7]

    const result = arr.map(function(element){
        return element+1;
    }, 80);
    console.log('input arr: ', arr)
    console.log('output arr: ', result)
}

test2();