// 얕은 복사 예시
// 일반적인 배열 할당시 실제로는 할당된 배열의 레퍼런스(주소)를 할당하는 것이다.
// 따라서 원래 배열을 바꾸면 할당된 배열도 바뀌게 된다.

const nums = [];
for(let i = 0; i < 10 ; i +=1){
    nums[i] = i + 1;
}

const samenums = nums

nums[0] = 400

console.log('nums[0] :',nums[0]);
console.log("samenums[0] :",samenums[0]);

// 깊은 복사 예시

function copy(arr1, arr2) {
    for(let i = 0; i < arr1.length ; i +=1){
        arr2[i] = arr1[i]
    }
}

const samenums2 = []
copy(nums, samenums2);
nums[0] = 500;

console.log('nums[0] :',nums[0]);
console.log("samenums2[0] :",samenums2[0]);
