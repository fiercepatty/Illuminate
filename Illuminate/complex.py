

list1 = [2, -1]
list2 = [3, 4]

resultList = []

a = list1[0] * list2[0]
b = list1[0] * list2[1]
c = list1[1] * list2[0]
d = (list1[1] * list2[1]) * -1

resultList.append((a + d, b + c))

print(resultList)
