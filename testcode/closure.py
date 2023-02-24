# 클로저(closure)
# 함수가 선언(정의)될 당시의 환경을 기억 했다가, 차후 호출될때 기억한 환경을 이용하는 함수
# 아래 함수에서는 new_fn2, new_fn3가 클로저 함수 라고 볼수 있음


def make_double(base_number):
    i=0
    new_fn1 = lambda number : base_number + number ** 2
    
    def new_fn2(number1, number2):
        print("new_fn2>> base_number, number1, number2 : ",base_number, number1, number2)
        return base_number + number1 ** 2
    
    def new_fn3(number3):
        print("new_fn3",base_number, number3)
        return base_number + number3 ** 2

    return new_fn2


return_fn = make_double(10)

print(return_fn(number2=5,number1=4))

# 파이썬의 클로저에서 변수가 들어가는게 제대로 이해가 되지 않아서 테스트 해봄, 결론은 클로저에서 return되는 함수에 따라 인자를 순서대로 넣을수 있음. 순서대로 넣고싶지 않으면 당연하게도 변수 이름을 지정하여 넣으면 됨

