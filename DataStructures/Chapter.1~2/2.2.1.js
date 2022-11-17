
const numbers = new Array(1,2,3,4,5)

console.log(numbers);
// 결과 : [ 1, 2, 3, 4, 5 ]

const numbers2 = new Array(10)

console.log(numbers2);
// 결과 : [ <10 empty items> ]

const numbers3 = 3;
const arr = [7,4,1776];
console.log(Array.isArray(numbers3))  //false
console.log(Array.isArray(arr))  // true
