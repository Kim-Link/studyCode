# 사분면 관련 좌표를 넣으면 사분면중 어느 사분면인지 알려주는 코드

def solution(dot):
    quad = [(3,2),(4,1)]
    return quad[dot[0]>0][dot[1]>0]

print(solution([-1,1]))
