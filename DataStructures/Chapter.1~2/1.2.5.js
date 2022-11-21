function curve(arr,amount) {
    for(let i = 0; i < arr.length; i+= 1){
        arr[i] += amount;
    }
};
const grade = [77,73,74,81,90];

curve(grade,5)
console.log(grade)