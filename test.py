def hanoi(n, source, target, auxiliary):
    if n == 1:
        print("Переместить диск 1 из башни", source, "на башню", target)
        return
    hanoi(n - 1, source, auxiliary, target)
    print("Переместить диск", n, "из башни", source, "на башню", target)
    hanoi(n - 1, auxiliary, target, source)


n = 1
source = 1
target = 3
auxiliary = 2

print("Для перемещения всех дисков из башни", source, "на башню", target, "используем:")
hanoi(n, source, target, auxiliary)
