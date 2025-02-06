
class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def Distance(self, x, y):
        return (self.x - x) ** 2 + (self.y - y) ** 2
def CheckMin(pos):[]


    min = 99999999
    index = 0
    i = 0
    for v in pos:
        if min > v:
           index = i
           min = v
        i += 1
    return index
data = input()
num, current_x, current_y = data.split()
current = Vector2(float(current_x), float(current_y))
positions = []
distances = []
for i in range(int(num)):
    data = input()
    x, y = data.split()
    positions.append(Vector2(float(x), float(y)))
    distances.append(positions[i].Distance(current.x, current.y))
print(CheckMin(distances) + 1)

    

    